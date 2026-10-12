"""SkillLogger editor. Install PySide6, then run: python config_tool.py."""
import copy
import json
import os
import sys
import tempfile
from pathlib import Path


def default_config():
    return {
        'config_version': '2.0',
        'device': {'device_id': 'SKILLLOGGER-0001'},
        'channels': [{
            'channel_id': 'CAN1', 'enabled': True, 'mode': 'classic_can',
            'nominal_bitrate_bps': 500000, 'data_bitrate_bps': None,
            'filters': {'mode': 'all', 'combine': 'or', 'rules': []},
            'triggers': {'start': {'type': 'power_on'}, 'stop': {'type': 'none'},
                         'rearm_after_stop': False},
        }],
        'logging': {'formats': ['asc', 'mf4'], 'file_split_size_bytes': 104857600,
                    'file_split_time_seconds': 1800,
                    'split_policy': 'first_limit_reached', 'on_sd_full': 'stop',
                    'on_write_error': 'stop', 'overwrite_existing': False},
    }


def require(ok, message):
    if not ok:
        raise ValueError(message)


def keys(obj, expected, label):
    require(isinstance(obj, dict) and set(obj) == set(expected.split()),
            f'{label}: expected fields: {expected}')


def number(value, low, high, label):
    require(type(value) is int and low <= value <= high,
            f'{label}: enter an integer from {low} to {high}')


def boolean(value, label):
    require(type(value) is bool, f'{label}: expected true or false')


def can_id(value, extended):
    require(isinstance(value, str) and value.lower().startswith('0x') and len(value) > 2
            and all(c in '0123456789abcdefABCDEF' for c in value[2:]),
            'Use hexadecimal identifiers or masks, for example 0x123')
    result = int(value, 16)
    require(result <= (0x1FFFFFFF if extended else 0x7FF), 'Identifier/mask exceeds selected ID width')
    return result


def validate_rule(rule):
    require(isinstance(rule, dict), 'Filter must be an object')
    kind = rule.get('type')
    require(kind in ('id_list', 'id_range', 'id_mask'), 'Invalid filter type')
    extra = {'id_list': 'ids', 'id_range': 'id_start id_end', 'id_mask': 'match_id mask'}[kind]
    keys(rule, 'filter_id enabled type extended_id ' + extra, 'Filter')
    require(isinstance(rule['filter_id'], str) and 1 <= len(rule['filter_id'].strip()) <= 64,
            'Filter name must have 1–64 characters')
    boolean(rule['enabled'], 'Filter enabled')
    boolean(rule['extended_id'], 'Extended ID')
    ext = rule['extended_id']
    if kind == 'id_list':
        require(isinstance(rule['ids'], list) and 1 <= len(rule['ids']) <= 256, 'Enter 1–256 IDs')
        values = [can_id(v, ext) for v in rule['ids']]
        require(len(set(values)) == len(values), 'Duplicate IDs in list')
    elif kind == 'id_range':
        require(can_id(rule['id_start'], ext) <= can_id(rule['id_end'], ext), 'Range start exceeds end')
    else:
        can_id(rule['match_id'], ext)
        can_id(rule['mask'], ext)


