
import sys
import os
import winreg
from PyQt6.QtWidgets import QApplication, QToolBar, QMenu, QToolButton, QWidget, QComboBox, QLabel
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon, QAction

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Import the original MainWindow class
try:
    from main import MainWindow
except ImportError:
    pass

from styles import LIGHT_THEME, DARK_THEME

class ThemeManager:
    def __init__(self, app):
        self.app = app
        self.current_theme = None
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_system_theme)
        self.check_timer.start(2000) # Check every 2 seconds
        
        # Initial check
        self.check_system_theme()

    def check_system_theme(self):
        try:
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            
            # AppsUseLightTheme: 1 = Light, 0 = Dark
            new_theme = "LIGHT" if value == 1 else "DARK"
            if new_theme != self.current_theme:
                self.apply_theme(new_theme)
        except Exception:
            # Fallback to light theme if detection fails
            if self.current_theme != "LIGHT":
                self.apply_theme("LIGHT")

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        if theme_name == "LIGHT":
            self.app.setStyleSheet(LIGHT_THEME)
        else:
            self.app.setStyleSheet(DARK_THEME)

class ModernMainWindow(MainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Easy Menu 菜单配置器")
        
        # Set object names for specific styling
        if self.centralWidget():
            self.centralWidget().setObjectName("CentralWidget")
        
        if hasattr(self, 'property_editor'):
            self.property_editor.setObjectName("PropertyEditor")
            
        self.override_styles()
        
    def createMenuBar(self):
        # Override to disable default menu bar creation
        # We will integrate the file menu into the toolbar instead
        pass

    def createToolBar(self):
        # Create a unified toolbar
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # --- Standard Toolbar Items ---
        
        # New
        new_action = QAction("新建", self)
        new_action.setToolTip("新建配置 (Ctrl+N)")
        new_action.triggered.connect(self.newConfig)
        toolbar.addAction(new_action)
        
        # Save
        save_action = QAction("保存", self)
        save_action.setToolTip("保存配置 (Ctrl+S)")
        save_action.triggered.connect(self.saveConfig)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Import
        import_btn_action = QAction("导入", self)
        import_btn_action.setToolTip("导入配置 (Ctrl+I)")
        import_btn_action.triggered.connect(self.importConfig)
        toolbar.addAction(import_btn_action)
        
        # Export
        export_btn_action = QAction("导出", self)
        export_btn_action.setToolTip("导出配置 (Ctrl+E)")
        export_btn_action.triggered.connect(self.exportConfig)
        toolbar.addAction(export_btn_action)
        
        toolbar.addSeparator()
        
        # Generate
        generate_code_action = QAction("生成代码", self)
        generate_code_action.setToolTip("生成C语言代码")
        generate_code_action.triggered.connect(self.generateCode)
        toolbar.addAction(generate_code_action)
        
        toolbar.addSeparator()
        
        # Encoding Setting (Independent)
        encoding_label = QLabel("编码:")
        encoding_label.setStyleSheet("padding-left: 5px; padding-right: 2px;")
        toolbar.addWidget(encoding_label)
        
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItem("GB2312", "gb2312")
        self.encoding_combo.addItem("UTF-8", "utf-8")
        self.encoding_combo.setToolTip("选择文件编码")
        
        # Set current selection
        index = self.encoding_combo.findData(self.encoding_setting)
        if index >= 0:
            self.encoding_combo.setCurrentIndex(index)
            
        self.encoding_combo.currentIndexChanged.connect(self.onEncodingChanged)
        toolbar.addWidget(self.encoding_combo)

    def onEncodingChanged(self, index):
        """Handle encoding change from toolbar combobox"""
        encoding = self.encoding_combo.itemData(index)
        self.encoding_setting = encoding
        if hasattr(self, 'statusBar'):
            self.statusBar().showMessage(f"编码设置已更改为: {encoding}")

    def override_styles(self):
        """
        Clear hardcoded styles from the original classes to allow 
        the global stylesheet (QSS) to take effect.
        """
        # Clear MainWindow style
        self.setStyleSheet("")
        
        # Clear TreeWidget style
        if hasattr(self, 'tree_widget'):
             self.tree_widget.setStyleSheet("")
             
        # Clear PropertyEditor style
        if hasattr(self, 'property_editor'):
             self.property_editor.setStyleSheet("")

if __name__ == '__main__':
    # Create QApplication with Fusion style for better QSS support
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setWindowIcon(QIcon(resource_path("图标.png")))
    
    # Initialize Theme Manager
    theme_manager = ThemeManager(app)
    
    # Create and show the modern window
    window = ModernMainWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())
