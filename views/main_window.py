import os
import json
import copy

from PySide6.QtCore import Qt, QSize,QUrl

from PySide6.QtGui import (
    QFont,
    QIcon,
    QColor,
    QAction,
    QDesktopServices
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
    QSizePolicy
    
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

from views.classic_can_dialog import ClassicCANSettingsDialog
from views.canfd_dialog import CANFDSettingsDialog
from views.log_config_widget import LogConfigWidget
from views.tree_delegate import ModernTreeDelegate
from app.controller import AppController
from services.config_repository import JsonConfigurationRepository

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
            "bitrate": "50.000 kbits/s",
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
        self.resize(1400, 850)

        # ------------------------------------------------------------------
        # Toolbar (New / Open / Save / Import / Export)
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
        imported_layout.setContentsMargins(10, 10, 10, 10)
        imported_layout.setSpacing(6)

        self.imported_label = QLabel("Imported Files")
        self.imported_label.setFont(section_font)
        imported_layout.addWidget(self.imported_label)

        self.imported_list = QListWidget()
        self.imported_list.setObjectName("importedList")
        self.imported_list.setUniformItemSizes(True)
        self.imported_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.imported_list.setSpacing(2)
        self.imported_list.setMaximumHeight(120)   # keep the list compact
        self.imported_list.itemClicked.connect(self.on_imported_file_clicked)
        imported_layout.addWidget(self.imported_list)
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
        # ---- Skillicon Technologies brand (top-right) ----
        self.skillicon_btn = QPushButton("Skillicon Technologies")
        self.skillicon_btn.setObjectName("skilliconBrand")
        self.skillicon_btn.setCursor(Qt.PointingHandCursor)
        self.skillicon_btn.setToolTip("Visit skillicon.in")
        self.skillicon_btn.setFlat(True)

        # Modern typography
        brand_font = QFont(FONT_FAMILY, 11)
        brand_font.setWeight(QFont.DemiBold)
        self.skillicon_btn.setFont(brand_font)

        # Open website on click
        self.skillicon_btn.clicked.connect(
          lambda: QDesktopServices.openUrl(QUrl("https://skillicon.in/"))
        )

        topbar.addWidget(self.skillicon_btn)
        topbar.addSpacing(16)   # nice gap before Help / theme buttons                   
        # Help button (left of the theme button)
        self.help_button = QPushButton("?")
        self.help_button.setObjectName("helpButton")
        self.help_button.setFixedSize(42, 42)
        self.help_button.setFont(QFont(FONT_FAMILY, 13, QFont.Bold))
        self.help_button.setCursor(Qt.PointingHandCursor)
        self.help_button.setToolTip("Help")
        self.help_button.clicked.connect(self.on_help)

        topbar.addWidget(self.help_button)
        topbar.addSpacing(8)
        self.theme_toggle = QPushButton()
        self.theme_toggle.setObjectName(
            "themeToggle"
        )

        self.theme_toggle.setFixedSize(
            42,
            42
        )

        self.theme_toggle.setCursor(
            Qt.PointingHandCursor
        )

        self.theme_toggle.setIconSize(
            QSize(18, 18)
        )

        self.theme_toggle.clicked.connect(
            self.toggle_theme
        )

        topbar.addWidget(
            self.theme_toggle
        )

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
        self.toolbar = QToolBar("Main toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.setIconSize(QSize(18, 18))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        self.act_new = QAction("New", self)
        self.act_new.setShortcut("Ctrl+N")
        self.act_new.setToolTip("New configuration (Ctrl+N)")
        self.act_new.triggered.connect(self.on_new)

        self.act_open = QAction("Open", self)
        self.act_open.setShortcut("Ctrl+O")
        self.act_open.setToolTip("Open configuration (Ctrl+O)")
        self.act_open.triggered.connect(self.on_open)

        self.act_save = QAction("Save", self)
        self.act_save.setShortcut("Ctrl+S")
        self.act_save.setToolTip("Save (Ctrl+S)")
        self.act_save.triggered.connect(self.on_save)

        self.act_save_as = QAction("Save As...", self)
        self.act_save_as.setShortcut("Ctrl+Shift+S")
        self.act_save_as.setToolTip("Save As (Ctrl+Shift+S)")
        self.act_save_as.triggered.connect(self.on_save_as)

        self.act_import = QAction("Import", self)
        self.act_import.setToolTip("Import settings from a JSON file")
        self.act_import.triggered.connect(self.on_import)

        # Make the Ctrl+S / Ctrl+Shift+S shortcuts work anywhere in the window
        self.addAction(self.act_save)
        self.addAction(self.act_save_as)

        # Save button: click = Save, small arrow = Save As
        save_menu = QMenu(self)
        save_menu.addAction(self.act_save_as)

        self.save_button = QToolButton()
        self.save_button.setDefaultAction(self.act_save)
        self.save_button.setMenu(save_menu)
        self.save_button.setPopupMode(QToolButton.MenuButtonPopup)
        self.save_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.save_button.setIconSize(QSize(18, 18))

        self.toolbar.addAction(self.act_new)
        self.toolbar.addAction(self.act_open)
        self.toolbar.addWidget(self.save_button)
        self.toolbar.addAction(self.act_import)
        

    def _refresh_toolbar_theme(self, c):
        for action, name in (
            (self.act_new, "new"),
            (self.act_open, "open"),
            (self.act_save, "save"),
            (self.act_import, "import"),
        ):
            action.setIcon(tinted_icon(name, c["toggle_icon"]))

        self.toolbar.setStyleSheet(
            f"""
            QToolBar {{
                background-color: {c['bg_panel']};
                border: none;
                border-bottom: 1px solid {c['border']};
                spacing: 2px;
                padding: 1px 6px;
            }}
            QToolBar::separator {{
                background-color: {c['border']};
                width: 1px;
                margin: 4px 4px;
            }}
            QToolButton {{
                color: {c['text_primary']};
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: {RADIUS_SM}px;
                padding: 2px 8px;
                font-size: 9pt;
            }}
            QToolButton:hover {{
                border: 1px solid {c['accent_blue']};
            }}
            QToolButton::menu-button {{
                border: none;
                width: 12px;
            }}
            """
        )

        self.statusBar().setStyleSheet(
            f"QStatusBar {{ background-color: {c['bg_panel']};"
            f" color: {c['text_secondary']}; }}"
        )

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
        item = QListWidgetItem(os.path.basename(path))
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
    # Toolbar actions
    # ------------------------------------------------------------------

    def on_new(self):
        self.classic_can_settings = (
          self.controller.get_classic_can()
       )
        self.classic_can_enabled = False
        self.current_file_path = None
        self._update_title()
        self._show_device_tree()
        self.statusBar().showMessage("New configuration", 3000)
        self.canfd_settings = dict(DEFAULT_CANFD)
        self.log_pages.apply(default_log_config())
        self.imported_list.clearSelection()

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
        # First time: no path yet, so ask for it. After that: save silently.
        if self.current_file_path is None:
            self.on_save_as()
            return

        if self._write_json(self.current_file_path):
            self.statusBar().showMessage(
                f"Saved: {self.current_file_path}", 3000
            )

    def on_save_as(self):
        start = self.current_file_path or ("config" + PROJECT_EXT)
        path, _ = QFileDialog.getSaveFileName(
            self, "Save As", start, PROJECT_FILTER
        )
        if not path:
            return

        if not os.path.splitext(path)[1]:
            path += PROJECT_EXT

        if self._write_json(path):
            self.current_file_path = path
            self._update_title()
            self.statusBar().showMessage(f"Saved: {path}", 3000)

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
            f"color: {c['text_primary']}; font-weight: 600;"
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
            f"#importedSection {{ {section_style} }}"
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

        # Imported list — transparent inside its section (only once)
        self.imported_list.setStyleSheet(
            f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: 0;
                padding: 2px;
            }}
            QListWidget::item {{
                color: {c['text_primary']};
                border-radius: {RADIUS_SM}px;
                padding: 6px 8px;
            }}
            QListWidget::item:hover {{
                background-color: {c['border']};
            }}
            QListWidget::item:selected {{
                background-color: {c['accent_blue']};
                color: #FFFFFF;
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