def validate_config(data):
    keys(data, 'config_version device channels logging', 'Configuration')
    require(data['config_version'] == '2.0', 'Only schema version 2.0 is supported')
    keys(data['device'], 'device_id', 'Device')
    name = data['device']['device_id']
    require(isinstance(name, str) and 1 <= len(name.strip()) <= 64, 'Device ID must have 1–64 characters')
    require(isinstance(data['channels'], list) and len(data['channels']) == 1, 'Exactly one physical channel required')
    ch = data['channels'][0]
    keys(ch, 'channel_id enabled mode nominal_bitrate_bps data_bitrate_bps filters triggers', 'Channel')
    require(ch['channel_id'] == 'CAN1', 'Physical channel must be CAN1')
    boolean(ch['enabled'], 'Channel enabled')
    require(ch['mode'] in ('classic_can', 'can_fd'), 'Invalid CAN mode')
    number(ch['nominal_bitrate_bps'], 10000, 1000000, 'Nominal bitrate')
    if ch['mode'] == 'classic_can':
        require(ch['data_bitrate_bps'] is None, 'Classical CAN data bitrate must be null')
    else:
        number(ch['data_bitrate_bps'], ch['nominal_bitrate_bps'], 8000000, 'Data bitrate')
    filters = ch['filters']
    keys(filters, 'mode combine rules', 'Filters')
    require(filters['mode'] in ('all', 'matching') and filters['combine'] == 'or', 'Invalid filter mode/combination')
    require(isinstance(filters['rules'], list) and len(filters['rules']) <= 64, 'Maximum 64 filters')
    names = set()
    for rule in filters['rules']:
        validate_rule(rule)
        require(rule['filter_id'] not in names, 'Duplicate filter name')
        names.add(rule['filter_id'])
    require(filters['mode'] != 'matching' or any(r['enabled'] for r in filters['rules']),
            'Matching mode needs at least one enabled filter')
    triggers = ch['triggers']
    keys(triggers, 'start stop rearm_after_stop', 'Triggers')
    boolean(triggers['rearm_after_stop'], 'Rearm')
    for side, allowed in [('start', ('power_on', 'can_id_match')), ('stop', ('none', 'can_id_match', 'duration'))]:
        trigger = triggers[side]
        require(isinstance(trigger, dict) and trigger.get('type') in allowed, f'Invalid {side} trigger')
        kind = trigger['type']
        keys(trigger, 'type can_id extended_id' if kind == 'can_id_match' else
             'type seconds' if kind == 'duration' else 'type', side)
        if kind == 'can_id_match':
            boolean(trigger['extended_id'], 'Trigger ID format')
            can_id(trigger['can_id'], trigger['extended_id'])
        if kind == 'duration':
            number(trigger['seconds'], 1, 604800, 'Recording duration')
    start, stop = triggers['start'], triggers['stop']
    require(not triggers['rearm_after_stop'] or (start['type'] == 'can_id_match' and stop['type'] != 'none'),
            'Rearm requires ID start and a configured stop')
    if start['type'] == stop['type'] == 'can_id_match':
        require((can_id(start['can_id'], start['extended_id']), start['extended_id']) !=
                (can_id(stop['can_id'], stop['extended_id']), stop['extended_id']), 'Start and stop IDs must differ')
    log = data['logging']
    keys(log, 'formats file_split_size_bytes file_split_time_seconds split_policy on_sd_full on_write_error overwrite_existing', 'Logging')
    formats = log['formats']
    require(isinstance(formats, list) and 1 <= len(formats) <= 2 and
            all(isinstance(f, str) and f in ('asc', 'mf4') for f in formats), 'Select ASC and/or MF4')
    require(len(set(formats)) == len(formats), 'Duplicate output format')
    number(log['file_split_size_bytes'], 1048576, 2146435072, 'File size limit')
    number(log['file_split_time_seconds'], 0, 604800, 'File time limit')
    require(log['split_policy'] == 'first_limit_reached', 'Invalid split policy')
    require(log['on_sd_full'] == log['on_write_error'] == 'stop', 'Storage errors must stop logging')
    require(log['overwrite_existing'] is False, 'Existing logs must not be overwritten')
    return data


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def load_config(path):
    require(Path(path).stat().st_size <= 1048576, 'Configuration exceeds 1 MiB')
    with open(path, encoding='utf-8-sig') as handle:
        return validate_config(json.load(handle, object_pairs_hook=unique_keys))


