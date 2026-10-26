import os
import json
import copy

from PySide6.QtCore import Qt, QSize, QUrl, QTimer,QFile,QEvent, QRect

from PySide6.QtGui import (
    QFont,
    QIcon,
    QColor,
    QAction,
    QDesktopServices,
    QShortcut,
    QKeySequence,
    QPainter
)

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QFrame,
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QToolBar,
    QToolButton,
    QFileDialog,
    QMessageBox,
    QMenu,
    QMenuBar,
    QGraphicsDropShadowEffect,
    QStackedWidget,
    QSizePolicy,
    QStackedWidget,
    QSizePolicy,
    QStyledItemDelegate,
        QSizePolicy,
    QStyledItemDelegate,
    QStyle
)


from models.constants import (
    DEFAULT_CLASSIC_CAN,
    DEFAULT_CANFD,
    PROJECT_EXT,
    PROJECT_FILTER,
    JSON_FILTER,
    LOG_PAGES
)

from models.config_model import default_log_config

from services.config_validator import (
    validate_log_config
)

from services.config_repository import (
    save_json,
    load_json
)

from resources.theme import (
    LIGHT,
    DARK,
    RADIUS_SM,
    RADIUS_LG,
    FONT_FAMILY
)

from resources.icons import (
    tinted_icon,
    make_theme_icon
)

from resources.logo_widget import LogoWidget
from resources.skillicon_logo_data import skillicon_logo_icon
from resources.trash_icon_data import trash_pixmap

from views.classic_can_dialog import ClassicCANSettingsDialog
from views.canfd_dialog import CANFDSettingsDialog
from views.log_config_widget import LogConfigWidget
from views.tree_delegate import ModernTreeDelegate
from app.controller import AppController
from services.config_repository import JsonConfigurationRepository


class NewFileDelegate(QStyledItemDelegate):
    """Row height, 'new file' typing box, and the trash icon on the
    selected row of the imported files list."""

    ROW_HEIGHT = 34          # thickness of the blue band
    ICON_SIZE = 15           # trash icon size
    ICON_RIGHT_GAP = 14      # distance of the icon from the right edge
    

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(self.ROW_HEIGHT)
        return size

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect.adjusted(2, 3, -60, -3))

    @classmethod
    def trash_rect(cls, row_rect):
        s = cls.ICON_SIZE
        return QRect(
            row_rect.right() - cls.ICON_RIGHT_GAP - s,
            row_rect.center().y() - s // 2 + 1,
            s, s
        )

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        # icon only on the selected row of a real (saved/imported) file
        if (option.state & QStyle.State_Selected) and index.data(Qt.UserRole):
            painter.save()
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
            painter.drawPixmap(self.trash_rect(option.rect), trash_pixmap())
            painter.restore()

