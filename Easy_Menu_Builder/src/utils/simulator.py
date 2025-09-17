from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTextEdit, QLabel, QGridLayout, QFrame, QLineEdit, QFormLayout, QGroupBox,
                             QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPalette, QTextOption
import os
import sys

class Simulator(QWidget):
    """菜单仿真器"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("菜单仿真器")
        self.setMinimumSize(300, 200)
        
        self.MAX_DISPLAY_CHAR = 20
        self.MAX_DISPLAY_ITEM = 8
        
        self.MENU_SELECT_CURSOR = "->"
        self.MENU_HAS_SUBMENU_INDICATOR = ">>"
        
        self.current_menu = None
        self.selected_index = 0
        self.first_visible_item = 0
        self.in_app_mode = False
        
        self._validate_cursor_indicators()
        
        self.display_buffer = [""] * self.MAX_DISPLAY_ITEM
        
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        self.config_group = self.create_config_panel()
        
        self.display_area = QTextEdit()
        self.display_area.setReadOnly(True)
        self.display_area.setFontFamily("Courier New")
        self.display_area.setFontPointSize(12)
        
        self.display_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.display_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self._set_display_style()
        
        self._update_display_size()
        
        layout.addWidget(self.config_group)
        layout.addWidget(self.display_area)
        
        button_frame = QFrame()
        button_layout = QGridLayout(button_frame)
        button_layout.setSpacing(10)
        
        self.up_btn = QPushButton("↑")
        self.down_btn = QPushButton("↓")
        self.left_btn = QPushButton("←")
        self.right_btn = QPushButton("→")
        
        button_size = 60
        for btn in [self.up_btn, self.down_btn, self.left_btn, self.right_btn]:
            btn.setFixedSize(button_size, button_size)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 20px;
                    font-weight: bold;
                    border: 2px solid #ccc;
                    border-radius: 30px;
                    background-color: #f0f0f0;
                }
                QPushButton:pressed {
                    background-color: #ddd;
                }
            """)
        
        button_layout.addWidget(self.up_btn, 0, 1, Qt.AlignmentFlag.AlignCenter)
        button_layout.addWidget(self.left_btn, 1, 0, Qt.AlignmentFlag.AlignCenter)
        button_layout.addWidget(self.right_btn, 1, 2, Qt.AlignmentFlag.AlignCenter)
        button_layout.addWidget(self.down_btn, 2, 1, Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(button_frame, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.up_btn.clicked.connect(lambda: self.handle_key_input("UP"))
        self.down_btn.clicked.connect(lambda: self.handle_key_input("DOWN"))
        self.left_btn.clicked.connect(lambda: self.handle_key_input("LEFT"))
        self.right_btn.clicked.connect(lambda: self.handle_key_input("RIGHT"))
        
        self.max_display_char_edit.textChanged.connect(self.on_config_changed)
        self.max_display_item_edit.textChanged.connect(self.on_config_changed)
        self.menu_select_cursor_edit.textChanged.connect(self.on_config_changed)
        self.menu_has_submenu_indicator_edit.textChanged.connect(self.on_config_changed)
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def create_config_panel(self):
        """创建配置面板"""
        config_group = QGroupBox("仿真器配置")
        config_layout = QFormLayout(config_group)
        
        self.max_display_char_edit = QLineEdit(str(20))
        self.max_display_char_edit.setFixedWidth(100)
        config_layout.addRow("最大显示字符数:", self.max_display_char_edit)
        
        self.max_display_item_edit = QLineEdit(str(8))
        self.max_display_item_edit.setFixedWidth(100)
        config_layout.addRow("最大显示行数:", self.max_display_item_edit)
        
        self.menu_select_cursor_edit = QLineEdit("->")
        self.menu_select_cursor_edit.setFixedWidth(100)
        config_layout.addRow("选择提示符:", self.menu_select_cursor_edit)
        
        self.menu_has_submenu_indicator_edit = QLineEdit(">>")
        self.menu_has_submenu_indicator_edit.setFixedWidth(100)
        config_layout.addRow("锁定提示符:", self.menu_has_submenu_indicator_edit)
        
        return config_group
        
    def _set_display_style(self):
        """设置显示区域样式为黑底白字"""
        palette = self.display_area.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        self.display_area.setPalette(palette)
        self.display_area.setStyleSheet("QTextEdit { background-color: black; color: white; }")
        
    def _update_display_size(self):
        """更新显示区域大小"""
        font = self.display_area.font()
        font.setFamily("Courier New")
        font.setPointSize(12)
        self.display_area.setFont(font)
        
        font_metrics = self.display_area.fontMetrics()
        
        char_width = font_metrics.horizontalAdvance('W')
        width = int(char_width * self.MAX_DISPLAY_CHAR + 20)
        
        line_spacing = font_metrics.lineSpacing()
        height = line_spacing * self.MAX_DISPLAY_ITEM + 20
        
        self.display_area.setFixedSize(width, height)
        
        self.display_area.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        
        self.adjustSize()
        
    def on_config_changed(self):
        """配置改变时的处理"""
        if not hasattr(self, '_config_timer'):
            self._config_timer = QTimer()
            self._config_timer.setSingleShot(True)
            self._config_timer.timeout.connect(self._apply_config_changes)
        self._config_timer.start(500)
            
    def _apply_config_changes(self):
        """应用配置更改"""
        try:
            old_max_display_char = self.MAX_DISPLAY_CHAR
            old_max_display_item = self.MAX_DISPLAY_ITEM
            old_menu_select_cursor = self.MENU_SELECT_CURSOR
            old_menu_has_submenu_indicator = self.MENU_HAS_SUBMENU_INDICATOR
            
            self.MAX_DISPLAY_CHAR = int(self.max_display_char_edit.text())
            self.MAX_DISPLAY_ITEM = int(self.max_display_item_edit.text())
            self.MENU_SELECT_CURSOR = self.menu_select_cursor_edit.text()
            self.MENU_HAS_SUBMENU_INDICATOR = self.menu_has_submenu_indicator_edit.text()
            
            if not self._validate_cursor_indicators():
                self.MAX_DISPLAY_CHAR = old_max_display_char
                self.MAX_DISPLAY_ITEM = old_max_display_item
                self.MENU_SELECT_CURSOR = old_menu_select_cursor
                self.MENU_HAS_SUBMENU_INDICATOR = old_menu_has_submenu_indicator
                
                self.max_display_char_edit.setText(str(old_max_display_char))
                self.max_display_item_edit.setText(str(old_max_display_item))
                self.menu_select_cursor_edit.setText(old_menu_select_cursor)
                self.menu_has_submenu_indicator_edit.setText(old_menu_has_submenu_indicator)
                
                QMessageBox.warning(self, "配置错误", "提示符必须由两个字符组成，已恢复默认值。")
            
            self.display_buffer = [""] * self.MAX_DISPLAY_ITEM
            
            self._update_display_size()
            
            self.refresh_display()
        except (ValueError, Exception) as e:
            self.max_display_char_edit.setText(str(self.MAX_DISPLAY_CHAR))
            self.max_display_item_edit.setText(str(self.MAX_DISPLAY_ITEM))
            self.menu_select_cursor_edit.setText(self.MENU_SELECT_CURSOR)
            self.menu_has_submenu_indicator_edit.setText(self.MENU_HAS_SUBMENU_INDICATOR)
            
    def _validate_cursor_indicators(self):
        """验证提示字符长度，如果不是两个字符则恢复默认值"""
        valid = True
        if len(self.MENU_SELECT_CURSOR) != 2:
            self.MENU_SELECT_CURSOR = "->"
            if hasattr(self, 'menu_select_cursor_edit'):
                self.menu_select_cursor_edit.setText("->")
            valid = False
        if len(self.MENU_HAS_SUBMENU_INDICATOR) != 2:
            self.MENU_HAS_SUBMENU_INDICATOR = ">>"
            if hasattr(self, 'menu_has_submenu_indicator_edit'):
                self.menu_has_submenu_indicator_edit.setText(">>")
            valid = False
        return valid
        
    def keyPressEvent(self, event):
        """处理键盘事件"""
        key = event.key()
        if key == Qt.Key.Key_Up:
            self.handle_key_input("UP")
        elif key == Qt.Key.Key_Down:
            self.handle_key_input("DOWN")
        elif key == Qt.Key.Key_Left:
            self.handle_key_input("LEFT")
        elif key == Qt.Key.Key_Right:
            self.handle_key_input("RIGHT")
        else:
            super().keyPressEvent(event)
            
    def set_menu_config(self, config):
        """设置菜单配置"""
        # 完全重置仿真器状态
        self.current_menu = None
        self.selected_index = 0
        self.first_visible_item = 0
        self.in_app_mode = False
        
        # 清空显示缓冲区
        self.display_buffer = [""] * self.MAX_DISPLAY_ITEM
        
        # 初始化菜单项
        if config and hasattr(config, 'root_item') and config.root_item:
            self._initialize_menu_items(config.root_item)
            self.current_menu = config.root_item
        else:
            pass
        
        # 刷新显示
        self.refresh_display()
        
    def _initialize_menu_items(self, item):
        """初始化菜单项属性"""
        # 重置所有菜单项的状态为初始值
        item.is_locked = True
        item.current_page = 0
        item.saved_selected_index = 0
        item.saved_first_visible_item = 0
        item.saved_first_visible_item_before_exhibition = 0
            
        if item.type.name == "CHANGEABLE":
            # 根据新的逻辑设置初始值
            if hasattr(item, 'min_val') and item.min_val is not None and item.min_val > 0:
                # 当最小值大于0时，初始值等于最小值
                item.current_val = float(item.min_val)
            elif hasattr(item, 'max_val') and item.max_val is not None and item.max_val < 0:
                # 当最大值小于0时，初始值等于最大值
                item.current_val = float(item.max_val)
            else:
                # 其他情况，初始值为0
                item.current_val = 0.0
            
            # 确保当前值在有效范围内
            if hasattr(item, 'min_val') and item.min_val is not None:
                if item.current_val < item.min_val:
                    item.current_val = float(item.min_val)
            if hasattr(item, 'max_val') and item.max_val is not None:
                if item.current_val > item.max_val:
                    item.current_val = float(item.max_val)
                
        if item.type.name == "TOGGLE":
            item.state = False
            
        if item.type.name == "EXHIBITION":
            item.current_page = 0
                
        for child in item.children:
            self._initialize_menu_items(child)
        
    def handle_key_input(self, key):
        """处理按键输入"""
        if not self.current_menu or not self.current_menu.children:
            return
            
        if self.in_app_mode:
            if key == "LEFT":
                self.in_app_mode = False
                self.refresh_display()
            return
            
        current_item = self.current_menu.children[self.selected_index]
        
        if key == "UP":
            self._handle_up_key(current_item)
        elif key == "DOWN":
            self._handle_down_key(current_item)
        elif key == "RIGHT":
            self._handle_right_key(current_item)
        elif key == "LEFT":
            self._handle_left_key(current_item)
            
        self.refresh_display()
        
    def _handle_up_key(self, current_item):
        """处理上键"""
        if current_item.type.name == "EXHIBITION":
            if current_item.is_locked:
                self._move_selection_up()
            else:
                current_item.current_page = (current_item.current_page - 1) % max(1, getattr(current_item, 'total_pages', 1))
        elif current_item.type.name in ["CHANGEABLE", "TOGGLE"]:
            if not current_item.is_locked:
                if current_item.type.name == "CHANGEABLE":
                    self._increment_value(current_item)
                elif current_item.type.name == "TOGGLE":
                    self._toggle_state(current_item)
            else:
                self._move_selection_up()
        else:
            self._move_selection_up()
            
    def _handle_down_key(self, current_item):
        """处理下键"""
        if current_item.type.name == "EXHIBITION":
            if current_item.is_locked:
                self._move_selection_down()
            else:
                current_item.current_page = (current_item.current_page + 1) % max(1, getattr(current_item, 'total_pages', 1))
        elif current_item.type.name in ["CHANGEABLE", "TOGGLE"]:
            if not current_item.is_locked:
                if current_item.type.name == "CHANGEABLE":
                    self._decrement_value(current_item)
                elif current_item.type.name == "TOGGLE":
                    self._toggle_state(current_item)
            else:
                self._move_selection_down()
        else:
            self._move_selection_down()
            
    def _handle_right_key(self, current_item):
        """处理右键"""
        if current_item.type.name == "APPLICATION":
            return
        elif current_item.type.name == "EXHIBITION":
            if current_item.is_locked:
                current_item.is_locked = False
                current_item.current_page = 0
                current_item.saved_first_visible_item_before_exhibition = self.first_visible_item
                self.first_visible_item = self.selected_index
        elif current_item.type.name in ["CHANGEABLE", "TOGGLE"]:
            current_item.is_locked = False
        elif current_item.type.name == "NORMAL":
            if current_item.children:
                self.current_menu.saved_selected_index = self.selected_index
                self.current_menu.saved_first_visible_item = self.first_visible_item
                self.current_menu = current_item
                self.selected_index = 0
                self.first_visible_item = 0
                
    def _handle_left_key(self, current_item):
        """处理左键"""
        if current_item.type.name == "APPLICATION":
            if self.current_menu.parent:
                self.current_menu = self.current_menu.parent
                self.selected_index = self.current_menu.saved_selected_index
                self.first_visible_item = self.current_menu.saved_first_visible_item
        elif current_item.type.name == "EXHIBITION":
            if not current_item.is_locked:
                current_item.is_locked = True
                self.first_visible_item = current_item.saved_first_visible_item_before_exhibition
            else:
                if self.current_menu.parent:
                    self.current_menu = self.current_menu.parent
                    self.selected_index = self.current_menu.saved_selected_index
                    self.first_visible_item = self.current_menu.saved_first_visible_item
        elif current_item.type.name in ["CHANGEABLE", "TOGGLE"]:
            if not current_item.is_locked:
                current_item.is_locked = True
            else:
                if self.current_menu.parent:
                    self.current_menu = self.current_menu.parent
                    self.selected_index = self.current_menu.saved_selected_index
                    self.first_visible_item = self.current_menu.saved_first_visible_item
        else:
            if self.current_menu.parent:
                self.current_menu = self.current_menu.parent
                self.selected_index = self.current_menu.saved_selected_index
                self.first_visible_item = self.current_menu.saved_first_visible_item
                
    def _move_selection_up(self):
        """向上移动选择"""
        self.selected_index = (self.selected_index - 1) % len(self.current_menu.children)
        self._adjust_visible_range()
        
    def _move_selection_down(self):
        """向下移动选择"""
        self.selected_index = (self.selected_index + 1) % len(self.current_menu.children)
        self._adjust_visible_range()
        
    def _adjust_visible_range(self):
        """调整可见范围"""
        if len(self.current_menu.children) > self.MAX_DISPLAY_ITEM:
            if self.selected_index >= self.first_visible_item + self.MAX_DISPLAY_ITEM:
                self.first_visible_item += self.MAX_DISPLAY_ITEM
            elif self.selected_index < self.first_visible_item:
                self.first_visible_item = max(0, self.selected_index - self.MAX_DISPLAY_ITEM + 1)
                
    def _increment_value(self, item):
        """增加可变项的值"""
        if item.type.name == "CHANGEABLE":
            # 确保current_val不为None
            if not hasattr(item, 'current_val') or item.current_val is None:
                item.current_val = getattr(item, 'min_val', 0) or 0
            
            # 确保step_val不为None
            step_val = getattr(item, 'step_val', 1)
            if step_val is None:
                step_val = 1
            
            item.current_val += step_val
            
            max_val = getattr(item, 'max_val', 100)
            if max_val is not None and item.current_val > max_val:
                item.current_val = max_val
                
    def _decrement_value(self, item):
        """减少可变项的值"""
        if item.type.name == "CHANGEABLE":
            # 确保current_val不为None
            if not hasattr(item, 'current_val') or item.current_val is None:
                item.current_val = getattr(item, 'max_val', 100) or 0
            
            # 确保step_val不为None
            step_val = getattr(item, 'step_val', 1)
            if step_val is None:
                step_val = 1
            
            item.current_val -= step_val
            
            min_val = getattr(item, 'min_val', 0)
            if min_val is not None and item.current_val < min_val:
                item.current_val = min_val
                
    def _toggle_state(self, item):
        """切换状态"""
        if item.type.name == "TOGGLE":
            item.state = not item.state
                
    def refresh_display(self):
        """刷新显示"""
        if not self.current_menu or not self.current_menu.children:
            self.display_buffer = [""] * self.MAX_DISPLAY_ITEM
            self._update_display()
            return
            
        self.display_buffer = [""] * self.MAX_DISPLAY_ITEM
        
        if not self.in_app_mode:
            current_item = self.current_menu.children[self.selected_index]
            if current_item.type.name == "EXHIBITION" and not current_item.is_locked:
                indicator = self.MENU_SELECT_CURSOR if current_item.is_locked else self.MENU_HAS_SUBMENU_INDICATOR
                self.display_buffer[0] = self._format_item_display(current_item, indicator)
            else:
                visible_count = min(len(self.current_menu.children) - self.first_visible_item, 
                                  self.MAX_DISPLAY_ITEM)
                
                for i in range(visible_count):
                    item_index = self.first_visible_item + i
                    if item_index < len(self.current_menu.children):
                        item = self.current_menu.children[item_index]
                        indicator = self.MENU_SELECT_CURSOR if self.selected_index == item_index else "  "
                        self.display_buffer[i] = self._format_item_display(item, indicator)
                        
        self._update_display()
        
    def _format_item_display(self, item, indicator):
        """格式化菜单项显示"""
        if item.type.name == "NORMAL":
            display_text = f"{indicator}{item.name}"
        elif item.type.name == "EXHIBITION":
            if item.is_locked:
                display_text = f"{indicator}{item.name}"
            else:
                if getattr(item, 'total_pages', 1) > 1:
                    display_text = f"{self.MENU_HAS_SUBMENU_INDICATOR}{item.name}({item.current_page + 1}/{item.total_pages}):"
                else:
                    display_text = f"{self.MENU_HAS_SUBMENU_INDICATOR}{item.name}:"
        elif item.type.name in ["CHANGEABLE", "TOGGLE"]:
            if item.type.name == "CHANGEABLE":
                current_val = getattr(item, 'current_val', 0)
                # 检查是否为浮点类型，如果是则格式化为2位小数
                if hasattr(item, 'data_type') and hasattr(item.data_type, 'name'):
                    if item.data_type.name in ["FLOAT", "DOUBLE"]:
                        value_str = f"{current_val:.2f}"
                    else:
                        value_str = str(int(current_val)) if isinstance(current_val, (int, float)) else str(current_val)
                else:
                    # 如果没有数据类型信息，根据值的类型判断
                    if isinstance(current_val, float):
                        value_str = f"{current_val:.2f}"
                    else:
                        value_str = str(current_val)
            else:
                value_str = "ON" if getattr(item, 'state', False) else "OFF"
                
            if item.is_locked:
                display_text = f"{indicator}{item.name}: {value_str}"
            else:
                display_text = f"{self.MENU_HAS_SUBMENU_INDICATOR}{item.name}: {value_str}"
        elif item.type.name == "APPLICATION":
            display_text = f"{indicator}{item.name}"
        else:
            display_text = f"{indicator}{item.name}"
            
        if len(display_text) > self.MAX_DISPLAY_CHAR:
            display_text = display_text[:self.MAX_DISPLAY_CHAR]
        elif len(display_text) < self.MAX_DISPLAY_CHAR:
            display_text = display_text.ljust(self.MAX_DISPLAY_CHAR)
            
        return display_text
            
    def _update_display(self):
        """更新显示区域"""
        self._set_display_style()
        
        display_text = "\n".join(self.display_buffer)
        self.display_area.setPlainText(display_text)