def save_config(path, data):
    validate_config(data)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=Path(path).parent,
                                         prefix='.skilllogger-', suffix='.tmp', delete=False) as handle:
            temporary = handle.name
            json.dump(data, handle, indent=2, allow_nan=False)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def main():
    from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QFormLayout, QLineEdit, QComboBox, QCheckBox, QSpinBox, QPushButton, QTabWidget,
        QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QDialog,
        QDialogButtonBox, QMessageBox, QFileDialog, QPlainTextEdit, QLabel, QToolBar)
    from PySide6.QtGui import QAction

    def combo(items):
        w = QComboBox()
        for label, value in items:
            w.addItem(label, value)
        return w

    def select(widget, value):
        widget.setCurrentIndex(widget.findData(value))

    def spin(low, high, suffix=''):
        w = QSpinBox()
        w.setRange(low, high)
        w.setSuffix(suffix)
        return w

    def note(text):
        w = QLabel(text)
        w.setWordWrap(True)
        return w

    class FilterDialog(QDialog):
        def __init__(self, parent, rule):
            super().__init__(parent)
            self.setWindowTitle('Filter rule')
            self.resize(500, 320)
            form = QFormLayout(self)
            self.name = QLineEdit(rule['filter_id'])
            self.enabled = QCheckBox('Enabled')
            self.enabled.setChecked(rule['enabled'])
            self.ext = QCheckBox('Extended (29-bit) identifier')
            self.ext.setChecked(rule['extended_id'])
            self.kind = combo([('ID list', 'id_list'), ('ID range', 'id_range'), ('ID mask', 'id_mask')])
            select(self.kind, rule['type'])
            self.first, self.second = QLineEdit(), QLineEdit()
            self.label1, self.label2 = QLabel(), QLabel()
            for label, w in [('Name', self.name), ('', self.enabled), ('', self.ext), ('Type', self.kind),
                             (self.label1, self.first), (self.label2, self.second)]:
                form.addRow(label, w)
            form.addRow(note('Use 0x-prefixed IDs. Mask: (ID & mask) == (match ID & mask). A zero mask accepts every ID of the selected identifier format.'))
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(self.check)
            buttons.rejected.connect(self.reject)
            form.addRow(buttons)
            self.kind.currentIndexChanged.connect(self.update_fields)
            self.update_fields()
            if rule['type'] == 'id_list':
                self.first.setText(', '.join(rule['ids']))
            else:
                self.first.setText(rule.get('id_start', rule.get('match_id', '')))
                self.second.setText(rule.get('id_end', rule.get('mask', '')))

        def update_fields(self):
            kind = self.kind.currentData()
            self.label1.setText({'id_list': 'IDs (comma separated)', 'id_range': 'First ID', 'id_mask': 'Match ID'}[kind])
            self.label2.setText('Last ID' if kind == 'id_range' else 'Mask')
            self.second.setVisible(kind != 'id_list')
            self.label2.setVisible(kind != 'id_list')

        def rule(self):
            kind = self.kind.currentData()
            result = dict(filter_id=self.name.text().strip(), enabled=self.enabled.isChecked(),
                          type=kind, extended_id=self.ext.isChecked())
            a, b = self.first.text().strip(), self.second.text().strip()
            if kind == 'id_list':
                result['ids'] = [v.strip() for v in a.split(',')]
            elif kind == 'id_range':
                result.update(id_start=a, id_end=b)
            else:
                result.update(match_id=a, mask=b)
            return result

        def check(self):
            try:
                validate_rule(self.rule())
                self.accept()
            except ValueError as error:
                QMessageBox.warning(self, 'Invalid filter', str(error))

    class Window(QMainWindow):
        def __init__(self):
            super().__init__()
            self.path, self.snapshot, self.rules = None, None, []
            self.resize(1050, 720)
            toolbar = QToolBar('Configuration')
            toolbar.setMovable(False)
            self.addToolBar(toolbar)
            for label, shortcut, slot in [('New', 'Ctrl+N', self.new), ('Open / Import', 'Ctrl+O', self.open),
                    ('Save', 'Ctrl+S', self.save), ('Save As', 'Ctrl+Shift+S', self.save_as),
                    ('Export for SD', 'Ctrl+E', self.export), ('Validate', 'F5', self.validate)]:
                action = QAction(label, self)
                action.setShortcut(shortcut)
                action.triggered.connect(slot)
                toolbar.addAction(action)
            self.tabs = QTabWidget()
            self.setCentralWidget(self.tabs)
            page = QWidget()
            form = QFormLayout(page)
            self.device = QLineEdit()
            self.enabled = QCheckBox('Enable physical channel CAN1')
            self.mode = combo([('Classical CAN', 'classic_can'), ('CAN FD', 'can_fd')])
            self.nominal = spin(10000, 1000000, ' bit/s')
            self.data_rate = spin(10000, 8000000, ' bit/s')
            for label, w in [('Device ID', self.device), ('', self.enabled), ('Mode', self.mode),
                             ('Nominal / arbitration bitrate', self.nominal), ('FD data bitrate', self.data_rate)]:
                form.addRow(label, w)
            form.addRow(note('CAN1 means the physical connector. Firmware maps it to the wired peripheral. CAN FD requires an FD-capable controller and transceiver. Firmware must validate exact bit timing; sample point and SJW overrides are not exported in this version.'))
            self.tabs.addTab(page, 'Bus Configuration')
            page = QWidget()
            layout = QVBoxLayout(page)
            self.filter_mode = combo([('Log all frames', 'all'), ('Log matching frames (OR)', 'matching')])
            layout.addWidget(self.filter_mode)
            layout.addWidget(note('Filters control storage. Trigger detection still sees excluded frames.'))
            self.table = QTableWidget(0, 5)
            self.table.setHorizontalHeaderLabels(['Name', 'Enabled', 'Identifier', 'Type', 'Condition'])
            self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setStretchLastSection(True)
            self.table.doubleClicked.connect(lambda _: self.edit_filter())
            layout.addWidget(self.table)
            row = QHBoxLayout()
            for label, slot in [('Add', self.add_filter), ('Edit', self.edit_filter),
                                ('Remove', self.remove_filter), ('Remove All', self.remove_all)]:
                button = QPushButton(label)
                button.clicked.connect(slot)
                row.addWidget(button)
            layout.addLayout(row)
            self.tabs.addTab(page, 'Filters')
            page = QWidget()
            form = QFormLayout(page)
            self.start = combo([('After initialization (power-on)', 'power_on'), ('CAN ID match', 'can_id_match')])
            self.stop = combo([('No configured stop', 'none'), ('CAN ID match', 'can_id_match'), ('Recording duration', 'duration')])
            self.start_id, self.stop_id = QLineEdit('0x123'), QLineEdit('0x124')
            self.start_ext, self.stop_ext = QCheckBox('Extended ID'), QCheckBox('Extended ID')
            self.duration = spin(1, 604800, ' seconds')
            self.rearm = QCheckBox('Wait for a new start ID after a normal stop')
            for label, w in [('Start recording', self.start), ('Start ID', self.start_id), ('', self.start_ext),
                             ('Stop recording', self.stop), ('Stop ID', self.stop_id), ('', self.stop_ext),
                             ('Recording duration', self.duration), ('Rearm', self.rearm)]:
                form.addRow(label, w)
            form.addRow(note('Trigger frames are stored if they pass filters. Duration starts at recording start; repeated start frames do not extend it. SD full or write failure stops without rearming. Power loss may lose buffered data.'))
            self.tabs.addTab(page, 'Triggers')
            page = QWidget()
            form = QFormLayout(page)
            self.asc, self.mf4 = QCheckBox('ASC'), QCheckBox('MF4 (ASAM MDF 4)')
            self.size = spin(1048576, 2146435072, ' bytes')
            self.split_time = spin(0, 604800, ' seconds')
            self.split_time.setSpecialValueText('Disabled')
            for label, w in [('Formats', self.asc), ('', self.mf4), ('File size limit', self.size), ('File duration limit', self.split_time)]:
                form.addRow(label, w)
            form.addRow(note('Split at the first enabled limit, separately for each output format. Never overwrite existing logs. MF4 requests a real MDF 4 writer in firmware; renaming ASC does not create MF4. The current Teensy sketch requires firmware changes for this configuration contract, MF4, and CAN FD.'))
            self.tabs.addTab(page, 'Log Files')
            self.preview = QPlainTextEdit()
            self.preview.setReadOnly(True)
            self.tabs.addTab(self.preview, 'JSON Preview')
            for w in (self.mode, self.start, self.stop):
                w.currentIndexChanged.connect(self.update_controls)
            self.tabs.currentChanged.connect(self.refresh_preview)
            self.apply(default_config())

        def update_controls(self):
            self.data_rate.setEnabled(self.mode.currentData() == 'can_fd')
            for selector, field, ext in [(self.start, self.start_id, self.start_ext), (self.stop, self.stop_id, self.stop_ext)]:
                field.setEnabled(selector.currentData() == 'can_id_match')
                ext.setEnabled(selector.currentData() == 'can_id_match')
            self.duration.setEnabled(self.stop.currentData() == 'duration')
            enabled = self.start.currentData() == 'can_id_match' and self.stop.currentData() != 'none'
            self.rearm.setEnabled(enabled)
            if not enabled:
                self.rearm.setChecked(False)

        def collect(self):
            data = default_config()
            data['device']['device_id'] = self.device.text().strip()
            ch = data['channels'][0]
            ch.update(enabled=self.enabled.isChecked(), mode=self.mode.currentData(),
                      nominal_bitrate_bps=self.nominal.value(),
                      data_bitrate_bps=self.data_rate.value() if self.mode.currentData() == 'can_fd' else None)
            ch['filters'].update(mode=self.filter_mode.currentData(), rules=copy.deepcopy(self.rules))
            for side, selector, field, ext in [('start', self.start, self.start_id, self.start_ext), ('stop', self.stop, self.stop_id, self.stop_ext)]:
                trigger = {'type': selector.currentData()}
                if trigger['type'] == 'can_id_match':
                    trigger.update(can_id=field.text().strip(), extended_id=ext.isChecked())
                elif trigger['type'] == 'duration':
                    trigger['seconds'] = self.duration.value()
                ch['triggers'][side] = trigger
            ch['triggers']['rearm_after_stop'] = self.rearm.isChecked()
            data['logging'].update(formats=[name for name, w in [('asc', self.asc), ('mf4', self.mf4)] if w.isChecked()],
                                   file_split_size_bytes=self.size.value(), file_split_time_seconds=self.split_time.value())
            return data

        def apply(self, data):
            validate_config(data)
            ch = data['channels'][0]
            self.device.setText(data['device']['device_id'])
            self.enabled.setChecked(ch['enabled'])
            select(self.mode, ch['mode'])
            self.nominal.setValue(ch['nominal_bitrate_bps'])
            self.data_rate.setValue(ch['data_bitrate_bps'] or 2000000)
            select(self.filter_mode, ch['filters']['mode'])
            self.rules = copy.deepcopy(ch['filters']['rules'])
            self.refresh_table()
            for side, selector, field, ext in [('start', self.start, self.start_id, self.start_ext), ('stop', self.stop, self.stop_id, self.stop_ext)]:
                trigger = ch['triggers'][side]
                select(selector, trigger['type'])
                field.setText(trigger.get('can_id', '0x123' if side == 'start' else '0x124'))
                ext.setChecked(trigger.get('extended_id', False))
            self.duration.setValue(ch['triggers']['stop'].get('seconds', 600))
            self.rearm.setChecked(ch['triggers']['rearm_after_stop'])
            self.asc.setChecked('asc' in data['logging']['formats'])
            self.mf4.setChecked('mf4' in data['logging']['formats'])
            self.size.setValue(data['logging']['file_split_size_bytes'])
            self.split_time.setValue(data['logging']['file_split_time_seconds'])
            self.update_controls()
            self.snapshot = copy.deepcopy(data)
            self.refresh_preview()
            self.title()

        def title(self):
            self.setWindowTitle('SkillLogger Configuration Tool — ' + (str(self.path) if self.path else 'Untitled'))

        def refresh_table(self):
            self.table.setRowCount(len(self.rules))
            for row, r in enumerate(self.rules):
                condition = ', '.join(r['ids']) if r['type'] == 'id_list' else (
                    f"{r['id_start']} – {r['id_end']}" if r['type'] == 'id_range' else f"Match {r['match_id']}; mask {r['mask']}")
                for col, value in enumerate([r['filter_id'], 'Yes' if r['enabled'] else 'No',
                                            'Extended' if r['extended_id'] else 'Standard', r['type'], condition]):
                    self.table.setItem(row, col, QTableWidgetItem(value))

        def edit_rule(self, index=None):
            if index is None:
                if len(self.rules) >= 64:
                    QMessageBox.warning(self, 'Limit', 'Maximum 64 filters')
                    return
                n = 1
                while any(r['filter_id'] == f'F{n}' for r in self.rules):
                    n += 1
                rule = dict(filter_id=f'F{n}', enabled=True, type='id_list', extended_id=False, ids=['0x123'])
            else:
                rule = self.rules[index]
            dialog = FilterDialog(self, rule)
            while dialog.exec() == QDialog.Accepted:
                rule = dialog.rule()
                if any(r['filter_id'] == rule['filter_id'] for i, r in enumerate(self.rules) if i != index):
                    QMessageBox.warning(self, 'Duplicate name', 'Choose a unique filter name')
                    continue
                if index is None:
                    self.rules.append(rule)
                else:
                    self.rules[index] = rule
                self.refresh_table()
                break

        def add_filter(self):
            self.edit_rule()

        def edit_filter(self):
            if self.table.currentRow() >= 0:
                self.edit_rule(self.table.currentRow())

        def remove_filter(self):
            if self.table.currentRow() >= 0:
                del self.rules[self.table.currentRow()]
                self.refresh_table()

        def remove_all(self):
            if self.rules and QMessageBox.question(self, 'Remove filters', 'Remove all filters?') == QMessageBox.Yes:
                self.rules.clear()
                self.refresh_table()

        def refresh_preview(self, *_):
            data = self.collect()
            self.preview.setPlainText(json.dumps(data, indent=2))
            try:
                validate_config(data)
                self.statusBar().showMessage('Valid schema 2.0 configuration; device must verify firmware capabilities.')
            except ValueError as error:
                self.statusBar().showMessage(str(error))

        def validate(self):
            try:
                validate_config(self.collect())
                QMessageBox.information(self, 'Valid', 'Schema 2.0 validation passed. Device capability checks are still required.')
            except ValueError as error:
                QMessageBox.warning(self, 'Invalid configuration', str(error))

        def may_discard(self):
            if self.collect() == self.snapshot:
                return True
            answer = QMessageBox.question(self, 'Unsaved changes', 'Save changes before continuing?',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)
            return self.save() if answer == QMessageBox.Save else answer == QMessageBox.Discard

        def new(self):
            if self.may_discard():
                self.path = None
                self.apply(default_config())

        def open(self):
            if not self.may_discard():
                return
            path, _ = QFileDialog.getOpenFileName(self, 'Open configuration', '', 'JSON files (*.json)')
            if path:
                try:
                    data = load_config(path)
                    self.path = path
                    self.apply(data)
                except (OSError, ValueError, RecursionError) as error:
                    QMessageBox.critical(self, 'Open failed', str(error))

        def write(self, path, adopt=True):
            try:
                data = self.collect()
                save_config(path, data)
                if adopt:
                    self.path, self.snapshot = path, copy.deepcopy(data)
                    self.title()
                self.statusBar().showMessage(f'Saved {path}')
                return True
            except (OSError, ValueError) as error:
                QMessageBox.critical(self, 'Save failed', str(error))
                return False

        def save(self):
            return self.write(self.path) if self.path else self.save_as()

        def save_as(self):
            path, _ = QFileDialog.getSaveFileName(self, 'Save configuration', self.path or 'config.json', 'JSON files (*.json)')
            return self.write(path if path.lower().endswith('.json') else path + '.json') if path else False

        def export(self):
            try:
                validate_config(self.collect())
            except ValueError as error:
                QMessageBox.warning(self, 'Invalid configuration', str(error))
                return
            folder = QFileDialog.getExistingDirectory(self, 'Select SD root or export folder')
            if folder:
                path = str(Path(folder) / 'config.json')
                if os.path.exists(path) and QMessageBox.question(self, 'Replace configuration',
                        'Replace config.json in this folder?') != QMessageBox.Yes:
                    return
                self.write(path, adopt=False)

        def closeEvent(self, event):
            event.accept() if self.may_discard() else event.ignore()

    app = QApplication(sys.argv)
    app.setApplicationName('SkillLogger Configuration Tool')
    app.setStyle('Fusion')
    window = Window()
    window.show()
    if '--smoke-test' in sys.argv:
        from PySide6.QtCore import QTimer
        original = load_config(Path(__file__).with_name('config.json'))
        window.apply(original)
        assert window.collect() == original, 'GUI changed the imported example'
        fd = copy.deepcopy(original)
        ch = fd['channels'][0]
        ch.update(mode='can_fd', data_bitrate_bps=2000000)
        ch['triggers'].update(start=dict(type='can_id_match', can_id='0x123', extended_id=False),
                              stop=dict(type='duration', seconds=600), rearm_after_stop=True)
        window.apply(fd)
        assert window.collect() == fd, 'GUI changed the FD/trigger configuration'
        for rule in original['channels'][0]['filters']['rules']:
            dialog = FilterDialog(window, rule)
            assert dialog.rule() == rule, 'Filter editor changed the rule'
            dialog.close()
        window.apply(original)
        for index in range(window.tabs.count()):
            window.tabs.setCurrentIndex(index)
        print('GUI startup, configuration round trips, filter dialogs and tabs passed')
        QTimer.singleShot(100, app.quit)
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
