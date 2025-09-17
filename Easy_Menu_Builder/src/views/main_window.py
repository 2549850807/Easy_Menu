import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, 
                             QVBoxLayout, QHBoxLayout, QWidget, QPushButton, 
                             QMenuBar, QFileDialog, QMessageBox, QSplitter, QTextEdit, QTabWidget,
                             QMenu, QFrame, QLabel, QDialog)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QTextCharFormat, QColor, QFont, QSyntaxHighlighter
import re
import os
import sys as sys_module
sys_module.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from ..controllers.menu_controller import MenuController
from ..controllers.file_controller import FileController
from ..models.menu_item_model import MenuItemModel, MenuItemType
from .menu_tree_view import MenuTreeView
from .property_panel import PropertyPanel
from ..utils.style_manager import StyleManager


class CodeHighlighter(QSyntaxHighlighter):
    """C语言代码高亮器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        colors = StyleManager.get_brighter_color_scheme()
        
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(colors['keyword']))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        keywords = [
            'auto', 'break', 'case', 'char', 'const', 'continue', 'default',
            'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto',
            'if', 'int', 'long', 'register', 'return', 'short', 'signed',
            'sizeof', 'static', 'struct', 'switch', 'typedef', 'union',
            'unsigned', 'void', 'volatile', 'while', 'bool', 'true', 'false',
            'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t', 'int8_t', 'int16_t',
            'int32_t', 'int64_t', 'size_t', 'NULL'
        ]
        
        for word in keywords:
            pattern = QRegularExpression(r'\b' + word + r'\b')
            self.highlighting_rules.append((pattern, keyword_format))
        
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(colors['function']))
        function_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((QRegularExpression(r'\b[A-Za-z0-9_]+(?=\()'), function_format))
        
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(colors['number']))
        self.highlighting_rules.append((QRegularExpression(r'\b[0-9]+\b'), number_format))
        self.highlighting_rules.append((QRegularExpression(r'\b[0-9]*\.?[0-9]+([eE][+-]?[0-9]+)?[fF]?\b'), number_format))
        
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(colors['string']))
        self.highlighting_rules.append((QRegularExpression(r'".*"'), string_format))
        self.highlighting_rules.append((QRegularExpression(r"'.*'"), string_format))
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(colors['comment']))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegularExpression(r'//.*'), comment_format))
        self.highlighting_rules.append((QRegularExpression(r'/\*.*\*/'), comment_format))
        
        preprocessor_format = QTextCharFormat()
        preprocessor_format.setForeground(QColor(colors['preprocessor']))
        preprocessor_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((QRegularExpression(r'^\s*#.*'), preprocessor_format))
        
        type_format = QTextCharFormat()
        type_format.setForeground(QColor(colors['type']))
        type_format.setFontWeight(QFont.Weight.Bold)
        types = ['menu_item_t', 'navigator_t', 'data_type_t', 'key_value_t', 'line_state_t']
        for word in types:
            pattern = QRegularExpression(r'\b' + word + r'\b')
            self.highlighting_rules.append((pattern, type_format))

    def highlightBlock(self, text):
        """高亮文本块"""
        for pattern, format in self.highlighting_rules:
            expression = QRegularExpression(pattern)
            iterator = expression.globalMatch(text)
            
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


class SimulatorConfigDialog(QDialog):
    """仿真器配置对话框"""
    def __init__(self, main_simulator, parent=None):
        super().__init__(parent)
        self.main_simulator = main_simulator
        self.setWindowTitle("仿真器配置")
        self.setModal(False)
        self.resize(400, 300)
        
        from ..utils.simulator import Simulator
        self.config_simulator = Simulator()
        
        layout = QVBoxLayout(self)
        self.config_group = self.config_simulator.create_config_panel()
        layout.addWidget(self.config_group)
        
        info_label = QLabel("在此配置仿真器参数，配置将应用于代码预览界面中的仿真器")
        info_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(info_label)
        
        self.config_simulator.max_display_char_edit.textChanged.connect(self.on_config_changed)
        self.config_simulator.max_display_item_edit.textChanged.connect(self.on_config_changed)
        self.config_simulator.menu_select_cursor_edit.textChanged.connect(self.on_config_changed)
        self.config_simulator.menu_has_submenu_indicator_edit.textChanged.connect(self.on_config_changed)
        
        self.load_config_from_main()

    def on_config_changed(self):
        """当配置更改时的处理"""

    def load_config_from_main(self):
        """从主仿真器加载配置"""
        self.config_simulator.max_display_char_edit.setText(str(self.main_simulator.MAX_DISPLAY_CHAR))
        self.config_simulator.max_display_item_edit.setText(str(self.main_simulator.MAX_DISPLAY_ITEM))
        self.config_simulator.menu_select_cursor_edit.setText(self.main_simulator.MENU_SELECT_CURSOR)
        self.config_simulator.menu_has_submenu_indicator_edit.setText(self.main_simulator.MENU_HAS_SUBMENU_INDICATOR)

    def apply_config_to_main(self):
        """将配置应用到主仿真器"""
        try:
            self.main_simulator.MAX_DISPLAY_CHAR = int(self.config_simulator.max_display_char_edit.text())
            self.main_simulator.MAX_DISPLAY_ITEM = int(self.config_simulator.max_display_item_edit.text())
            self.main_simulator.MENU_SELECT_CURSOR = self.config_simulator.menu_select_cursor_edit.text()
            self.main_simulator.MENU_HAS_SUBMENU_INDICATOR = self.config_simulator.menu_has_submenu_indicator_edit.text()
            
            self.main_simulator._validate_cursor_indicators()
            
            self.main_simulator._update_display_size()
            
            self.main_simulator.refresh_display()
        except (ValueError, Exception) as e:
            print(f"应用配置时出错: {e}")

    def closeEvent(self, event):
        """对话框关闭事件"""
        self.apply_config_to_main()
        super().closeEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.menu_controller = MenuController()
        self.file_controller = FileController()
        self.init_ui()
        self.new_file()
        StyleManager.apply_apple_fluent_style()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("Easy_Menu 菜单配置器")
        self.setGeometry(100, 100, 1400, 800)

        self.create_menu_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self.create_file_tab()
        
        self.create_code_preview_tab()

        self.menu_tree_view.item_selected.connect(self.property_panel.set_current_item)
        self.property_panel.properties_changed.connect(self.on_properties_changed)

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        file_menu = menubar.addMenu('文件')

        new_action = file_menu.addAction('新建')
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)

        open_action = file_menu.addAction('打开')
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)

        save_action = file_menu.addAction('保存')
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)

        save_as_action = file_menu.addAction('另存为')
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_file_as)

        file_menu.addSeparator()

        generate_action = file_menu.addAction('生成代码')
        generate_action.setShortcut('Ctrl+G')
        generate_action.triggered.connect(self.generate_code)

        exit_action = file_menu.addAction('退出')
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        
        config_action = menubar.addAction('仿真器配置')
        config_action.triggered.connect(self.open_simulator_config)

    def open_simulator_config(self):
        """打开仿真器配置对话框"""
        try:
            if hasattr(self, 'simulator'):
                if not hasattr(self, 'simulator_config_dialog') or not self.simulator_config_dialog.isVisible():
                    self.simulator_config_dialog = SimulatorConfigDialog(self.simulator, self)
                    self._connect_simulator_configs()
                else:
                    self.simulator_config_dialog.load_config_from_main()
                    
                self.simulator_config_dialog.show()
                self.simulator_config_dialog.raise_()
                self.simulator_config_dialog.activateWindow()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法打开仿真器配置: {str(e)}')
            
    def _connect_simulator_configs(self):
        """连接主仿真器和配置对话框的配置同步"""
        if hasattr(self, 'simulator') and hasattr(self, 'simulator_config_dialog'):
            try:
                self.simulator.max_display_char_edit.textChanged.disconnect()
                self.simulator.max_display_item_edit.textChanged.disconnect()
                self.simulator.menu_select_cursor_edit.textChanged.disconnect()
                self.simulator.menu_has_submenu_indicator_edit.textChanged.disconnect()
            except TypeError:
                pass
                
            try:
                self.simulator_config_dialog.config_simulator.max_display_char_edit.textChanged.disconnect()
                self.simulator_config_dialog.config_simulator.max_display_item_edit.textChanged.disconnect()
                self.simulator_config_dialog.config_simulator.menu_select_cursor_edit.textChanged.disconnect()
                self.simulator_config_dialog.config_simulator.menu_has_submenu_indicator_edit.textChanged.disconnect()
            except TypeError:
                pass
            
            self.simulator.max_display_char_edit.textChanged.connect(
                self.simulator_config_dialog.config_simulator.max_display_char_edit.setText)
            self.simulator.max_display_item_edit.textChanged.connect(
                self.simulator_config_dialog.config_simulator.max_display_item_edit.setText)
            self.simulator.menu_select_cursor_edit.textChanged.connect(
                self.simulator_config_dialog.config_simulator.menu_select_cursor_edit.setText)
            self.simulator.menu_has_submenu_indicator_edit.textChanged.connect(
                self.simulator_config_dialog.config_simulator.menu_has_submenu_indicator_edit.setText)
                
            self.simulator_config_dialog.config_simulator.max_display_char_edit.textChanged.connect(
                self.simulator.max_display_char_edit.setText)
            self.simulator_config_dialog.config_simulator.max_display_item_edit.textChanged.connect(
                self.simulator.max_display_item_edit.setText)
            self.simulator_config_dialog.config_simulator.menu_select_cursor_edit.textChanged.connect(
                self.simulator.menu_select_cursor_edit.setText)
            self.simulator_config_dialog.config_simulator.menu_has_submenu_indicator_edit.textChanged.connect(
                self.simulator.menu_has_submenu_indicator_edit.setText)
                
            self.simulator_config_dialog.config_simulator.max_display_char_edit.textChanged.connect(
                self.simulator.on_config_changed)
            self.simulator_config_dialog.config_simulator.max_display_item_edit.textChanged.connect(
                self.simulator.on_config_changed)
            self.simulator_config_dialog.config_simulator.menu_select_cursor_edit.textChanged.connect(
                self.simulator.on_config_changed)
            self.simulator_config_dialog.config_simulator.menu_has_submenu_indicator_edit.textChanged.connect(
                self.simulator.on_config_changed)

    def create_file_tab(self):
        """创建文件标签页"""
        file_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.menu_tree_view = MenuTreeView(self.menu_controller)
        file_splitter.addWidget(self.menu_tree_view)

        self.property_panel = PropertyPanel(self.menu_controller)
        file_splitter.addWidget(self.property_panel)
        
        file_splitter.setSizes([400, 200])
        
        self.menu_tree_view.setMinimumWidth(200)
        self.property_panel.setMinimumWidth(150)

        self.tab_widget.addTab(file_splitter, "菜单")

    def create_code_preview_tab(self):
        """创建代码预览标签页"""
        code_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        code_preview_layout = QVBoxLayout()
        self.code_preview = QTextEdit()
        self.code_preview.setReadOnly(True)
        self.code_preview.setFontFamily("Consolas")
        self.code_preview.setFontPointSize(10)
        self.code_preview.setPlaceholderText("生成的C代码将显示在这里...")
        
        self.highlighter = CodeHighlighter(self.code_preview.document())
        
        code_preview_layout.addWidget(self.code_preview)
        
        generate_btn = QPushButton("生成代码")
        generate_btn.setObjectName("primaryButton")
        generate_btn.clicked.connect(self.generate_code)
        code_preview_layout.addWidget(generate_btn)
        
        code_preview_widget = QWidget()
        code_preview_widget.setLayout(code_preview_layout)
        code_splitter.addWidget(code_preview_widget)
        
        try:
            from ..utils.simulator import Simulator
            self.simulator = Simulator()
            self.simulator.config_group.hide()
            code_splitter.addWidget(self.simulator)
        except ImportError as e:
            error_label = QLabel(f"仿真器加载失败: {str(e)}")
            error_label.setStyleSheet("color: red; font-weight: bold;")
            code_splitter.addWidget(error_label)
        
        code_splitter.setSizes([600, 200])
        
        code_preview_widget.setMinimumWidth(300)
        
        self.tab_widget.addTab(code_splitter, "代码预览")

    def new_file(self):
        """新建文件"""
        self.file_controller.new_file()
        self.menu_controller = MenuController()
        self.menu_controller.config = self.file_controller.get_current_config()
        self.menu_tree_view.set_controller(self.menu_controller)
        self.property_panel.set_controller(self.menu_controller)
        self.code_preview.clear()
        self.statusBar().showMessage('新建文件', 2000)

    def open_file(self):
        """打开文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, '打开配置文件', '', 'JSON Files (*.json)')
        
        if file_path:
            config = self.file_controller.load_file(file_path)
            if config:
                self.menu_controller.config = config
                self.menu_tree_view.refresh_tree()
                self.code_preview.clear()
                self.statusBar().showMessage(f'已打开: {file_path}', 2000)
            else:
                QMessageBox.critical(self, '错误', '无法加载配置文件')

    def save_file(self):
        """保存文件"""
        if not self.file_controller.current_file_path:
            self.save_file_as()
        else:
            self.file_controller.config = self.menu_controller.config
            if self.file_controller.save_file():
                self.statusBar().showMessage(
                    f'已保存: {self.file_controller.current_file_path}', 2000)
            else:
                QMessageBox.critical(self, '错误', '无法保存文件')

    def save_file_as(self):
        """另存为文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, '保存配置文件', '', 'JSON Files (*.json)')
        
        if file_path:
            self.file_controller.config = self.menu_controller.config
            if self.file_controller.save_file(file_path):
                self.statusBar().showMessage(f'已保存: {file_path}', 2000)
            else:
                QMessageBox.critical(self, '错误', '无法保存文件')

    def generate_code(self):
        """生成代码"""
        try:
            code = self.menu_controller.generate_c_code()
            self.code_preview.setPlainText(code)
            
            # 重置并更新仿真器配置
            try:
                if hasattr(self, 'simulator') and self.simulator:
                    # 使用仿真器的set_menu_config方法来完全重置状态
                    if self.menu_controller.config:
                        self.simulator.set_menu_config(self.menu_controller.config)
                    else:
                        # 如果没有配置，确保清空仿真器状态
                        self.simulator.current_menu = None
                        self.simulator.selected_index = 0
                        self.simulator.first_visible_item = 0
                        self.simulator.in_app_mode = False
                        self.simulator.display_buffer = [""] * self.simulator.MAX_DISPLAY_ITEM
                        self.simulator.refresh_display()
                    
                    # 强制刷新显示
                    self.simulator.refresh_display()
                else:
                    pass
            except Exception as e:
                pass
            
            self.tab_widget.setCurrentIndex(1)
            
            reply = QMessageBox.question(
                self, '生成代码', '代码已生成，是否保存到文件？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.save_generated_code(code)
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'生成代码时出错: {str(e)}')

    def save_generated_code(self, code: str):
        """保存生成的代码到文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, '保存生成的代码', 'generated_code.c', 'C Files (*.c)')
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                self.statusBar().showMessage(f'代码已保存到: {file_path}', 2000)
            except Exception as e:
                QMessageBox.critical(self, '错误', f'保存代码时出错: {str(e)}')


    def on_properties_changed(self):
        """属性更改时的处理"""
        self.menu_tree_view.refresh_tree()
        self.statusBar().showMessage('属性已更新', 2000)