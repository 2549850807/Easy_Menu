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
        self.setMinimumSize(300, 200)  # 设置最小尺寸而不是固定尺寸
        
        # 默认仿真参数
        self.MAX_DISPLAY_CHAR = 20  # 显示的字符数量
        self.MAX_DISPLAY_ITEM = 8   # 显示的行数
        
        # 提示字符（必须由两个字符组成）
        self.MENU_SELECT_CURSOR = "->"  # 选择提示符
        self.MENU_HAS_SUBMENU_INDICATOR = ">>"  # 锁定提示符
        
        # 仿真状态
        self.current_menu = None
        self.selected_index = 0
        self.first_visible_item = 0
        self.in_app_mode = False
        
        # 验证提示字符长度
        self._validate_cursor_indicators()
        
        # 初始化显示缓冲区
        self.display_buffer = [""] * self.MAX_DISPLAY_ITEM
        
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 配置面板
        self.config_group = self.create_config_panel()
        
        # 仿真显示区域
        self.display_area = QTextEdit()
        self.display_area.setReadOnly(True)
        self.display_area.setFontFamily("Courier New")
        self.display_area.setFontPointSize(12)
        
        # 禁用滚动条
        self.display_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.display_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 设置黑底白字样式
        self._set_display_style()
        
        # 设置固定高度以匹配显示行数
        self._update_display_size()
        
        layout.addWidget(self.config_group)
        layout.addWidget(self.display_area)
        
        # 按钮区域
        button_frame = QFrame()
        button_layout = QGridLayout(button_frame)
        button_layout.setSpacing(10)
        
        # 上下左右按钮
        self.up_btn = QPushButton("↑")
        self.down_btn = QPushButton("↓")
        self.left_btn = QPushButton("←")
        self.right_btn = QPushButton("→")
        
        # 设置按钮大小
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
        
        # 布局按钮（十字排列）
        button_layout.addWidget(self.up_btn, 0, 1, Qt.AlignmentFlag.AlignCenter)
        button_layout.addWidget(self.left_btn, 1, 0, Qt.AlignmentFlag.AlignCenter)
        button_layout.addWidget(self.right_btn, 1, 2, Qt.AlignmentFlag.AlignCenter)
        button_layout.addWidget(self.down_btn, 2, 1, Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(button_frame, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 连接按钮信号
        self.up_btn.clicked.connect(lambda: self.handle_key_input("UP"))
        self.down_btn.clicked.connect(lambda: self.handle_key_input("DOWN"))
        self.left_btn.clicked.connect(lambda: self.handle_key_input("LEFT"))
        self.right_btn.clicked.connect(lambda: self.handle_key_input("RIGHT"))
        
        # 连接配置变化信号
        self.max_display_char_edit.textChanged.connect(self.on_config_changed)
        self.max_display_item_edit.textChanged.connect(self.on_config_changed)
        self.menu_select_cursor_edit.textChanged.connect(self.on_config_changed)
        self.menu_has_submenu_indicator_edit.textChanged.connect(self.on_config_changed)
        
        # 启用键盘事件
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def create_config_panel(self):
        """创建配置面板"""
        config_group = QGroupBox("仿真器配置")
        config_layout = QFormLayout(config_group)
        
        # MAX_DISPLAY_CHAR
        self.max_display_char_edit = QLineEdit(str(20))
        self.max_display_char_edit.setFixedWidth(100)
        config_layout.addRow("最大显示字符数:", self.max_display_char_edit)
        
        # MAX_DISPLAY_ITEM
        self.max_display_item_edit = QLineEdit(str(8))
        self.max_display_item_edit.setFixedWidth(100)
        config_layout.addRow("最大显示行数:", self.max_display_item_edit)
        
        # MENU_SELECT_CURSOR
        self.menu_select_cursor_edit = QLineEdit("->")
        self.menu_select_cursor_edit.setFixedWidth(100)
        config_layout.addRow("选择提示符:", self.menu_select_cursor_edit)
        
        # MENU_HAS_SUBMENU_INDICATOR
        self.menu_has_submenu_indicator_edit = QLineEdit(">>")
        self.menu_has_submenu_indicator_edit.setFixedWidth(100)
        config_layout.addRow("锁定提示符:", self.menu_has_submenu_indicator_edit)
        
        return config_group
        
    def _set_display_style(self):
        """设置显示区域样式为黑底白字"""
        palette = self.display_area.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0))  # 黑色背景
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))  # 白色文字
        self.display_area.setPalette(palette)
        self.display_area.setStyleSheet("QTextEdit { background-color: black; color: white; }")
        
    def _update_display_size(self):
        """更新显示区域大小"""
        # 设置显示区域的字体，确保计算准确
        font = self.display_area.font()
        font.setFamily("Courier New")
        font.setPointSize(12)
        self.display_area.setFont(font)
        
        font_metrics = self.display_area.fontMetrics()
        
        # 计算宽度
        char_width = font_metrics.horizontalAdvance('W')  # 使用宽字符计算宽度
        width = int(char_width * self.MAX_DISPLAY_CHAR + 20)  # 添加一些边距并转换为整数
        
        # 使用一个经验公式来计算高度
        # 通过实验发现，lineSpacing * MAX_DISPLAY_ITEM + 20 能够正确显示指定行数
        line_spacing = font_metrics.lineSpacing()
        height = line_spacing * self.MAX_DISPLAY_ITEM + 20
        
        # 设置显示区域大小
        self.display_area.setFixedSize(width, height)
        
        # 确保内容不会被截断
        self.display_area.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        
        # 调整窗口大小以适应内容
        self.adjustSize()
        
    def on_config_changed(self):
        """配置改变时的处理"""
        # 使用定时器延迟处理配置更改，确保在编辑完成后验证
        if not hasattr(self, '_config_timer'):
            self._config_timer = QTimer()
            self._config_timer.setSingleShot(True)
            self._config_timer.timeout.connect(self._apply_config_changes)
        self._config_timer.start(500)  # 500毫秒后应用更改
            
    def _apply_config_changes(self):
        """应用配置更改"""
        try:
            # 保存旧值用于恢复
            old_max_display_char = self.MAX_DISPLAY_CHAR
            old_max_display_item = self.MAX_DISPLAY_ITEM
            old_menu_select_cursor = self.MENU_SELECT_CURSOR
            old_menu_has_submenu_indicator = self.MENU_HAS_SUBMENU_INDICATOR
            
            # 更新参数
            self.MAX_DISPLAY_CHAR = int(self.max_display_char_edit.text())
            self.MAX_DISPLAY_ITEM = int(self.max_display_item_edit.text())
            self.MENU_SELECT_CURSOR = self.menu_select_cursor_edit.text()
            self.MENU_HAS_SUBMENU_INDICATOR = self.menu_has_submenu_indicator_edit.text()
            
            # 验证提示字符长度
            if not self._validate_cursor_indicators():
                # 如果验证失败，恢复原有值
                self.MAX_DISPLAY_CHAR = old_max_display_char
                self.MAX_DISPLAY_ITEM = old_max_display_item
                self.MENU_SELECT_CURSOR = old_menu_select_cursor
                self.MENU_HAS_SUBMENU_INDICATOR = old_menu_has_submenu_indicator
                
                # 更新编辑框显示
                self.max_display_char_edit.setText(str(old_max_display_char))
                self.max_display_item_edit.setText(str(old_max_display_item))
                self.menu_select_cursor_edit.setText(old_menu_select_cursor)
                self.menu_has_submenu_indicator_edit.setText(old_menu_has_submenu_indicator)
                
                # 显示警告信息
                QMessageBox.warning(self, "配置错误", "提示符必须由两个字符组成，已恢复默认值。")
            
            # 重新初始化显示缓冲区
            self.display_buffer = [""] * self.MAX_DISPLAY_ITEM
            
            # 更新显示区域大小
            self._update_display_size()
            
            # 刷新显示
            self.refresh_display()
        except (ValueError, Exception) as e:
            # 如果输入无效，恢复原有值
            self.max_display_char_edit.setText(str(self.MAX_DISPLAY_CHAR))
            self.max_display_item_edit.setText(str(self.MAX_DISPLAY_ITEM))
            self.menu_select_cursor_edit.setText(self.MENU_SELECT_CURSOR)
            self.menu_has_submenu_indicator_edit.setText(self.MENU_HAS_SUBMENU_INDICATOR)
            
    def _validate_cursor_indicators(self):
        """验证提示字符长度，如果不是两个字符则恢复默认值"""
        valid = True
        if len(self.MENU_SELECT_CURSOR) != 2:
            # 恢复默认值
            self.MENU_SELECT_CURSOR = "->"
            if hasattr(self, 'menu_select_cursor_edit'):
                self.menu_select_cursor_edit.setText("->")
            valid = False
        if len(self.MENU_HAS_SUBMENU_INDICATOR) != 2:
            # 恢复默认值
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
        # 为菜单项添加必要的属性
        self._initialize_menu_items(config.root_item)
        
        self.current_menu = config.root_item
        self.selected_index = 0
        self.first_visible_item = 0
        self.in_app_mode = False
        self.refresh_display()
        
    def _initialize_menu_items(self, item):
        """初始化菜单项属性"""
        # 为每个菜单项添加仿真所需的属性
        if not hasattr(item, 'is_locked'):
            item.is_locked = True
            
        if not hasattr(item, 'current_page'):
            item.current_page = 0
            
        if not hasattr(item, 'saved_selected_index'):
            item.saved_selected_index = 0
            
        if not hasattr(item, 'saved_first_visible_item'):
            item.saved_first_visible_item = 0
            
        # 添加展示项专用的可见项保存属性
        if not hasattr(item, 'saved_first_visible_item_before_exhibition'):
            item.saved_first_visible_item_before_exhibition = 0
            
        # 为可变项添加当前值属性
        if item.type.name == "CHANGEABLE":
            if not hasattr(item, 'current_val'):
                item.current_val = getattr(item, 'min_val', 0)
                
        # 为切换项添加状态属性
        if item.type.name == "TOGGLE":
            if not hasattr(item, 'state'):
                item.state = False
                
        # 递归初始化子项
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
                # 展示项未锁定时，上键切换页面
                current_item.current_page = (current_item.current_page - 1) % max(1, getattr(current_item, 'total_pages', 1))
        elif current_item.type.name in ["CHANGEABLE", "TOGGLE"]:
            if not current_item.is_locked:
                # 编辑模式下，上键增加值
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
                # 展示项未锁定时，下键切换页面
                current_item.current_page = (current_item.current_page + 1) % max(1, getattr(current_item, 'total_pages', 1))
        elif current_item.type.name in ["CHANGEABLE", "TOGGLE"]:
            if not current_item.is_locked:
                # 编辑模式下，下键减少值
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
            # 应用菜单项右键无效
            return
        elif current_item.type.name == "EXHIBITION":
            if current_item.is_locked:
                # 锁定状态下，右键进入编辑模式
                current_item.is_locked = False
                current_item.current_page = 0  # 重置到第一页
                # 保存当前的可见项范围，以便退出编辑模式时恢复
                current_item.saved_first_visible_item_before_exhibition = self.first_visible_item
                self.first_visible_item = self.selected_index
        elif current_item.type.name in ["CHANGEABLE", "TOGGLE"]:
            # 切换/可变菜单项进入编辑模式
            current_item.is_locked = False
        elif current_item.type.name == "NORMAL":
            # 普通菜单项进入子菜单
            if current_item.children:
                self.current_menu.saved_selected_index = self.selected_index
                self.current_menu.saved_first_visible_item = self.first_visible_item
                self.current_menu = current_item
                self.selected_index = 0
                self.first_visible_item = 0
                
    def _handle_left_key(self, current_item):
        """处理左键"""
        if current_item.type.name == "APPLICATION":
            # 应用菜单项左键返回上级菜单
            if self.current_menu.parent:
                self.current_menu = self.current_menu.parent
                self.selected_index = self.current_menu.saved_selected_index
                self.first_visible_item = self.current_menu.saved_first_visible_item
        elif current_item.type.name == "EXHIBITION":
            if not current_item.is_locked:
                # 展示项未锁定时，左键退出编辑模式
                current_item.is_locked = True
                # 恢复到进入展示项之前的可见项位置
                self.first_visible_item = current_item.saved_first_visible_item_before_exhibition
            else:
                # 展示项锁定时，左键返回上级菜单
                if self.current_menu.parent:
                    self.current_menu = self.current_menu.parent
                    self.selected_index = self.current_menu.saved_selected_index
                    self.first_visible_item = self.current_menu.saved_first_visible_item
        elif current_item.type.name in ["CHANGEABLE", "TOGGLE"]:
            if not current_item.is_locked:
                # 编辑模式下，左键退出编辑模式
                current_item.is_locked = True
            else:
                # 锁定状态下，左键返回上级菜单
                if self.current_menu.parent:
                    self.current_menu = self.current_menu.parent
                    self.selected_index = self.current_menu.saved_selected_index
                    self.first_visible_item = self.current_menu.saved_first_visible_item
        else:
            # 其他类型菜单项，左键返回上级菜单
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
            # 简化的值增加逻辑
            if not hasattr(item, 'current_val'):
                item.current_val = getattr(item, 'min_val', 0)
            item.current_val += getattr(item, 'step_val', 1)
            
            # 检查最大值限制
            max_val = getattr(item, 'max_val', 100)
            if item.current_val > max_val:
                item.current_val = max_val
                
    def _decrement_value(self, item):
        """减少可变项的值"""
        if item.type.name == "CHANGEABLE":
            # 简化的值减少逻辑
            if not hasattr(item, 'current_val'):
                item.current_val = getattr(item, 'max_val', 100)
            item.current_val -= getattr(item, 'step_val', 1)
            
            # 检查最小值限制
            min_val = getattr(item, 'min_val', 0)
            if item.current_val < min_val:
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
            
        # 清空显示缓冲区
        self.display_buffer = [""] * self.MAX_DISPLAY_ITEM
        
        if not self.in_app_mode:
            # 检查是否在展示项编辑模式
            current_item = self.current_menu.children[self.selected_index]
            if current_item.type.name == "EXHIBITION" and not current_item.is_locked:
                # 展示项编辑模式：只显示标题行，其他行清空
                indicator = self.MENU_SELECT_CURSOR if current_item.is_locked else self.MENU_HAS_SUBMENU_INDICATOR
                self.display_buffer[0] = self._format_item_display(current_item, indicator)
                # 其他行保持空状态（已经初始化为空字符串）
            else:
                # 普通模式：显示菜单项
                # 计算可见项数量
                visible_count = min(len(self.current_menu.children) - self.first_visible_item, 
                                  self.MAX_DISPLAY_ITEM)
                
                # 填充显示缓冲区
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
                # 根据C代码实现，展示项在编辑模式下需要显示页码信息
                # 统一使用新的显示逻辑：当页数为1时不显示页码，当页数大于1时显示页码
                if getattr(item, 'total_pages', 1) > 1:
                    display_text = f"{self.MENU_HAS_SUBMENU_INDICATOR}{item.name}({item.current_page + 1}/{item.total_pages}):"
                else:
                    display_text = f"{self.MENU_HAS_SUBMENU_INDICATOR}{item.name}:"
        elif item.type.name in ["CHANGEABLE", "TOGGLE"]:
            if item.type.name == "CHANGEABLE":
                # 获取当前值
                value_str = str(getattr(item, 'current_val', "0.0"))
            else:  # TOGGLE
                value_str = "ON" if getattr(item, 'state', False) else "OFF"
                
            if item.is_locked:
                display_text = f"{indicator}{item.name}: {value_str}"
            else:
                display_text = f"{self.MENU_HAS_SUBMENU_INDICATOR}{item.name}: {value_str}"
        elif item.type.name == "APPLICATION":
            display_text = f"{indicator}{item.name}"
        else:
            display_text = f"{indicator}{item.name}"
            
        # 确保显示文本不超过最大字符数限制
        if len(display_text) > self.MAX_DISPLAY_CHAR:
            display_text = display_text[:self.MAX_DISPLAY_CHAR]
        elif len(display_text) < self.MAX_DISPLAY_CHAR:
            # 如果文本长度小于最大字符数，用空格填充到指定长度
            display_text = display_text.ljust(self.MAX_DISPLAY_CHAR)
            
        return display_text
            
    def _update_display(self):
        """更新显示区域"""
        # 确保每次更新显示时都设置黑底白字样式
        self._set_display_style()
        
        display_text = "\n".join(self.display_buffer)
        self.display_area.setPlainText(display_text)