class ConfigurationTool(QMainWindow):
    
    @property
    def classic_can_settings(self):
        return self.controller.get_classic_can()

    @classic_can_settings.setter
    def classic_can_settings(self, settings):
        self.controller.update_classic_can(settings)

    
    @property
    def canfd_settings(self):
        return self.controller.get_canfd()

    @canfd_settings.setter
    def canfd_settings(self, settings):
        self.controller.update_canfd(settings)



    def __init__(self):
        super().__init__()
        self.controller = AppController(
        repository=JsonConfigurationRepository()
        )

        self.dark_mode = False
        self.current_file_path = None      # file used by Save / Ctrl+S
        # Classic CAN runtime configuration/state
        self.classic_can_settings = {
            "bitrate": "100.000 kbits/s",
            "sampling_point": "75%",
            "sjw": "1",
            "enabled": False,
        }
        self.classic_can_default_settings = dict(
            self.classic_can_settings
        )
        self.classic_can_default_all_settings = dict(
            self.classic_can_settings
        )
        self.classic_can_all_settings = dict(
            self.classic_can_settings
        )
        self.classic_can_enabled = False
        self.canfd_settings = dict(DEFAULT_CANFD)
        self.canfd_settings = self.controller.get_canfd()

        self.setWindowTitle("Configuration Tool")
        self.resize(1400, 950)
        print(self.screen().availableGeometry())

        # ------------------------------------------------------------------
        # Toolbar (New / Save / Import)
        # ------------------------------------------------------------------
        self._create_toolbar()

        # ------------------------------------------------------------------
        # Central layout
        # ------------------------------------------------------------------
        root = QWidget()
        self.setCentralWidget(root)

        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ---------------- Left sidebar ----------------
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(300)
        self.sidebar.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(
            20,
            24,
            20,
            24
        )
        sidebar_layout.setSpacing(0)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(10)

        # --------------------------------------------------------------
        # Configuration Tool text
        # --------------------------------------------------------------
        self.brand_label = QLabel(
            "Configuration Tool"
        )

        brand_font = QFont()
        brand_font.setFamilies(["Segoe UI Variable Display", "Segoe UI", "Arial"])
        brand_font.setPointSizeF(12.5)
        brand_font.setWeight(QFont.DemiBold)

        self.brand_label.setFont(
            brand_font
        )

        brand_row.addWidget(
            self.brand_label
        )

        brand_row.addStretch(1)

        sidebar_layout.addLayout(
            brand_row
        )
        sidebar_layout.addSpacing(14)
        section_font = QFont()
        section_font.setFamilies(["Segoe UI Variable Text", "Segoe UI", "Arial"])
        section_font.setPointSizeF(10.5)
        section_font.setWeight(QFont.DemiBold)

        # ================================================================
        # SECTION 1: Imported Files  (own frame + own layout)
        # ================================================================
        self.imported_section = QFrame()
        self.imported_section.setObjectName("importedSection")
        self.imported_section.setAttribute(Qt.WA_StyledBackground, True)
        imported_layout = QVBoxLayout(self.imported_section)
        imported_layout.setContentsMargins(0, 0, 0, 0)
        imported_layout.setSpacing(8)

        self.imported_label = QLabel("IMPORTED FILES")
        self.imported_label.setFont(section_font)
        imported_layout.addWidget(self.imported_label)

        self.imported_list = QListWidget()
        self.imported_list.setObjectName("importedList")
        self.imported_list.setUniformItemSizes(True)
        self.imported_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.imported_list.setSpacing(0)
        self.imported_list.setMinimumHeight(110)
        self.imported_list.setMaximumHeight(150)
        self.imported_list.itemClicked.connect(self.on_imported_file_clicked)
        self.imported_list.itemClicked.connect(self.on_imported_file_clicked)

        # "New file" row support
        self._pending_new_item = None   # blank row while the name is typed
        self._draft_item = None         # named row, not saved to disk yet
        self._draft_name = None
        self._last_folder = ""          # remembered after the first save
        self._imported_delegate = NewFileDelegate(self.imported_list)
        self.imported_list.setItemDelegate(self._imported_delegate)

        self._imported_delegate.closeEditor.connect(
            self._on_new_file_editor_closed
        )
        # Delete key on the imported files list
        self._delete_shortcut = QShortcut(
            QKeySequence("Delete"), self.imported_list
        )
        self._delete_shortcut.setContext(Qt.WidgetShortcut)
        self._delete_shortcut.activated.connect(self.on_delete_selected_file)
        # Click on the trash icon of the selected row
        self._press_item = None
        self._press_was_selected = False
        self.imported_list.viewport().installEventFilter(self)

        imported_layout.addWidget(self.imported_list)
        imported_layout.addWidget(self.imported_list)

        # New / Save / Import buttons under the list
        button_row = QHBoxLayout()
        button_row.setSpacing(10)

        self.new_button = QPushButton("+  New")
        self.new_button.setObjectName("newButton")
        self.new_button.clicked.connect(self.on_new)

        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.on_save)

        # small arrow next to Save -> opens the "Save As..." dropdown
        self.save_arrow_button = QPushButton("▾")
        self.save_arrow_button.setObjectName("saveArrowButton")
        self.save_arrow_button.setFixedWidth(30)
        self.save_arrow_button.setToolTip("More save options")
        self.save_arrow_button.clicked.connect(self._show_save_menu)

        self._save_menu = QMenu(self)
        self._save_menu.addAction(self.act_save_as)

        self.import_button = QPushButton("Import")
        self.import_button.setObjectName("importButton")
        self.import_button.clicked.connect(self.on_import)

        for button in (self.new_button, self.save_button,
                       self.save_arrow_button, self.import_button):
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumHeight(40)

        # Save + arrow are glued together so they look like one split button
        save_group = QHBoxLayout()
        save_group.setSpacing(0)
        save_group.addWidget(self.save_button, 1)
        save_group.addWidget(self.save_arrow_button)

        button_row.addWidget(self.new_button)
        button_row.addWidget(self.import_button)
        button_row.addLayout(save_group)

        imported_layout.addLayout(button_row)
        sidebar_layout.addWidget(self.imported_section, 0)
        sidebar_layout.addSpacing(12)

        # ================================================================
        # SECTION 2: Bus / Log Configuration  (own frame + own layout)
        # ================================================================
        self.config_section = QFrame()
        self.config_section.setObjectName("configSection")
        self.config_section.setAttribute(Qt.WA_StyledBackground, True)
        config_layout = QVBoxLayout(self.config_section)
        config_layout.setContentsMargins(10, 10, 10, 10)
        config_layout.setSpacing(6)

        self.config_label = QLabel("Configuration")
        self.config_label.setFont(section_font)
        config_layout.addWidget(self.config_label)

        self.new_tree = QTreeWidget()
        self.new_tree.setHeaderHidden(True)
        self.new_tree.setVisible(True)
        self.new_tree.setRootIsDecorated(False)
        self.new_tree.setIndentation(16)
        self.new_tree.setAnimated(True)
        self.new_tree.setExpandsOnDoubleClick(False)
        self.new_tree.setUniformRowHeights(True)
        self.new_tree.setMouseTracking(True)
        self.new_tree.viewport().setAttribute(Qt.WA_Hover, True)
        self.new_tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.new_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tree_delegate = ModernTreeDelegate(self.new_tree)
        self.new_tree.setItemDelegate(self.tree_delegate)
        self.new_tree.itemClicked.connect(self.on_tree_item_clicked)
        config_layout.addWidget(self.new_tree, 1)

        # stretch 1 = grow and fill remaining space under Imported Files
        sidebar_layout.addWidget(self.config_section, 1)
        self.imported_files = []
        
      

        root_layout.addWidget(
            self.sidebar
        )

        # ---------------- Main area ----------------
        main_area = QWidget()
        main_area.setObjectName(
            "mainArea"
        )

        main_area.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        main_layout = QVBoxLayout(
            main_area
        )

        main_layout.setContentsMargins(
            24,
            12,
            24,
            12
        )

        main_layout.setSpacing(10)

        topbar = QHBoxLayout()

        self.title_label = QLabel(
            "Configuration Tool"
        )

        title_font = QFont(
            FONT_FAMILY,
            21,
            QFont.Bold
         )

        self.title_label.setFont(
            title_font
        )

        topbar.addWidget(
            self.title_label
        )

        topbar.addStretch(1)

        # 1) Help button
        self.help_button = QPushButton("?")
        self.help_button.setObjectName("helpButton")
        self.help_button.setFixedSize(42, 42)
        self.help_button.setFont(QFont(FONT_FAMILY, 16, QFont.Bold))
        self.help_button.setCursor(Qt.PointingHandCursor)
        self.help_button.setToolTip("Help")
        self.help_button.clicked.connect(self.on_help)

        topbar.addWidget(self.help_button)
        topbar.addSpacing(3)

        # 2) Theme button
        self.theme_toggle = QPushButton()
        self.theme_toggle.setObjectName("themeToggle")
        self.theme_toggle.setFixedSize(42, 42)
        self.theme_toggle.setCursor(Qt.PointingHandCursor)
        self.theme_toggle.setIconSize(QSize(18, 18))
        self.theme_toggle.clicked.connect(self.toggle_theme)

        topbar.addWidget(self.theme_toggle)
        topbar.addSpacing(4)

        # 3) Skillicon logo (far right)
        self.skillicon_btn = QPushButton()
        self.skillicon_btn.setObjectName("skilliconBrand")
        self.skillicon_btn.setCursor(Qt.PointingHandCursor)
        self.skillicon_btn.setToolTip("Visit skillicon.in")
        self.skillicon_btn.setFlat(True)
        self.skillicon_btn.setIcon(skillicon_logo_icon())
        self.skillicon_btn.setIconSize(QSize(184, 34))

        # Open website on click (same as before)
        self.skillicon_btn.clicked.connect(
          lambda: QDesktopServices.openUrl(QUrl("https://skillicon.in/"))
        )

        topbar.addWidget(self.skillicon_btn)

        main_layout.addLayout(
            topbar
        )

        self.content_panel = QFrame()
        self.content_panel.setObjectName(
            "contentPanel"
        )

        self.content_panel.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        self.content_panel.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.content_panel.setMaximumHeight(500)
        content_layout = QVBoxLayout(self.content_panel)
        content_layout.setContentsMargins(12, 10, 12, 10)

        self.content_stack = QStackedWidget()
        self.content_stack.setVisible(False)

        self.log_pages = LogConfigWidget(
            get_full_config=self._collect_config,
            show_status=lambda msg: self.statusBar().showMessage(msg, 8000),
        )
        self.log_pages.configuration_changed.connect(
           self.sync_logging_to_model
        )
        # "Generate Config" button on the JSON Preview page
        self.log_pages.generate_requested.connect(self.on_export)

        self.classic_can_page = ClassicCANSettingsDialog(self)
        self.canfd_page = CANFDSettingsDialog(self)

        self.content_stack.addWidget(self.log_pages)         # 0
        self.content_stack.addWidget(self.classic_can_page)  # 1
        self.content_stack.addWidget(self.canfd_page)        # 2

        content_layout.addWidget(self.content_stack)
        shadow = QGraphicsDropShadowEffect(
            self
        )

        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(2)

        shadow.setColor(
            QColor(
                16,
                24,
                40,
                40
            )
        )

        self.content_panel.setGraphicsEffect(
            shadow
        )

        main_layout.addWidget(
            self.content_panel,
            1
        )

        root_layout.addWidget(
            main_area,
            1
        )

        self.apply_theme()
        self._show_device_tree()      # show the device tree on startup

    # ------------------------------------------------------------------
    # Toolbar
    # ------------------------------------------------------------------
    def _create_toolbar(self):
        # No top toolbar any more: New / Save / Import are sidebar buttons.
        # The actions stay so the keyboard shortcuts keep working.
        self.act_new = QAction("New", self)
        self.act_new.setShortcut("Ctrl+N")
        self.act_new.triggered.connect(self.on_new)

        self.act_open = QAction("Open", self)
        self.act_open.setShortcut("Ctrl+O")
        self.act_open.triggered.connect(self.on_open)

        self.act_save = QAction("Save", self)
        self.act_save.setShortcut("Ctrl+S")
        self.act_save.triggered.connect(self.on_save)

        self.act_save_as = QAction("Save As...", self)
        self.act_save_as.setShortcut("Ctrl+Shift+S")
        self.act_save_as.triggered.connect(self.on_save_as)

        self.act_import = QAction("Import", self)
        self.act_import.triggered.connect(self.on_import)

        for action in (self.act_new, self.act_open,
                       self.act_save, self.act_save_as):
            self.addAction(action)
        

    def _refresh_toolbar_theme(self, c):
        self.statusBar().setStyleSheet(
            f"QStatusBar {{ background-color: {c['bg_panel']};"
            f" color: {c['text_secondary']}; }}"
        )
        
    # ------------------------------------------------------------------
    # Unsaved-changes warning
    # ------------------------------------------------------------------
    def _snapshot(self):
        try:
            return json.dumps(self._collect_config(), sort_keys=True)
        except (ValueError, TypeError):
            return None

    def _mark_clean(self):
        """Remember the current configuration as 'saved'."""
        self._saved_snapshot = self._snapshot()

    def _has_unsaved_changes(self):
        current = self._snapshot()
        if current is None:          # half-typed / invalid values
            return True
        return current != self._saved_snapshot

    def _confirm_discard_changes(self):
        """Ask 'Save your changes?'. Returns True if it is OK to continue."""
        if not self._has_unsaved_changes():
            return True

        answer = QMessageBox.question(
            self, "Unsaved changes", "Save your changes?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save
        )
        if answer == QMessageBox.Cancel:
            return False
        if answer == QMessageBox.Save:
            self.on_save()
            # the file dialog may have been cancelled, or saving may have failed
            return not self._has_unsaved_changes()
        return True                  # Discard

    def _reselect_current_file(self):
        """Put the list highlight back on the file that is really open."""
        self.imported_list.clearSelection()
        for i in range(self.imported_list.count()):
            item = self.imported_list.item(i)
            if item.data(Qt.UserRole) == self.current_file_path:
                self.imported_list.setCurrentItem(item)
                break

    def closeEvent(self, event):
        if self._confirm_discard_changes():
            event.accept()
        else:
            event.ignore()
    # ------------------------------------------------------------------
    # Window title
    # ------------------------------------------------------------------
    def _update_title(self):
        name = (
            f" - {os.path.basename(self.current_file_path)}"
            if self.current_file_path else ""
        )
        self.setWindowTitle(f"Configuration Tool{name}")

    def sync_logging_to_model(self):
        try:
            settings = self.log_pages.collect()

            self.controller.update_logging_config(
                settings
            )

        except ValueError:
            # Allow users to edit temporarily incomplete values.
            # Validation will run again when saving.
            pass
    # ------------------------------------------------------------------
    # Configuration data (used by Save / Open / Import / Export)
    # ------------------------------------------------------------------
    
    def _collect_config(self) -> dict:

        # Collect the current logging settings
        log_data = self.log_pages.collect()

        # Update the central logging model
        self.controller.update_logging_config(
            log_data
        )

        # Preserve the existing configuration file format
        data = {
            "app": "CAN Configuration Tool",
            "version": 1,
            "classic_can": dict(self.classic_can_settings),
            "canfd": dict(self.canfd_settings),
        }

        data.update(log_data)

        return data

    
    def _apply_config(self, data):
        if not isinstance(data, dict) or not isinstance(
            data.get("classic_can"), dict
        ):
            raise ValueError("This is not a valid configuration file.")
        log_data = default_log_config()
        for key in ("filters", "triggers", "logging"):
            if key in data:
                log_data[key] = data[key]
        validate_log_config(log_data)

        settings = dict(DEFAULT_CLASSIC_CAN)
        settings.update(data["classic_can"])

        self.classic_can_settings = settings
        self.classic_can_enabled = bool(settings.get("enabled", False))
        canfd = dict(DEFAULT_CANFD)
        if isinstance(data.get("canfd"), dict):
            canfd.update(data["canfd"])
        self.canfd_settings = canfd
        # Restore logging values into the GUI
        self.log_pages.apply(log_data)

        # Synchronize logging with the Central Model
        self.controller.update_logging_config(
         log_data
        ) 

    
    
    def _write_json(self, path: str) -> bool:

      try:
        # Step 1: Collect configuration from the UI
        data = self._collect_config()

        # Step 2: Ask the controller to save
        self.controller.save_configuration(
            path,
            data
        )

        return True

      except ValueError as error:
        QMessageBox.warning(
            self,
            "Invalid configuration",
            str(error)
        )
        return False

      except (OSError, TypeError, KeyError) as error:
        QMessageBox.critical(
            self,
            "Save error",
            f"Could not save file:\n{error}"
        )
        return False
    
    def _read_json(self, path: str) -> bool:
        try:
            data = self.controller.load_configuration(path)

            self._apply_config(data)
            self._discard_draft()

            return True

        except FileNotFoundError:
            QMessageBox.warning(
                self,
                "File not found",
                "The selected configuration file could not be found."
            )

        except PermissionError:
            QMessageBox.warning(
                self,
                "Access denied",
                "You do not have permission to read this file."
            )

        except json.JSONDecodeError:
            QMessageBox.warning(
                self,
                "Invalid JSON",
                "The configuration file contains invalid JSON data."
            )

        except (ValueError, KeyError, TypeError) as error:
            QMessageBox.warning(
                self,
                "Invalid configuration",
                str(error)
            )

        except OSError as error:
            QMessageBox.critical(
                self,
                "File error",
                f"Could not read the configuration file:\n{error}"
            )

        return False


    # ------------------------------------------------------------------
    # Imported files list
    # ------------------------------------------------------------------
    def _add_imported_file(self, path: str):
        """Add a JSON file to the sidebar list if not already present."""
        path = os.path.normpath(os.path.abspath(path))
        if path in self.imported_files:
            for i in range(self.imported_list.count()):
                item = self.imported_list.item(i)
                if item.data(Qt.UserRole) == path:
                    self.imported_list.setCurrentItem(item)
                    break
            return

        self.imported_files.append(path)
        item = QListWidgetItem("•  " + os.path.basename(path))
        item.setData(Qt.UserRole, path)
        item.setToolTip(path)
        self.imported_list.addItem(item)
        self.imported_list.setCurrentItem(item)

    def on_imported_file_clicked(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        if not path:
            return
        if self._read_json(path):
            self.statusBar().showMessage(f"Loaded: {path}", 3000)
            self._show_device_tree()

    # ------------------------------------------------------------------
    # New file row (like "New File" in VS Code)
    # ------------------------------------------------------------------
    def _start_new_file_row(self):
        # Already typing a name? Just put the cursor back there.
        if self._pending_new_item is not None:
            self.imported_list.editItem(self._pending_new_item)
            return

        item = QListWidgetItem("")
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.imported_list.addItem(item)
        self.imported_list.setCurrentItem(item)
        self.imported_list.clearSelection()
        self.imported_list.scrollToItem(item)
        self._pending_new_item = item
        self.imported_list.setFocus()
        self.imported_list.editItem(item)

    def _on_new_file_editor_closed(self, editor, hint):
        item = self._pending_new_item
        if item is None:
            return
        name = item.text().strip()
        self._pending_new_item = None
        # Deferred: the editor is still closing at this moment
        QTimer.singleShot(0, lambda: self._finish_new_file(item, name))

    def _finish_new_file(self, item, name):
        def discard():
            row = self.imported_list.row(item)
            if row >= 0:
                self.imported_list.takeItem(row)

        if not name:                      # Esc or empty name
            discard()
            return

        if any(ch in name for ch in '<>:"/\\|?*'):
            QMessageBox.warning(
                self, "Invalid name",
                'A file name cannot contain any of these characters:\n'
                '< > : " / \\ | ? *'
            )
            discard()
            return

        if not name.lower().endswith(".json"):
            name += ".json"

        # name already used by another row in the list?
        for i in range(self.imported_list.count()):
            other = self.imported_list.item(i)
            if other is not item and \
               other.text().lstrip("• ").strip().lower() == name.lower():
                QMessageBox.warning(
                    self, "Name already used",
                    f"{name} is already in the list."
                )
                discard()
                return

        # Keep it as a draft: nothing is written to disk until Save
        item.setText("•  " + name)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        item.setToolTip("Not saved yet - click Save to choose a folder")
        self._draft_item = item
        self._draft_name = name
        self.imported_list.setCurrentItem(item)
        self.statusBar().showMessage(
            f"{name} created - click Save to choose where to store it", 6000
        )

    def _discard_draft(self):
        item = self._draft_item
        self._draft_item = None
        self._draft_name = None
        if item is not None:
            row = self.imported_list.row(item)
            if row >= 0:
                self.imported_list.takeItem(row)

    def _save_draft(self):
        """First Save of a file created with New: ask for the folder."""
        start = (
            os.path.join(self._last_folder, self._draft_name)
            if self._last_folder else self._draft_name
        )
        path, _ = QFileDialog.getSaveFileName(
            self, "Save new file", start, JSON_FILTER
        )
        if not path:
            return

        if not os.path.splitext(path)[1]:
            path += ".json"
        path = os.path.normpath(os.path.abspath(path))

        if path in self.imported_files:
            QMessageBox.warning(
                self, "Already in list",
                "That file is already in the imported files list.\n"
                "Please choose a different name."
            )
            return

        if not self._write_json(path):    # shows its own error message
            return

        item = self._draft_item
        self.imported_files.append(path)
        item.setText("•  " + os.path.basename(path))
        item.setData(Qt.UserRole, path)
        item.setToolTip(path)
        self._draft_item = None
        self._draft_name = None
        self._last_folder = os.path.dirname(path)

        self.current_file_path = path     # later saves go to this file
        self._update_title()
        self.imported_list.setCurrentItem(item)
        self.statusBar().showMessage(f"Saved: {path}", 3000)

  
    # ------------------------------------------------------------------
    # Toolbar actions
    # ------------------------------------------------------------------

    def on_new(self):
        self._discard_draft()   # drop an earlier unsaved draft, if any

        # 1) Reset every stored setting to the factory defaults
        self.classic_can_settings = dict(DEFAULT_CLASSIC_CAN)
        self.classic_can_enabled = False
        self.classic_can_default_settings = dict(DEFAULT_CLASSIC_CAN)
        self.classic_can_default_all_settings = dict(DEFAULT_CLASSIC_CAN)
        self.classic_can_all_settings = dict(DEFAULT_CLASSIC_CAN)
        self.canfd_settings = dict(DEFAULT_CANFD)
        self.controller.update_logging_config(default_log_config())
        self.log_pages.apply(default_log_config())

        # 2) Refresh the pages so they show the defaults right away
        self.classic_can_page.load_from_parent()
        self.canfd_page.load_from_parent()

        # 3) Forget the current file and start a new one
        self.current_file_path = None
        self._update_title()
        self._show_device_tree()
        self.statusBar().showMessage("New configuration", 3000)
        self.imported_list.clearSelection()

        # show the empty "type a file name" row
        self._start_new_file_row()
    def on_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open configuration", "", PROJECT_FILTER
        )
        if not path:
            return

        if self._read_json(path):
            self.current_file_path = path
            self._update_title()
            self._show_device_tree()
            self.statusBar().showMessage(f"Opened: {path}", 3000)

    def on_save(self):
        # file created with New but not saved yet -> ask for the folder
        if self.current_file_path is None and self._draft_item is not None:
            self._save_draft()
            return
        
        # First time: no path yet, so ask for it. After that: save silently.
        if self.current_file_path is None:
            self.on_save_as()
            return

        if self._write_json(self.current_file_path):
            self.statusBar().showMessage(
                f"Saved: {self.current_file_path}", 3000
            )

    def on_save_as(self):
        # New file that was never saved: same "choose folder" dialog
        if self.current_file_path is None and self._draft_item is not None:
            self._save_draft()
            return

        # Always ask for the path
        if self.current_file_path:
            start = self.current_file_path
        elif self._last_folder:
            start = os.path.join(self._last_folder, "config.json")
        else:
            start = "config.json"

        path, _ = QFileDialog.getSaveFileName(
            self, "Save As", start, JSON_FILTER
        )
        if not path:
            return

        if not os.path.splitext(path)[1]:
            path += ".json"
        path = os.path.normpath(os.path.abspath(path))

        if self._write_json(path):
            self.current_file_path = path
            self._last_folder = os.path.dirname(path)
            self._update_title()
            self._add_imported_file(path)   # shows it in the list
            self.statusBar().showMessage(f"Saved: {path}", 3000)

    def eventFilter(self, obj, event):
        if obj is self.imported_list.viewport():
            kind = event.type()

            if kind == QEvent.MouseButtonPress and \
               event.button() == Qt.LeftButton:
                item = self.imported_list.itemAt(event.position().toPoint())
                self._press_item = item
                self._press_was_selected = (
                    item is not None and item.isSelected()
                )

            elif kind == QEvent.MouseButtonRelease and \
                 event.button() == Qt.LeftButton:
                pos = event.position().toPoint()
                item = self.imported_list.itemAt(pos)
                if (item is not None
                        and item is self._press_item
                        and self._press_was_selected
                        and item.data(Qt.UserRole)):
                    hit = NewFileDelegate.trash_rect(
                        self.imported_list.visualItemRect(item)
                    ).adjusted(-6, -6, 6, 6)
                    if hit.contains(pos):
                        self.imported_list.setCurrentItem(item)
                        QTimer.singleShot(0, self.on_delete_selected_file)
                        return True
        return super().eventFilter(obj, event)
    
    def on_delete_selected_file(self):
        item = self.imported_list.currentItem()
        if item is None or item is self._pending_new_item:
            return

        # Draft created with New but never saved: just remove the row
        if item is self._draft_item:
            self._discard_draft()
            return

        path = item.data(Qt.UserRole)
        name = os.path.basename(path) if path else item.text()

        # Ask first
        answer = QMessageBox.question(
            self, "Remove file",
            f"Remove '{name}' from the list?\n\n",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if answer != QMessageBox.Yes:
            return

        # Remove from the list only. The file on disk is NOT touched.
        row = self.imported_list.row(item)
        if row >= 0:
            self.imported_list.takeItem(row)
        if path in self.imported_files:
            self.imported_files.remove(path)

        self.statusBar().showMessage(f"Removed from list: {name}", 3000)

    def _show_save_menu(self):
        # open the dropdown just below the Save button
        pos = self.save_button.mapToGlobal(
            self.save_button.rect().bottomLeft()
        )
        self._save_menu.exec(pos)

    def on_import(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import JSON", "", JSON_FILTER
        )
        if not path:
            return

        if self._read_json(path):
            self._add_imported_file(path)
            self._show_device_tree()
            self.statusBar().showMessage(f"Imported: {path}", 3000)

    def on_help(self):
        QMessageBox.information(
            self,
            "Help",
            "Configuration Tool\n\n"
            "Toolbar\n"
            "  New (Ctrl+N)  start a new configuration\n"
            "  Open (Ctrl+O)  open a saved configuration\n"
            "  Save (Ctrl+S)  save; the arrow next to it gives Save As\n"
            "  Import  load settings from a JSON file\n\n"
            "Tree on the left\n"
            "  Bus Configuration  Classic CAN and CAN FD settings\n"
            "  Log Configuration  Filters, Triggers and Log Files\n"
            "  JSON Preview  shows the configuration; use "
            "Generate Config to export it"
        )
        
    def on_export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export JSON", "config_export.json", JSON_FILTER
        )
        if not path:
            return

        if not os.path.splitext(path)[1]:
            path += ".json"

        if self._write_json(path):
            self.statusBar().showMessage(f"Exported: {path}", 3000)

    # ------------------------------------------------------------------
    # Device tree
    # ------------------------------------------------------------------
    def _show_device_tree(self):
        self.new_tree.clear()

        bus_item = QTreeWidgetItem(["Bus Configuration"])
        bus_item.addChild(QTreeWidgetItem(["Classic CAN"]))
        bus_item.addChild(QTreeWidgetItem(["CAN FD"]))

        self.new_tree.addTopLevelItem(bus_item)
        log_item = QTreeWidgetItem(["Log Configuration"])
        log_item.addChild(QTreeWidgetItem(["Filters"]))
        log_item.addChild(QTreeWidgetItem(["Triggers"]))
        log_item.addChild(QTreeWidgetItem(["Log Files"]))
        self.new_tree.addTopLevelItem(log_item)

        # JSON Preview as its own top-level item
        preview_item = QTreeWidgetItem(["JSON Preview"])
        self.new_tree.addTopLevelItem(preview_item)

        bus_item.setExpanded(False)
        self.new_tree.setVisible(True)
    
    
    def on_tree_item_clicked(self, item, column):
        if item.childCount() > 0:
            item.setExpanded(not item.isExpanded())
            return

        name = item.text(0)

        page = LOG_PAGES.get(name)
        if page:
            self.title_label.setText(name)
            self.content_stack.setVisible(True)
            self.content_stack.setCurrentWidget(self.log_pages)
            self.log_pages.show_page(page)
            return

        if name == "Classic CAN":
            self.title_label.setText("Classic CAN")
            self.classic_can_page.load_from_parent()
            self.content_stack.setVisible(True)
            self.content_stack.setCurrentWidget(self.classic_can_page)
            return

        if name == "CAN FD":
            self.title_label.setText("CAN FD")
            self.canfd_page.load_from_parent()
            self.content_stack.setVisible(True)
            self.content_stack.setCurrentWidget(self.canfd_page)
            return

  
    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------
    def toggle_theme(self):

        self.dark_mode = not self.dark_mode

        self.apply_theme()

    def apply_theme(self):

        c = (
            DARK
            if self.dark_mode
            else LIGHT
        )

        self.sidebar.setStyleSheet(
            f"""
            #sidebar {{
                background-color: {c['bg_panel']};
                border-right: 1px solid {c['border']};
            }}
            """
        )

        self.brand_label.setStyleSheet(
            f"color: {c['text_primary']};"
        )

        # Section titles — primary + bold (only once)
        self.imported_label.setStyleSheet(
            f"color: {c['text_secondary']}; font-size: 9pt; font-weight: 700;"
        )
        self.config_label.setStyleSheet(
            f"color: {c['text_primary']}; font-weight: 600;"
        )

        # Visible section boxes (only once)
        section_style = f"""
            background-color: {c['bg_main']};
            border: 2px solid {c['border']};
            border-radius: {RADIUS_LG}px;
        """
        self.imported_section.setStyleSheet(
            f"""
            #importedSection {{
                background: transparent;
                border: none;
            }}
            QPushButton {{
                color: {c['text_primary']};
                background-color: {c['btn_bg']};
                border: 1px solid {c['btn_border']};
                border-radius: 12px;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                border: 1px solid {c['accent_blue']};
            }}
            QPushButton:pressed {{
                background-color: {c['border']};
            }}

            QPushButton#newButton {{
                background-color: {c['bg_main']};
                border: 1px solid {c['border']};
                font-family: "Segoe UI";     /* NEW font   */
                font-size: 10pt;             /* NEW size   */
                font-weight: 400;            /* NEW weight */
            }}
            QPushButton#newButton:hover {{
                border: 1px solid {c['accent_blue']};
            }}

            QPushButton#saveButton {{
                font-family: "Segoe UI";     /* SAVE font   */
                font-size: 9pt;             /* SAVE size   */
                font-weight: 700;            /* SAVE weight */
            }}

            QPushButton#importButton {{
                font-family: "Segoe UI";     /* IMPORT font   */
                font-size: 9pt;             /* IMPORT size   */
                font-weight: 700;            /* IMPORT weight */
            }}
            QPushButton#saveButton {{
                padding: 0 8px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
            }}
            QPushButton#saveArrowButton {{
                padding: 0px;
                font-size: 11pt;
                font-weight: 700;
                border-left: none;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
            }}
            QPushButton#saveArrowButton:hover {{
                border: 1px solid {c['accent_blue']};
                border-left: none;
            }}
            """
        )
        self._save_menu.setStyleSheet(
            f"""
            QMenu {{
                background-color: {c['bg_panel']};
                color: {c['text_primary']};
                border: 1px solid {c['btn_border']};
                padding: 6px;
            }}
            QMenu::item {{
                padding: 8px 28px 8px 14px;
                border-radius: 6px;
                font-size: 11pt;
            }}
            QMenu::item:selected {{
                background-color: {c['accent_blue']};
                color: #FFFFFF;
            }}
            """
        )
        self.config_section.setStyleSheet(
            f"#configSection {{ {section_style} }}"
        )

        self.centralWidget().layout().itemAt(
            1
        ).widget().setStyleSheet(
            f"""
            #mainArea {{
                background-color: {c['bg_main']};
            }}
            """
        )

        self.title_label.setStyleSheet(
            f"color: {c['text_primary']};"
        )

        self.theme_toggle.setStyleSheet(
            f"""
            #themeToggle {{
                background-color: {c['bg_panel']};
                border: 1px solid {c['border']};
                border-radius: {RADIUS_SM}px;
            }}

            #themeToggle:hover {{
                border: 1px solid {c['accent_blue']};
            }}
            """
        )
        self.help_button.setStyleSheet(
            f"""
            #helpButton {{
                background-color: {c['bg_panel']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: {RADIUS_SM}px;
            }}

            #helpButton:hover {{
                border: 1px solid {c['accent_blue']};
            }}
            """
        )
        # Skillicon brand – deep yellow
        self.skillicon_btn.setStyleSheet(f"""
        #skilliconBrand {{
            background-color: transparent;
            border: none;
            padding: 6px 12px;
        }}
        #skilliconBrand:hover {{
            background-color: transparent;
            border: none;
        }}
        #skilliconBrand:pressed {{
            background-color: transparent;
            border: none;
        }}
        """)

        self.theme_toggle.setIcon(
            make_theme_icon(
                self.dark_mode,
                c["toggle_icon"]
            )
        )

        self.content_panel.setStyleSheet(
            f"""
            #contentPanel {{
                background-color: {c['bg_panel']};
                border: 1px solid {c['border']};
                border-radius: {RADIUS_LG}px;
            }}
            """
        )

        self.imported_list.setStyleSheet(
            f"""
            QListWidget {{
                background-color: {c['list_bg']};
                border: 1px solid {c['btn_border']};
                border-radius: {RADIUS_LG}px;
                outline: 0;
                padding: 3px;
                font-size: 11pt;
            }}
            QListWidget::item {{
                color: {c['text_primary']};
                border-radius: 5px;
                padding: 0px 40px 0px 12px;
            }}
            QListWidget::item:hover {{
                background-color: {c['border']};
            }}
            QListWidget::item:selected {{
                background-color: {c['accent_blue']};
                color: #FFFFFF;
            }}
            QListWidget QLineEdit {{
                background-color: {c['bg_main']};
                color: {c['text_primary']};
                border: 1px solid {c['btn_border']};
                border-radius: 5px;
                padding: 0px 10px;
                font-size: 10.5pt;
                selection-background-color: {c['accent_blue']};
                selection-color: #FFFFFF;
            }}
            """
        )
        self.new_tree.setStyleSheet(
            f"""
            QTreeWidget {{
                background-color: transparent;
                border: none;
                outline: 0;
            }}
            """
        )
        self.tree_delegate.set_colors(c)
        self.new_tree.viewport().update()

        self._refresh_toolbar_theme(c)
        self.log_pages.set_theme(c)
        self.classic_can_page.set_theme(c)
        self.canfd_page.set_theme(c)