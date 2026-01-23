"""
Easy Menu - 菜单配置生成器
基于PyQt6的可视化菜单配置工具，可生成嵌入式设备C语言菜单代码
"""

import sys
import json
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMenu, QMessageBox, QFormLayout, QGroupBox,
    QCheckBox, QComboBox, QFileDialog, QMenuBar, QToolBar, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon


def preserve_user_code(old_content, new_content):
    """
    Preserves user code between /* USER CODE BEGIN */ and /* USER CODE END */ markers,
    as well as between /* USER CODE VALUE BEGIN */ and /* USER CODE VALUE END */ markers,
    and between /* USER CODE PUBLIC BEGIN */ and /* USER CODE PUBLIC END */ markers.
    If a callback function existed in old_content but is not in new_content, it will be removed.
    """
    # Extract all user code blocks from the old content
    old_user_blocks = {}
    old_value_blocks = {}
    old_public_code_blocks = {}
    old_lines = old_content.split('\n')
    i = 0
    while i < len(old_lines):
        line = old_lines[i]
        if '/* USER CODE BEGIN */' in line:
            # Find the function name by looking backwards for the function signature
            func_start = i
            while func_start >= 0 and not ('void' in old_lines[func_start] and '(' in old_lines[func_start]):
                func_start -= 1
            
            if func_start >= 0:
                # Find the end of the function
                brace_count = 0
                func_end = func_start
                while func_end < len(old_lines):
                    if '{' in old_lines[func_end]:
                        brace_count += old_lines[func_end].count('{')
                    if '}' in old_lines[func_end]:
                        brace_count -= old_lines[func_end].count('}')
                    if brace_count == 0 and '}' in old_lines[func_end]:
                        break
                    func_end += 1
                
                if func_end < len(old_lines):
                    # Extract the user code between BEGIN and END
                    user_code_start = i + 1
                    user_code_end = func_end
                    for j in range(i, func_end):
                        if '/* USER CODE END */' in old_lines[j]:
                            user_code_end = j
                            break
                    
                    # Get the function signature (from the function name to the closing brace of function header)
                    # Find where the function header ends and body begins
                    header_end = func_start
                    brace_found = False
                    while header_end <= func_end:
                        if '{' in old_lines[header_end]:
                            brace_found = True
                            break
                        header_end += 1
                    
                    # Extract function header (up to and including the opening brace)
                    func_header_lines = old_lines[func_start:header_end+1]
                    full_func_sig = '\n'.join(func_header_lines)
                    
                    user_code = '\n'.join(old_lines[user_code_start:user_code_end])
                    old_user_blocks[full_func_sig.strip()] = user_code
        elif '/* USER CODE VALUE BEGIN */' in line:
            # Extract the user code between VALUE BEGIN and VALUE END
            value_code_start = i + 1
            value_code_end = len(old_lines)
            for j in range(i + 1, len(old_lines)):
                if '/* USER CODE VALUE END */' in old_lines[j]:
                    value_code_end = j
                    break
            
            user_value_code = '\n'.join(old_lines[value_code_start:value_code_end])
            old_value_blocks['/* USER CODE VALUE BEGIN */'] = user_value_code
        elif '/* USER CODE PUBLIC BEGIN */' in line:
            # Extract the user code between PUBLIC BEGIN and PUBLIC END
            public_code_start = i + 1
            public_code_end = len(old_lines)
            for j in range(i + 1, len(old_lines)):
                if '/* USER CODE PUBLIC END */' in old_lines[j]:
                    public_code_end = j
                    break
            
            user_public_code = '\n'.join(old_lines[public_code_start:public_code_end])
            old_public_code_blocks['/* USER CODE PUBLIC BEGIN */'] = user_public_code
        i += 1
    
    # Now, identify functions in old_content that are not present in new_content
    # These should be removed from the final output
    new_functions_with_user_code = []
    new_lines = new_content.split('\n')
    i = 0
    while i < len(new_lines):
        line = new_lines[i]
        if '/* USER CODE BEGIN */' in line:
            # Find the function signature by looking backwards
            func_start = i
            while func_start >= 0 and not ('void' in new_lines[func_start] and '(' in new_lines[func_start]):
                func_start -= 1
            
            if func_start >= 0:
                # Find where the function header ends
                header_end = func_start
                brace_found = False
                while header_end < len(new_lines):
                    if '{' in new_lines[header_end]:
                        brace_found = True
                        break
                    header_end += 1
                
                # Extract function header (up to and including the opening brace)
                func_header_lines = new_lines[func_start:header_end+1]
                full_func_sig = '\n'.join(func_header_lines)
                new_functions_with_user_code.append(full_func_sig.strip())
        i += 1
    
    # Remove old functions that are not in the new content
    functions_to_remove = []
    for old_func in old_user_blocks:
        if old_func not in new_functions_with_user_code:
            functions_to_remove.append(old_func)
    
    # Process new content and insert preserved user code
    result_lines = new_lines[:]  # Copy the new content
    i = 0
    while i < len(result_lines):
        line = result_lines[i]
        
        # Check if this is the start of a function with USER CODE BEGIN
        if '/* USER CODE BEGIN */' in line:
            # Find the function signature by looking backwards
            func_start = i
            while func_start >= 0 and not ('void' in result_lines[func_start] and '(' in result_lines[func_start]):
                func_start -= 1
            
            if func_start >= 0:
                # Find where the function header ends
                header_end = func_start
                brace_found = False
                while header_end < len(result_lines):
                    if '{' in result_lines[header_end]:
                        brace_found = True
                        break
                    header_end += 1
                
                # Extract function header (up to and including the opening brace)
                func_header_lines = result_lines[func_start:header_end+1]
                full_func_sig = '\n'.join(func_header_lines)
                
                # Check if this function existed in old content
                full_func_key = full_func_sig.strip()
                if full_func_key in old_user_blocks:
                    # Replace the user code between BEGIN and END
                    # Find the line with USER CODE END
                    end_line_idx = i
                    while end_line_idx < len(result_lines) and '/* USER CODE END */' not in result_lines[end_line_idx]:
                        end_line_idx += 1
                    
                    if end_line_idx < len(result_lines):
                        # Get the preserved user code
                        user_code_to_insert = old_user_blocks[full_func_key]
                        if user_code_to_insert.strip():
                            # Replace everything between BEGIN and END with preserved code
                            # Remove lines between BEGIN and END (excluding END line)
                            lines_to_remove = []
                            for j in range(i + 1, end_line_idx):
                                lines_to_remove.append(j)
                            # Remove in reverse order to maintain indices
                            for j in reversed(lines_to_remove):
                                if j < len(result_lines):
                                    del result_lines[j]
                            
                            # Insert the preserved user code after the BEGIN line
                            code_lines = user_code_to_insert.split('\n')
                            # Insert each line after the USER CODE BEGIN line
                            for j, code_line in enumerate(code_lines):
                                # Add all lines including empty ones to preserve formatting
                                result_lines.insert(i + 1 + j, code_line)
                            
                            # Adjust i to account for the new lines added
                            i = end_line_idx  # Move past the END line
                            continue  # Continue with next iteration
        
        # Check if this is the start of USER CODE VALUE section
        elif '/* USER CODE VALUE BEGIN */' in line:
            # Find the line with USER CODE VALUE END
            end_line_idx = i
            while end_line_idx < len(result_lines) and '/* USER CODE VALUE END */' not in result_lines[end_line_idx]:
                end_line_idx += 1
            
            if end_line_idx < len(result_lines):
                # Check if we have old value code to preserve
                if '/* USER CODE VALUE BEGIN */' in old_value_blocks:
                    # Get the preserved value code
                    value_code_to_insert = old_value_blocks['/* USER CODE VALUE BEGIN */']
                    if value_code_to_insert.strip():
                        # Replace everything between VALUE BEGIN and VALUE END with preserved code
                        # Remove lines between VALUE BEGIN and VALUE END (excluding VALUE END line)
                        lines_to_remove = []
                        for j in range(i + 1, end_line_idx):
                            lines_to_remove.append(j)
                        # Remove in reverse order to maintain indices
                        for j in reversed(lines_to_remove):
                            if j < len(result_lines):
                                del result_lines[j]
                        
                        # Insert the preserved value code after the VALUE BEGIN line
                        code_lines = value_code_to_insert.split('\n')
                        # Insert each line after the USER CODE VALUE BEGIN line
                        for j, code_line in enumerate(code_lines):
                            # Add all lines including empty ones to preserve formatting
                            result_lines.insert(i + 1 + j, code_line)
                        
                        # Adjust i to account for the new lines added
                        i = end_line_idx  # Move past the VALUE END line
                        continue  # Continue with next iteration
                    else:
                        # If no preserved code, still need to adjust i to skip to END marker
                        i = end_line_idx  # Move past the VALUE END line
                        continue  # Continue with next iteration
                else:
                    # If no preserved code, still need to adjust i to skip to END marker
                    i = end_line_idx  # Move past the VALUE END line
                    continue  # Continue with next iteration
        
        # Check if this is the start of USER CODE PUBLIC section
        elif '/* USER CODE PUBLIC BEGIN */' in line:
            # Find the line with USER CODE PUBLIC END
            end_line_idx = i
            while end_line_idx < len(result_lines) and '/* USER CODE PUBLIC END */' not in result_lines[end_line_idx]:
                end_line_idx += 1
            
            if end_line_idx < len(result_lines):
                # Check if we have old public code to preserve
                if '/* USER CODE PUBLIC BEGIN */' in old_public_code_blocks:
                    # Get the preserved public code
                    public_code_to_insert = old_public_code_blocks['/* USER CODE PUBLIC BEGIN */']
                    if public_code_to_insert.strip():
                        # Replace everything between PUBLIC BEGIN and PUBLIC END with preserved code
                        # Remove lines between PUBLIC BEGIN and PUBLIC END (excluding END line)
                        lines_to_remove = []
                        for j in range(i + 1, end_line_idx):
                            lines_to_remove.append(j)
                        # Remove in reverse order to maintain indices
                        for j in reversed(lines_to_remove):
                            if j < len(result_lines):
                                del result_lines[j]
                        
                        # Insert the preserved public code after the PUBLIC BEGIN line
                        code_lines = public_code_to_insert.split('\n')
                        # Insert each line after the USER CODE PUBLIC BEGIN line
                        for j, code_line in enumerate(code_lines):
                            # Add all lines including empty ones to preserve formatting
                            result_lines.insert(i + 1 + j, code_line)
                        
                        # Adjust i to account for the new lines added
                        i = end_line_idx  # Move past the PUBLIC END line
                    else:
                        # If no preserved code, still need to adjust i to skip to END marker
                        i = end_line_idx  # Move past the PUBLIC END line
                else:
                    # If no preserved code, still need to adjust i to skip to END marker
                    i = end_line_idx  # Move past the PUBLIC END line

        i += 1
    
    # Remove functions that exist in old content but not in new content
    # We need to parse the result_lines and remove the functions that were in old_user_blocks but not in new content
    if functions_to_remove:
        # Identify the complete function blocks in result_lines that need to be removed
        lines_to_remove = []
        result_i = 0
        while result_i < len(result_lines):
            line = result_lines[result_i]
            if '/* USER CODE BEGIN */' in line:
                # Find the function signature by looking backwards
                func_start = result_i
                while func_start >= 0 and not ('void' in result_lines[func_start] and '(' in result_lines[func_start]):
                    func_start -= 1
                
                if func_start >= 0:
                    # Find where the function header ends
                    header_end = func_start
                    brace_found = False
                    while header_end < len(result_lines):
                        if '{' in result_lines[header_end]:
                            brace_found = True
                            break
                        header_end += 1
                    
                    # Extract function header (up to and including the opening brace)
                    func_header_lines = result_lines[func_start:header_end+1]
                    full_func_sig = '\n'.join(func_header_lines)
                    
                    # Check if this function signature matches any to be removed
                    full_func_key = full_func_sig.strip()
                    if full_func_key in functions_to_remove:
                        # Mark this entire function block for removal
                        brace_count = 0
                        func_end = func_start
                        while func_end < len(result_lines):
                            if '{' in result_lines[func_end]:
                                brace_count += result_lines[func_end].count('{')
                            if '}' in result_lines[func_end]:
                                brace_count -= result_lines[func_end].count('}')
                            if brace_count == 0 and '}' in result_lines[func_end]:
                                break
                            func_end += 1
                        
                        # Add all lines from func_start to func_end to be removed
                        for k in range(func_start, func_end + 1):
                            lines_to_remove.append(k)
            result_i += 1
        
        # Build final result excluding marked lines (process in reverse order to maintain indices)
        lines_to_remove.sort(reverse=True)
        for idx in lines_to_remove:
            if idx < len(result_lines):
                del result_lines[idx]
        
        return '\n'.join(result_lines)
    
    return '\n'.join(result_lines)


class MenuItem(QTreeWidgetItem):
    """菜单项类，表示一个页面或条目"""
    
    def __init__(self, name="新页面", item_type="普通页面", parent=None):
        super().__init__(parent)
        self.name = name
        self.item_type = item_type
        self.setText(0, name)  # 第一栏：显示名称
        self.setText(1, item_type)  # 第二栏：类型
        
        # 根据类型初始化默认属性
        properties = self._get_default_properties(item_type, name)
        
        # 存储自定义数据
        self.setData(0, Qt.ItemDataRole.UserRole, {
            "name": name,
            "type": item_type,
            "properties": properties
        })
    
    def _get_default_properties(self, item_type, name):
        """根据类型获取默认属性"""
        properties = {}
        
        if item_type == "普通页面":
            properties = {
                "变量名": name
            }
        elif item_type == "展示页面":
            properties = {
                "变量名": name,
                "周期": "100",
                "进入回调函数": False,
                "周期回调函数": True,  # 默认勾选
                "退出回调函数": False
            }
        elif item_type == "文本条目":
            properties = {
                "回调函数": False,
                "回调函数名": ""
            }
        elif item_type == "开关条目":
            properties = {
                "变量名": f"{name}_data",
                "初始值": "0",
                "回调函数": False,
                "回调函数名": ""
            }
        elif item_type == "数据条目":
            properties = {
                "变量类型": "uint8_val",
                "变量名": f"{name}_data",
                "初始值": "0",
                "步进": "1",
                "最小值": "NULL",
                "最大值": "NULL",
                "回调函数": False,
                "回调函数名": ""
            }
        elif item_type == "枚举条目":
            properties = {
                "枚举数量": "1",
                "枚举字符串": ["str1"],  # 初始一个选项
                "回调函数": False,
                "回调函数名": ""
            }
        elif item_type == "展示条目":
            properties = {
                "周期": "100",
                "变量类型": "uint8_val",
                "变量名": f"{name}_data",
                "初始值": "0",
                "回调函数": False,
                "回调函数名": ""
            }
        elif item_type == "跳转条目":
            properties = {
                "目标页面": "NULL"
            }
        
        return properties
    
    def update_property(self, key, value):
        """更新属性值"""
        data = self.data(0, Qt.ItemDataRole.UserRole)
        if data and "properties" in data:
            data["properties"][key] = value
            self.setData(0, Qt.ItemDataRole.UserRole, data)
    
    def get_property(self, key, default=None):
        """获取属性值"""
        data = self.data(0, Qt.ItemDataRole.UserRole)
        if data and "properties" in data:
            return data["properties"].get(key, default)
        return default


class MenuTreeWidget(QTreeWidget):
    """菜单树形视图组件"""
    
    # 自定义信号
    itemSelected = pyqtSignal(QTreeWidgetItem)
    contextMenuRequested = pyqtSignal(object, str)  # 改为 object 以接受 None
    
    def __init__(self):
        super().__init__()
        # 设置两栏：显示名称和类型
        self.setHeaderLabels(["显示名称", "类型"])
        self.setColumnWidth(0, 200)  # 设置第一栏宽度
        self.setColumnWidth(1, 100)  # 设置第二栏宽度
        
        # 启用拖动功能
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.itemClicked.connect(self.onItemClicked)
        
        # 设置样式
        self.setStyleSheet("""
            QTreeWidget {
                font-size: 12px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QTreeWidget::item {
                padding: 5px;
                height: 25px;
            }
            QTreeWidget::item:selected {
                background-color: #e0e0e0;
                color: #000;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
    
    def onItemClicked(self, item, column):
        """项目被点击时发出信号"""
        self.itemSelected.emit(item)
    
    def dropEvent(self, event):
        """重写拖放事件，检查目标项目类型"""
        # 获取鼠标位置下的目标项目
        position = event.position().toPoint()  # 修复：使用position()而不是pos()
        target_item = self.itemAt(position)
        
        # 如果目标项目存在，检查其类型
        if target_item is not None:
            target_data = target_item.data(0, Qt.ItemDataRole.UserRole)
            if target_data:
                target_type = target_data.get("type")
                
                # 定义不允许有子项目的类型
                no_child_types = ["展示页面", "文本条目", "开关条目", "数据条目", "枚举条目", "展示条目", "跳转条目"]
                
                if target_type in no_child_types:
                    # 检查是否尝试将项目拖放到这些类型下
                    # 获取拖放指示器位置
                    drop_indicator_position = self.dropIndicatorPosition()
                    
                    # 如果指示器显示为子项目（在项目下方），则不允许
                    if drop_indicator_position == QTreeWidget.DropIndicatorPosition.OnItem:
                        # 显示警告
                        item_type_name = "展示页面" if target_type == "展示页面" else "条目"
                        QMessageBox.warning(
                            self,
                            "操作不允许",
                            f"不能将项目拖放到{item_type_name}下！"
                        )
                        event.ignore()
                        return
        
        # 调用父类的拖放事件
        super().dropEvent(event)
    
    def showContextMenu(self, position):
        """显示上下文菜单"""
        item = self.itemAt(position)
        
        menu = QMenu()
        
        if item is None:
            # 空白处右键：添加页面
            add_normal_action = QAction("添加普通页面", self)
            add_normal_action.triggered.connect(lambda checked, it=None, at="add_normal": 
                                               self.contextMenuRequested.emit(it, at))
            
            add_display_action = QAction("添加展示页面", self)
            add_display_action.triggered.connect(lambda checked, it=None, at="add_display": 
                                                self.contextMenuRequested.emit(it, at))
            
            menu.addAction(add_normal_action)
            menu.addAction(add_display_action)
        else:
            # 获取项目类型
            data = item.data(0, Qt.ItemDataRole.UserRole)
            item_type = data.get("type", "普通页面") if data else "普通页面"
            
            # 项目右键：删除
            delete_action = QAction("删除", self)
            delete_action.triggered.connect(lambda checked, it=item, at="delete": 
                                           self.contextMenuRequested.emit(it, at))
            menu.addAction(delete_action)
            
            # 只有普通页面才能添加子页面和条目
            if item_type == "普通页面":
                menu.addSeparator()
                
                # 添加子页面选项
                add_child_normal_action = QAction("添加子页面（普通）", self)
                add_child_normal_action.triggered.connect(lambda checked, it=item, at="add_child_normal": 
                                                         self.contextMenuRequested.emit(it, at))
                
                add_child_display_action = QAction("添加子页面（展示）", self)
                add_child_display_action.triggered.connect(lambda checked, it=item, at="add_child_display": 
                                                          self.contextMenuRequested.emit(it, at))
                
                menu.addAction(add_child_normal_action)
                menu.addAction(add_child_display_action)
                
                menu.addSeparator()
                
                # 添加五种条目类型
                add_text_entry_action = QAction("添加文本条目", self)
                add_text_entry_action.triggered.connect(lambda checked, it=item, at="add_text_entry": 
                                                       self.contextMenuRequested.emit(it, at))
                
                add_switch_entry_action = QAction("添加开关条目", self)
                add_switch_entry_action.triggered.connect(lambda checked, it=item, at="add_switch_entry": 
                                                         self.contextMenuRequested.emit(it, at))
                
                add_data_entry_action = QAction("添加数据条目", self)
                add_data_entry_action.triggered.connect(lambda checked, it=item, at="add_data_entry": 
                                                       self.contextMenuRequested.emit(it, at))
                
                add_enum_entry_action = QAction("添加枚举条目", self)
                add_enum_entry_action.triggered.connect(lambda checked, it=item, at="add_enum_entry": 
                                                       self.contextMenuRequested.emit(it, at))
                
                add_display_entry_action = QAction("添加展示条目", self)
                add_display_entry_action.triggered.connect(lambda checked, it=item, at="add_display_entry": 
                                                          self.contextMenuRequested.emit(it, at))
                
                # 添加跳转条目
                add_goto_entry_action = QAction("添加跳转条目", self)
                add_goto_entry_action.triggered.connect(lambda checked, it=item, at="add_goto_entry": 
                                                       self.contextMenuRequested.emit(it, at))
                
                menu.addAction(add_text_entry_action)
                menu.addAction(add_switch_entry_action)
                menu.addAction(add_data_entry_action)
                menu.addAction(add_enum_entry_action)
                menu.addAction(add_display_entry_action)
                menu.addAction(add_goto_entry_action)
        
        menu.exec(self.mapToGlobal(position))


class PropertyEditor(QWidget):
    """属性编辑器组件"""
    
    propertyChanged = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.current_item = None
        self.property_widgets = {}  # 存储属性控件
        self.initUI()
    
    def initUI(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("页面属性")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 基本属性表单
        basic_group = QGroupBox("基本属性")
        basic_layout = QFormLayout()
        
        # 显示名称
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入页面显示名称")
        self.name_edit.textChanged.connect(self.onNameChanged)
        basic_layout.addRow("显示名称:", self.name_edit)
        
        # 页面类型（只读）
        self.type_label = QLabel("")
        basic_layout.addRow("页面类型:", self.type_label)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 独有属性区域（动态创建）
        self.specific_group = QGroupBox("独有属性")
        self.specific_layout = QFormLayout()
        self.specific_group.setLayout(self.specific_layout)
        layout.addWidget(self.specific_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        self.setLayout(layout)
        
        # 设置样式
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                min-width: 200px;
            }
            QLabel {
                min-width: 80px;
            }
        """)
    
    def clearSpecificProperties(self):
        """清除独有属性区域"""
        # 移除所有控件
        while self.specific_layout.rowCount() > 0:
            self.specific_layout.removeRow(0)
        
        # 清空控件字典
        self.property_widgets.clear()
        
        # 隐藏独有属性区域
        self.specific_group.setVisible(False)
    
    def setupSpecificProperties(self, item_type, properties):
        """根据项目类型设置独有属性"""
        self.clearSpecificProperties()
        
        if not properties:
            return
        
        # 根据类型创建不同的属性控件
        if item_type == "普通页面":
            self.setupNormalPageProperties(properties)
        elif item_type == "展示页面":
            self.setupDisplayPageProperties(properties)
        elif item_type == "文本条目":
            self.setupTextEntryProperties(properties)
        elif item_type == "开关条目":
            self.setupSwitchEntryProperties(properties)
        elif item_type == "数据条目":
            self.setupDataEntryProperties(properties)
        elif item_type == "枚举条目":
            self.setupEnumEntryProperties(properties)
        elif item_type == "展示条目":
            self.setupDisplayEntryProperties(properties)
        elif item_type == "跳转条目":
            self.setupGotoEntryProperties(properties)
        
        # 如果有属性控件，显示独有属性区域
        if self.specific_layout.rowCount() > 0:
            self.specific_group.setVisible(True)
    
    def setupNormalPageProperties(self, properties):
        """设置普通页面属性"""
        # 变量名
        var_name_edit = QLineEdit(properties.get("变量名", ""))
        var_name_edit.textChanged.connect(lambda text: self.onPropertyChanged("变量名", text))
        self.specific_layout.addRow("变量名:", var_name_edit)
        self.property_widgets["变量名"] = var_name_edit
    
    def setupDisplayPageProperties(self, properties):
        """设置展示页面属性"""
        # 变量名
        var_name_edit = QLineEdit(properties.get("变量名", ""))
        var_name_edit.textChanged.connect(lambda text: self.onPropertyChanged("变量名", text))
        self.specific_layout.addRow("变量名:", var_name_edit)
        self.property_widgets["变量名"] = var_name_edit
        
        # 周期
        period_edit = QLineEdit(properties.get("周期", "100"))
        period_edit.textChanged.connect(lambda text: self.onPropertyChanged("周期", text))
        self.specific_layout.addRow("周期:", period_edit)
        self.property_widgets["周期"] = period_edit
        
        # 进入回调函数
        enter_cb = QCheckBox()
        enter_cb.setChecked(properties.get("进入回调函数", False))
        enter_cb.stateChanged.connect(lambda state: self.onPropertyChanged("进入回调函数", state == Qt.CheckState.Checked.value))
        self.specific_layout.addRow("进入回调函数:", enter_cb)
        self.property_widgets["进入回调函数"] = enter_cb
        
        # 周期回调函数
        period_cb = QCheckBox()
        period_cb.setChecked(properties.get("周期回调函数", True))
        period_cb.stateChanged.connect(lambda state: self.onPropertyChanged("周期回调函数", state == Qt.CheckState.Checked.value))
        self.specific_layout.addRow("周期回调函数:", period_cb)
        self.property_widgets["周期回调函数"] = period_cb
        
        # 退出回调函数
        exit_cb = QCheckBox()
        exit_cb.setChecked(properties.get("退出回调函数", False))
        exit_cb.stateChanged.connect(lambda state: self.onPropertyChanged("退出回调函数", state == Qt.CheckState.Checked.value))
        self.specific_layout.addRow("退出回调函数:", exit_cb)
        self.property_widgets["退出回调函数"] = exit_cb
    
    def getParentPageName(self):
        """获取父页面名称"""
        if self.current_item and self.current_item.parent():
            parent_data = self.current_item.parent().data(0, Qt.ItemDataRole.UserRole)
            if parent_data:
                # First try to get the variable name, fallback to display name if not available
                var_name = parent_data.get("properties", {}).get("变量名", "")
                if var_name:
                    return var_name
                else:
                    # Fallback to converting the display name to variable format
                    return parent_data.get("name", "").lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
        return "page"
    
    def getItemIndexInParent(self):
        """获取项目在其父级中的索引"""
        if self.current_item and self.current_item.parent():
            parent = self.current_item.parent()
            for i in range(parent.childCount()):
                if parent.child(i) == self.current_item:
                    return i + 1
        elif self.current_item:
            # 如果是顶级项目，返回在树中的位置
            for i in range(self.current_item.treeWidget().topLevelItemCount()):
                if self.current_item.treeWidget().topLevelItem(i) == self.current_item:
                    return i + 1
        return 1
    
    def toggleCallbackNameVisibility(self, visible):
        """控制回调函数名输入框的可见性"""
        if hasattr(self, 'callback_name_edit'):
            self.callback_name_edit.setVisible(visible)
            # Also update the label visibility
            # Find the callback name label and field to update visibility
            for i in range(self.specific_layout.rowCount()):
                # Get the field widget for the current row
                field_widget = self.specific_layout.itemAt(i).widget() if self.specific_layout.itemAt(i) else None
                if field_widget == self.callback_name_edit:
                    # Found the row containing our callback name edit
                    # Get the label for this row and update visibility
                    label_widget = self.specific_layout.labelForField(field_widget)
                    if label_widget:
                        label_widget.setVisible(visible)
                    field_widget.setVisible(visible)
                    break
    
    def setupTextEntryProperties(self, properties):
        """设置文本条目属性"""
        # 回调函数
        callback_cb = QCheckBox()
        callback_cb.setChecked(properties.get("回调函数", False))
        callback_cb.stateChanged.connect(lambda state: self.onPropertyChanged("回调函数", state == Qt.CheckState.Checked.value))
        self.specific_layout.addRow("回调函数:", callback_cb)
        self.property_widgets["回调函数"] = callback_cb
        
        # 回调函数名（仅在勾选回调函数时显示）
        self.callback_name_edit = QLineEdit()
        callback_name = properties.get("回调函数名", "")
        if callback_name:
            self.callback_name_edit.setText(callback_name)
        else:
            # 设置默认值格式：所属页面_在页面中的序号_Item_Callback
            parent_page = self.getParentPageName()
            item_index = self.getItemIndexInParent()
            default_callback_name = f"{parent_page}_{item_index}_Item_Callback"
            self.callback_name_edit.setText(default_callback_name)
        
        self.callback_name_edit.textChanged.connect(lambda text: self.onPropertyChanged("回调函数名", text))
        self.specific_layout.addRow("回调函数名:", self.callback_name_edit)
        self.property_widgets["回调函数名"] = self.callback_name_edit
        
        # 根据回调函数复选框的状态控制回调函数名输入框的可见性
        self.toggleCallbackNameVisibility(callback_cb.isChecked())
        callback_cb.stateChanged.connect(lambda state: self.toggleCallbackNameVisibility(state == Qt.CheckState.Checked.value))
        
        # Store the checkbox reference for visibility control
        self.property_widgets["回调函数复选框"] = callback_cb
    
    def setupSwitchEntryProperties(self, properties):
        """设置开关条目属性"""
        # 变量名
        var_name_edit = QLineEdit(properties.get("变量名", ""))
        var_name_edit.textChanged.connect(lambda text: self.onPropertyChanged("变量名", text))
        self.specific_layout.addRow("变量名:", var_name_edit)
        self.property_widgets["变量名"] = var_name_edit
        
        # 初始值
        initial_value_edit = QLineEdit(properties.get("初始值", "0"))
        initial_value_edit.textChanged.connect(lambda text: self.onPropertyChanged("初始值", text))
        self.specific_layout.addRow("初始值:", initial_value_edit)
        self.property_widgets["初始值"] = initial_value_edit
        
        # 回调函数
        callback_cb = QCheckBox()
        callback_cb.setChecked(properties.get("回调函数", False))
        callback_cb.stateChanged.connect(lambda state: self.onPropertyChanged("回调函数", state == Qt.CheckState.Checked.value))
        self.specific_layout.addRow("回调函数:", callback_cb)
        self.property_widgets["回调函数"] = callback_cb
        
        # 回调函数名（仅在勾选回调函数时显示）
        self.callback_name_edit = QLineEdit()
        callback_name = properties.get("回调函数名", "")
        if callback_name:
            self.callback_name_edit.setText(callback_name)
        else:
            # 设置默认值格式：所属页面_在页面中的序号_Item_Callback
            parent_page = self.getParentPageName()
            item_index = self.getItemIndexInParent()
            default_callback_name = f"{parent_page}_{item_index}_Item_Callback"
            self.callback_name_edit.setText(default_callback_name)
        
        self.callback_name_edit.textChanged.connect(lambda text: self.onPropertyChanged("回调函数名", text))
        self.specific_layout.addRow("回调函数名:", self.callback_name_edit)
        self.property_widgets["回调函数名"] = self.callback_name_edit
        
        # 根据回调函数复选框的状态控制回调函数名输入框的可见性
        self.toggleCallbackNameVisibility(callback_cb.isChecked())
        callback_cb.stateChanged.connect(lambda state: self.toggleCallbackNameVisibility(state == Qt.CheckState.Checked.value))
        
        # Store the checkbox reference for visibility control
        self.property_widgets["回调函数复选框"] = callback_cb
    
    def setupDataEntryProperties(self, properties):
        """设置数据条目属性"""
        # 变量类型选择列表
        var_type_combo = QComboBox()
        var_types = ["uint8_val", "int8_val", "uint16_val", "int16_val", "uint32_val", "int32_val", "float_val"]
        var_type_combo.addItems(var_types)
        current_type = properties.get("变量类型", "uint8_val")
        index = var_type_combo.findText(current_type)
        if index >= 0:
            var_type_combo.setCurrentIndex(index)
        var_type_combo.currentTextChanged.connect(lambda text: self.onPropertyChanged("变量类型", text))
        self.specific_layout.addRow("变量类型:", var_type_combo)
        self.property_widgets["变量类型"] = var_type_combo
        
        # 变量名
        var_name_edit = QLineEdit(properties.get("变量名", ""))
        var_name_edit.textChanged.connect(lambda text: self.onPropertyChanged("变量名", text))
        self.specific_layout.addRow("变量名:", var_name_edit)
        self.property_widgets["变量名"] = var_name_edit
        
        # 初始值
        initial_value_edit = QLineEdit(properties.get("初始值", "0"))
        initial_value_edit.textChanged.connect(lambda text: self.onPropertyChanged("初始值", text))
        self.specific_layout.addRow("初始值:", initial_value_edit)
        self.property_widgets["初始值"] = initial_value_edit
        
        # 步进
        step_edit = QLineEdit(properties.get("步进", "1"))
        step_edit.textChanged.connect(lambda text: self.onPropertyChanged("步进", text))
        self.specific_layout.addRow("步进:", step_edit)
        self.property_widgets["步进"] = step_edit
        
        # 最小值
        min_edit = QLineEdit(properties.get("最小值", "NULL"))
        min_edit.textChanged.connect(lambda text: self.onPropertyChanged("最小值", text))
        self.specific_layout.addRow("最小值:", min_edit)
        self.property_widgets["最小值"] = min_edit
        
        # 最大值
        max_edit = QLineEdit(properties.get("最大值", "NULL"))
        max_edit.textChanged.connect(lambda text: self.onPropertyChanged("最大值", text))
        self.specific_layout.addRow("最大值:", max_edit)
        self.property_widgets["最大值"] = max_edit
        
        # 回调函数
        callback_cb = QCheckBox()
        callback_cb.setChecked(properties.get("回调函数", False))
        callback_cb.stateChanged.connect(lambda state: self.onPropertyChanged("回调函数", state == Qt.CheckState.Checked.value))
        self.specific_layout.addRow("回调函数:", callback_cb)
        self.property_widgets["回调函数"] = callback_cb
        
        # 回调函数名（仅在勾选回调函数时显示）
        self.callback_name_edit = QLineEdit()
        callback_name = properties.get("回调函数名", "")
        if callback_name:
            self.callback_name_edit.setText(callback_name)
        else:
            # 设置默认值格式：所属页面_在页面中的序号_Item_Callback
            parent_page = self.getParentPageName()
            item_index = self.getItemIndexInParent()
            default_callback_name = f"{parent_page}_{item_index}_Item_Callback"
            self.callback_name_edit.setText(default_callback_name)
        
        self.callback_name_edit.textChanged.connect(lambda text: self.onPropertyChanged("回调函数名", text))
        self.specific_layout.addRow("回调函数名:", self.callback_name_edit)
        self.property_widgets["回调函数名"] = self.callback_name_edit
        
        # 根据回调函数复选框的状态控制回调函数名输入框的可见性
        self.toggleCallbackNameVisibility(callback_cb.isChecked())
        callback_cb.stateChanged.connect(lambda state: self.toggleCallbackNameVisibility(state == Qt.CheckState.Checked.value))
        
        # Store the checkbox reference for visibility control
        self.property_widgets["回调函数复选框"] = callback_cb
    
    def setupEnumEntryProperties(self, properties):
        """设置枚举条目属性"""
        # 枚举数量
        enum_count_edit = QLineEdit(properties.get("枚举数量", "1"))
        enum_count_edit.textChanged.connect(lambda text: self.onEnumCountChanged(text))
        self.specific_layout.addRow("枚举数量:", enum_count_edit)
        self.property_widgets["枚举数量"] = enum_count_edit
        
        # 枚举字符串（动态生成）
        enum_strings = properties.get("枚举字符串", ["str1"])
        self.enum_string_widgets = []
        self.setupEnumStringFields(enum_strings)
        
        # 回调函数
        callback_cb = QCheckBox()
        callback_cb.setChecked(properties.get("回调函数", False))
        callback_cb.stateChanged.connect(lambda state: self.onPropertyChanged("回调函数", state == Qt.CheckState.Checked.value))
        self.specific_layout.addRow("回调函数:", callback_cb)
        self.property_widgets["回调函数"] = callback_cb
        
        # 回调函数名（仅在勾选回调函数时显示）
        self.callback_name_edit = QLineEdit()
        callback_name = properties.get("回调函数名", "")
        if callback_name:
            self.callback_name_edit.setText(callback_name)
        else:
            # 设置默认值格式：所属页面_在页面中的序号_Item_Callback
            parent_page = self.getParentPageName()
            item_index = self.getItemIndexInParent()
            default_callback_name = f"{parent_page}_{item_index}_Item_Callback"
            self.callback_name_edit.setText(default_callback_name)
        
        self.callback_name_edit.textChanged.connect(lambda text: self.onPropertyChanged("回调函数名", text))
        self.specific_layout.addRow("回调函数名:", self.callback_name_edit)
        self.property_widgets["回调函数名"] = self.callback_name_edit
        
        # 根据回调函数复选框的状态控制回调函数名输入框的可见性
        self.toggleCallbackNameVisibility(callback_cb.isChecked())
        callback_cb.stateChanged.connect(lambda state: self.toggleCallbackNameVisibility(state == Qt.CheckState.Checked.value))
        
        # Store the checkbox reference for visibility control
        self.property_widgets["回调函数复选框"] = callback_cb
    
    def setupEnumStringFields(self, enum_strings):
        """设置枚举字符串输入框"""
        # 移除现有的枚举字符串控件
        for widget in self.enum_string_widgets:
            if widget[0] in self.property_widgets:
                del self.property_widgets[widget[0]]
            self.specific_layout.removeRow(widget[1])
        self.enum_string_widgets.clear()
        
        # 添加新的枚举字符串输入框
        for i, enum_str in enumerate(enum_strings):
            label = QLabel(f"str{i+1}:")
            edit = QLineEdit(enum_str)
            edit.textChanged.connect(lambda text, idx=i: self.onEnumStringChanged(idx, text))
            self.specific_layout.addRow(label, edit)
            self.enum_string_widgets.append((f"枚举字符串_{i}", edit))
            self.property_widgets[f"枚举字符串_{i}"] = edit
    
    def setupDisplayEntryProperties(self, properties):
        """设置展示条目属性"""
        # 周期
        period_edit = QLineEdit(properties.get("周期", "100"))
        period_edit.textChanged.connect(lambda text: self.onPropertyChanged("周期", text))
        self.specific_layout.addRow("周期:", period_edit)
        self.property_widgets["周期"] = period_edit
        
        # 变量类型选择列表
        var_type_combo = QComboBox()
        var_types = ["uint8_val", "int8_val", "uint16_val", "int16_val", "uint32_val", "int32_val", "float_val"]
        var_type_combo.addItems(var_types)
        current_type = properties.get("变量类型", "uint8_val")
        index = var_type_combo.findText(current_type)
        if index >= 0:
            var_type_combo.setCurrentIndex(index)
        var_type_combo.currentTextChanged.connect(lambda text: self.onPropertyChanged("变量类型", text))
        self.specific_layout.addRow("变量类型:", var_type_combo)
        self.property_widgets["变量类型"] = var_type_combo
        
        # 变量名
        var_name_edit = QLineEdit(properties.get("变量名", ""))
        var_name_edit.textChanged.connect(lambda text: self.onPropertyChanged("变量名", text))
        self.specific_layout.addRow("变量名:", var_name_edit)
        self.property_widgets["变量名"] = var_name_edit
        
        # 初始值
        initial_value_edit = QLineEdit(properties.get("初始值", "0"))
        initial_value_edit.textChanged.connect(lambda text: self.onPropertyChanged("初始值", text))
        self.specific_layout.addRow("初始值:", initial_value_edit)
        self.property_widgets["初始值"] = initial_value_edit
        
        # 回调函数
        callback_cb = QCheckBox()
        callback_cb.setChecked(properties.get("回调函数", False))
        callback_cb.stateChanged.connect(lambda state: self.onPropertyChanged("回调函数", state == Qt.CheckState.Checked.value))
        self.specific_layout.addRow("回调函数:", callback_cb)
        self.property_widgets["回调函数"] = callback_cb
        
        # 回调函数名（仅在勾选回调函数时显示）
        self.callback_name_edit = QLineEdit()
        callback_name = properties.get("回调函数名", "")
        if callback_name:
            self.callback_name_edit.setText(callback_name)
        else:
            # 设置默认值格式：所属页面_在页面中的序号_Item_Callback
            parent_page = self.getParentPageName()
            item_index = self.getItemIndexInParent()
            default_callback_name = f"{parent_page}_{item_index}_Item_Callback"
            self.callback_name_edit.setText(default_callback_name)
        
        self.callback_name_edit.textChanged.connect(lambda text: self.onPropertyChanged("回调函数名", text))
        self.specific_layout.addRow("回调函数名:", self.callback_name_edit)
        self.property_widgets["回调函数名"] = self.callback_name_edit
        
        # 根据回调函数复选框的状态控制回调函数名输入框的可见性
        self.toggleCallbackNameVisibility(callback_cb.isChecked())
        callback_cb.stateChanged.connect(lambda state: self.toggleCallbackNameVisibility(state == Qt.CheckState.Checked.value))
        
        # Store the checkbox reference for visibility control
        self.property_widgets["回调函数复选框"] = callback_cb
    
    def setupGotoEntryProperties(self, properties):
        """设置跳转条目属性"""
        # 目标页面
        target_page_edit = QLineEdit(properties.get("目标页面", "NULL"))
        target_page_edit.textChanged.connect(lambda text: self.onPropertyChanged("目标页面", text))
        self.specific_layout.addRow("目标页面:", target_page_edit)
        self.property_widgets["目标页面"] = target_page_edit
    
    def onEnumCountChanged(self, text):
        """枚举数量变化时更新枚举字符串输入框"""
        try:
            count = int(text)
            if count < 1:
                count = 1
            
            # 获取当前的枚举字符串
            current_strings = []
            for i in range(len(self.enum_string_widgets)):
                if i < len(self.enum_string_widgets):
                    edit = self.enum_string_widgets[i][1]
                    current_strings.append(edit.text())
            
            # 调整数量
            if count > len(current_strings):
                # 添加新的
                for i in range(len(current_strings), count):
                    current_strings.append(f"str{i+1}")
            else:
                # 减少数量
                current_strings = current_strings[:count]
            
            # 更新属性
            self.onPropertyChanged("枚举数量", text)
            self.onPropertyChanged("枚举字符串", current_strings)
            
            # 重新生成输入框
            self.setupEnumStringFields(current_strings)
        except ValueError:
            pass
    
    def onEnumStringChanged(self, index, text):
        """枚举字符串变化时更新属性"""
        # 收集所有枚举字符串
        enum_strings = []
        for i in range(len(self.enum_string_widgets)):
            if i < len(self.enum_string_widgets):
                edit = self.enum_string_widgets[i][1]
                enum_strings.append(edit.text())
        
        self.onPropertyChanged("枚举字符串", enum_strings)
    
    def onNameChanged(self, text):
        """名称变化时更新项目"""
        if self.current_item is None:
            return
        
        new_name = text.strip()
        if not new_name:
            return
        
        # 获取当前数据
        data = self.current_item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            data["name"] = new_name
            self.current_item.setData(0, Qt.ItemDataRole.UserRole, data)
            
            # 更新显示文本
            page_type = data.get("type", "普通页面")
            self.current_item.setText(0, new_name)
            self.current_item.setText(1, page_type)
            
            # 发出信号
            self.propertyChanged.emit(data)
    
    def onPropertyChanged(self, key, value):
        """属性变化时更新项目"""
        if self.current_item is None:
            return
        
        # 更新项目属性
        if hasattr(self.current_item, 'update_property'):
            self.current_item.update_property(key, value)
        
        # 获取更新后的数据并发出信号
        data = self.current_item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            self.propertyChanged.emit(data)
    
    def setItem(self, item):
        """设置当前编辑的项目"""
        self.current_item = item
        
        if item is None:
            # 清空编辑器
            self.name_edit.setText("")
            self.type_label.setText("")
            self.name_edit.setEnabled(False)
            self.clearSpecificProperties()
        else:
            # 从项目获取数据
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data:
                self.name_edit.setText(data.get("name", ""))
                self.type_label.setText(data.get("type", ""))
                self.name_edit.setEnabled(True)
                
                # 设置独有属性
                item_type = data.get("type", "普通页面")
                properties = data.get("properties", {})
                self.setupSpecificProperties(item_type, properties)
    


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        # 初始化计数器字典
        self.item_counters = {
            "普通页面": 1,
            "展示页面": 1,
            "文本条目": 1,
            "开关条目": 1,
            "数据条目": 1,
            "枚举条目": 1,
            "展示条目": 1,
            "跳转条目": 1
        }
        # 存储导入文件的目录路径
        self.import_dir = None
        # 存储导入文件的基名（不含扩展名）
        self.import_basename = None
        # 默认编码设置
        self.encoding_setting = 'gb2312'  # 可选 'utf-8' 或 'gb2312'
        self.initUI()
    
    def initUI(self):
        """初始化UI"""
        
        self.setWindowTitle("Easy Menu Builder - 菜单配置工具")
        self.setGeometry(100, 100, 900, 600)
        
        # 创建菜单栏
        self.createMenuBar()
        
        # 创建工具栏
        self.createToolBar()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：菜单树
        self.tree_widget = MenuTreeWidget()
        self.tree_widget.itemSelected.connect(self.onItemSelected)
        self.tree_widget.contextMenuRequested.connect(self.onContextMenuRequested)
        
        # 右侧：属性编辑器
        self.property_editor = PropertyEditor()
        
        # 添加到分割器
        splitter.addWidget(self.tree_widget)
        splitter.addWidget(self.property_editor)
        
        # 设置分割器比例
        splitter.setSizes([400, 500])
        
        main_layout.addWidget(splitter)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QSplitter::handle {
                background-color: #ddd;
                width: 4px;
            }
            QSplitter::handle:hover {
                background-color: #ccc;
            }
        """)
    
    def createMenuBar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        # 导入菜单项
        import_action = QAction("导入配置", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.importConfig)
        file_menu.addAction(import_action)
        
        # 导出菜单项
        export_action = QAction("导出配置", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.exportConfig)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # 退出菜单项
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def createToolBar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)
        
        # 新建按钮（在工具栏最左侧）
        new_action = QAction("新建", self)
        new_action.setToolTip("新建配置 (Ctrl+N)")
        new_action.triggered.connect(self.newConfig)
        toolbar.addAction(new_action)
        
        # 保存按钮（在新建按钮右侧）
        save_action = QAction("保存", self)
        save_action.setToolTip("保存配置 (Ctrl+S)")
        save_action.triggered.connect(self.saveConfig)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # 导入按钮
        import_action = QAction("导入", self)
        import_action.setToolTip("导入配置 (Ctrl+I)")
        import_action.triggered.connect(self.importConfig)
        toolbar.addAction(import_action)
        
        # 导出按钮
        export_action = QAction("导出", self)
        export_action.setToolTip("导出配置 (Ctrl+E)")
        export_action.triggered.connect(self.exportConfig)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # 生成代码按钮
        generate_code_action = QAction("生成代码", self)
        generate_code_action.setToolTip("生成C语言代码")
        generate_code_action.triggered.connect(self.generateCode)
        toolbar.addAction(generate_code_action)
        
        toolbar.addSeparator()
        
        # 设置按钮
        settings_action = QAction("设置", self)
        settings_action.setToolTip("编码设置")
        settings_action.triggered.connect(self.openSettingsDialog)
        toolbar.addAction(settings_action)
        
        toolbar.addSeparator()
        
        # 添加普通页面按钮
        add_normal_action = QAction("添加普通页面", self)
        add_normal_action.setToolTip("添加普通页面")
        add_normal_action.triggered.connect(lambda: self.addMenuItem("", "普通页面", None))
        toolbar.addAction(add_normal_action)
        
        # 添加展示页面按钮
        add_display_action = QAction("添加展示页面", self)
        add_display_action.setToolTip("添加展示页面")
        add_display_action.triggered.connect(lambda: self.addMenuItem("", "展示页面", None))
        toolbar.addAction(add_display_action)
    
    def onItemSelected(self, item):
        """树形视图项目被选中"""
        self.property_editor.setItem(item)
        self.statusBar().showMessage(f"已选中: {item.text(0)}")
    
    def onContextMenuRequested(self, item, action_type):
        """处理上下文菜单请求"""
        if action_type == "add_normal":
            self.addMenuItem("", "普通页面", item)
        elif action_type == "add_display":
            self.addMenuItem("", "展示页面", item)
        elif action_type == "add_child_normal":
            self.addMenuItem("", "普通页面", item)
        elif action_type == "add_child_display":
            self.addMenuItem("", "展示页面", item)
        elif action_type == "add_text_entry":
            self.addMenuItem("", "文本条目", item)
        elif action_type == "add_switch_entry":
            self.addMenuItem("", "开关条目", item)
        elif action_type == "add_data_entry":
            self.addMenuItem("", "数据条目", item)
        elif action_type == "add_enum_entry":
            self.addMenuItem("", "枚举条目", item)
        elif action_type == "add_display_entry":
            self.addMenuItem("", "展示条目", item)
        elif action_type == "add_goto_entry":
            self.addMenuItem("", "跳转条目", item)
        elif action_type == "delete":
            self.deleteMenuItem(item)
    
    def addMenuItem(self, name, page_type, parent_item):
        """添加菜单项"""
        # 检查父项目类型：展示页面和条目不能有子项目
        if parent_item is not None:
            parent_data = parent_item.data(0, Qt.ItemDataRole.UserRole)
            if parent_data:
                parent_type = parent_data.get("type")
                # 定义不允许有子项目的类型
                no_child_types = ["展示页面", "文本条目", "开关条目", "数据条目", "枚举条目", "展示条目"]
                
                if parent_type in no_child_types:
                    item_type_name = "展示页面" if parent_type == "展示页面" else "条目"
                    QMessageBox.warning(
                        self, 
                        "操作不允许",
                        f"{item_type_name}不能包含子项目！"
                    )
                    self.statusBar().showMessage(f"错误：{item_type_name}不能包含子项目")
                    return
        
        # 根据类型生成默认名称
        if page_type == "普通页面":
            default_name = f"ordinary_page_{self.item_counters['普通页面']}"
            self.item_counters["普通页面"] += 1
        elif page_type == "展示页面":
            default_name = f"show_page_{self.item_counters['展示页面']}"
            self.item_counters["展示页面"] += 1
        elif page_type == "文本条目":
            default_name = f"text_item_{self.item_counters['文本条目']}"
            self.item_counters["文本条目"] += 1
        elif page_type == "开关条目":
            default_name = f"switch_item_{self.item_counters['开关条目']}"
            self.item_counters["开关条目"] += 1
        elif page_type == "数据条目":
            default_name = f"data_item_{self.item_counters['数据条目']}"
            self.item_counters["数据条目"] += 1
        elif page_type == "枚举条目":
            default_name = f"enum_item_{self.item_counters['枚举条目']}"
            self.item_counters["枚举条目"] += 1
        elif page_type == "展示条目":
            default_name = f"show_item_{self.item_counters['展示条目']}"
            self.item_counters["展示条目"] += 1
        elif page_type == "跳转条目":
            default_name = f"Goto_Item_{self.item_counters['跳转条目']}"
            self.item_counters["跳转条目"] += 1
        else:
            # 如果类型未知，使用传入的名称
            default_name = name
        
        if parent_item is None:
            # 添加到根节点
            new_item = MenuItem(default_name, page_type, self.tree_widget)
        else:
            # 添加到父节点
            new_item = MenuItem(default_name, page_type, parent_item)
            parent_item.setExpanded(True)
        
        # 选中新项目
        self.tree_widget.setCurrentItem(new_item)
        self.property_editor.setItem(new_item)
        
        self.statusBar().showMessage(f"已添加: {default_name} ({page_type})")
    
    def deleteMenuItem(self, item):
        """删除菜单项"""
        if item is None:
            return
        
        # 确认对话框
        reply = QMessageBox.question(
            self, '确认删除',
            f'确定要删除 "{item.text(0)}" 吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                index = self.tree_widget.indexOfTopLevelItem(item)
                self.tree_widget.takeTopLevelItem(index)
            
            # 清空属性编辑器
            self.property_editor.setItem(None)
            
            self.statusBar().showMessage(f"已删除: {item.text(0)}")
    
    def exportConfig(self):
        """导出配置到JSON文件"""
        # 获取文件保存路径，设置默认文件名为User_Menu_Config
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出配置",
            "User_Menu_Config.json",  # 设置默认文件名
            "JSON文件 (*.json);;所有文件 (*)"
        )
        
        if not file_path:
            return
        
        # 确保文件扩展名为.json
        if not file_path.lower().endswith('.json'):
            file_path += '.json'
        
        # 构建树形结构数据
        tree_data = self.buildTreeData()
        
        try:
            # 保存JSON文件
            with open(file_path, 'w', encoding=self.encoding_setting) as f:
                json.dump(tree_data, f, ensure_ascii=False, indent=2)
            
            # 如果没有导入动作，则同时保存.c文件
            if self.import_dir is None or self.import_basename is None:
                # 获取JSON文件所在目录
                import os
                json_dir = os.path.dirname(file_path)
                json_basename = os.path.splitext(os.path.basename(file_path))[0]
                
                # 创建C文件路径
                c_file_path = os.path.join(json_dir, "Easy_Menu_User.c")
                
                # 生成C文件内容
                c_content = self.generateCFileContent(tree_data, json_basename)
                
                # 保存C文件
                with open(c_file_path, 'w', encoding=self.encoding_setting) as f:
                    f.write(c_content)
                self.statusBar().showMessage(f"配置已导出到: {file_path} 和 {c_file_path}")
                QMessageBox.information(self, "导出成功", 
                    f"配置已成功导出到:\n{file_path}\n\nC文件已保存到:\n{c_file_path}")
            else:
                # 如果有导入动作，只保存JSON文件
                self.statusBar().showMessage(f"配置已导出到: {file_path}")
                QMessageBox.information(self, "导出成功", f"配置已成功导出到:\n{file_path}")
        except Exception as e:
            self.statusBar().showMessage(f"导出失败: {str(e)}")
            QMessageBox.critical(self, "导出失败", f"导出配置时发生错误:\n{str(e)}")
    
    def importConfig(self):
        """从JSON文件导入配置"""
        # 获取文件打开路径
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "导入配置",
            "",
            "JSON文件 (*.json);;所有文件 (*)"
        )
        
        if not file_path:
            return
        
        try:
            # 读取文件
            with open(file_path, 'r', encoding=self.encoding_setting) as f:
                tree_data = json.load(f)
            
            # 确认是否清除现有数据
            if self.tree_widget.topLevelItemCount() > 0:
                reply = QMessageBox.question(
                    self, '确认导入',
                    '导入配置将清除现有数据，是否继续？',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # 清除现有数据
            self.tree_widget.clear()
            self.property_editor.setItem(None)
            
            # 重建树形结构
            self.rebuildTreeFromData(tree_data)
            
            # 重置计数器
            self.resetCounters(tree_data)
            
            # 存储导入文件信息
            import os
            self.import_dir = os.path.dirname(file_path)
            self.import_basename = os.path.splitext(os.path.basename(file_path))[0]
            
            # 检查同目录下是否有Easy_Menu_User.c文件，如果没有则创建
            c_file_path = os.path.join(self.import_dir, "Easy_Menu_User.c")
            if not os.path.exists(c_file_path):
                try:
                    with open(c_file_path, 'w', encoding=self.encoding_setting) as f:
                        f.write("/* This file is auto-generated by Easy Menu Builder */\n\n")
                        f.write("#include \"Easy_Menu.h\"\n\n")
                        f.write("/* User menu configuration will be generated here */\n")
                    self.statusBar().showMessage(f"已创建C文件: {c_file_path}")
                except Exception as e:
                    self.statusBar().showMessage(f"创建C文件失败: {str(e)}")
            
            self.statusBar().showMessage(f"配置已从 {file_path} 导入")
            QMessageBox.information(self, "导入成功", f"配置已成功从:\n{file_path}\n导入")
        except Exception as e:
            self.statusBar().showMessage(f"导入失败: {str(e)}")
            QMessageBox.critical(self, "导入失败", f"导入配置时发生错误:\n{str(e)}")
    
    def buildTreeData(self):
        """构建树形结构数据"""
        tree_data = []
        
        # 遍历所有顶级项目
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            tree_data.append(self.itemToDict(item))
        
        return tree_data
    
    def itemToDict(self, item):
        """将树形项目转换为字典"""
        # 获取项目数据
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return {}
        
        # 构建项目字典
        item_dict = {
            "name": data.get("name", ""),
            "type": data.get("type", ""),
            "properties": data.get("properties", {})
        }
        
        # 添加子项目
        children = []
        for i in range(item.childCount()):
            child_item = item.child(i)
            children.append(self.itemToDict(child_item))
        
        if children:
            item_dict["children"] = children
        
        return item_dict
    
    def rebuildTreeFromData(self, tree_data):
        """从数据重建树形结构"""
        for item_data in tree_data:
            self.createItemFromData(item_data, None)
    
    def createItemFromData(self, item_data, parent_item):
        """从数据创建树形项目"""
        name = item_data.get("name", "")
        item_type = item_data.get("type", "普通页面")
        properties = item_data.get("properties", {})
        
        # 创建项目
        if parent_item is None:
            new_item = MenuItem(name, item_type, self.tree_widget)
        else:
            new_item = MenuItem(name, item_type, parent_item)
        
        # 设置属性
        data = new_item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            # Get default properties for this item type to ensure essential properties are maintained
            default_properties = new_item._get_default_properties(item_type, name)
            
            # Merge the imported properties with default properties
            # This ensures that essential properties like "变量名" are preserved even if missing in the JSON
            merged_properties = default_properties.copy()
            merged_properties.update(properties)
            
            data["properties"] = merged_properties
            new_item.setData(0, Qt.ItemDataRole.UserRole, data)
        
        # 递归创建子项目
        children = item_data.get("children", [])
        for child_data in children:
            self.createItemFromData(child_data, new_item)
        
        # 展开父项目
        if parent_item:
            parent_item.setExpanded(True)
        
        return new_item
    
    def resetCounters(self, tree_data):
        """根据导入的数据重置计数器"""
        # 重置所有计数器为1
        self.item_counters = {
            "普通页面": 1,
            "展示页面": 1,
            "文本条目": 1,
            "开关条目": 1,
            "数据条目": 1,
            "枚举条目": 1,
            "展示条目": 1,
            "跳转条目": 1
        }
        
        # 递归遍历树形数据，更新计数器
        def update_counters(data_list):
            for item in data_list:
                item_type = item.get("type", "")
                if item_type in self.item_counters:
                    # 提取名称中的数字
                    name = item.get("name", "")
                    if item_type == "普通页面" and name.startswith("ordinary_page_"):
                        try:
                            num = int(name.split("_")[-1])
                            if num >= self.item_counters[item_type]:
                                self.item_counters[item_type] = num + 1
                        except:
                            pass
                    elif item_type == "展示页面" and name.startswith("show_page_"):
                        try:
                            num = int(name.split("_")[-1])
                            if num >= self.item_counters[item_type]:
                                self.item_counters[item_type] = num + 1
                        except:
                            pass
                    elif item_type == "文本条目" and name.startswith("text_item_"):
                        try:
                            num = int(name.split("_")[-1])
                            if num >= self.item_counters[item_type]:
                                self.item_counters[item_type] = num + 1
                        except:
                            pass
                    elif item_type == "开关条目" and name.startswith("switch_item_"):
                        try:
                            num = int(name.split("_")[-1])
                            if num >= self.item_counters[item_type]:
                                self.item_counters[item_type] = num + 1
                        except:
                            pass
                    elif item_type == "数据条目" and name.startswith("data_item_"):
                        try:
                            num = int(name.split("_")[-1])
                            if num >= self.item_counters[item_type]:
                                self.item_counters[item_type] = num + 1
                        except:
                            pass
                    elif item_type == "枚举条目" and name.startswith("enum_item_"):
                        try:
                            num = int(name.split("_")[-1])
                            if num >= self.item_counters[item_type]:
                                self.item_counters[item_type] = num + 1
                        except:
                            pass
                    elif item_type == "展示条目" and name.startswith("show_item_"):
                        try:
                            num = int(name.split("_")[-1])
                            if num >= self.item_counters[item_type]:
                                self.item_counters[item_type] = num + 1
                        except:
                            pass
                    elif item_type == "跳转条目" and name.startswith("Goto_Item_"):
                        try:
                            num = int(name.split("_")[-1])
                            if num >= self.item_counters[item_type]:
                                self.item_counters[item_type] = num + 1
                        except:
                            pass
                
                # 递归处理子项目
                children = item.get("children", [])
                if children:
                    update_counters(children)
        
        update_counters(tree_data)
    
    def generateCFileContent(self, tree_data, basename):
        """生成C文件内容"""
        c_content = f"""/* Easy Menu User Configuration File */
/* This file is auto-generated by Easy Menu Builder */
/* Configuration: {basename} */

#include "Easy_Menu.h"

/* User menu configuration will be generated here */

/* TODO: Implement actual C code generation */
/* This is a placeholder for future implementation */

"""
        return c_content
    
    def generateCode(self):
        """生成C语言代码"""
        # Check if we have imported a file and if Easy_Menu_User.c exists in the same directory
        if self.import_dir is not None and self.import_basename is not None:
            # Use the existing Easy_Menu_User.c file in the import directory
            import os
            c_file_path = os.path.join(self.import_dir, "Easy_Menu_User.c")
            
            try:
                # 构建树形结构数据
                tree_data = self.buildTreeData()
                
                # 生成C文件内容
                c_content = self.generateCFileContent(tree_data, self.import_basename)
                
                # If the C file already exists, preserve user code between /* USER CODE BEGIN */ and /* USER CODE END */
                if os.path.exists(c_file_path):
                    # Try to read with the selected encoding, fall back to alternative encodings if needed
                    old_c_content = ""
                    encodings_to_try = [self.encoding_setting]
                    if self.encoding_setting != 'gb2312':
                        encodings_to_try.append('gb2312')
                    if self.encoding_setting != 'utf-8':
                        encodings_to_try.append('utf-8')
                    
                    for enc in encodings_to_try:
                        try:
                            with open(c_file_path, 'r', encoding=enc) as f:
                                old_c_content = f.read()
                            break  # Successfully read, exit the loop
                        except UnicodeDecodeError:
                            continue  # Try the next encoding
                    
                    # If still empty, try with errors='ignore' as last resort
                    if not old_c_content:
                        with open(c_file_path, 'r', encoding=self.encoding_setting, errors='ignore') as f:
                            old_c_content = f.read()
                    
                    # Preserve user code between /* USER CODE BEGIN */ and /* USER CODE END */
                    c_content = preserve_user_code(old_c_content, c_content)
                
                # Save C file
                with open(c_file_path, 'w', encoding=self.encoding_setting) as f:
                    f.write(c_content)
                
                self.statusBar().showMessage(f"C代码已生成到: {c_file_path}")
                QMessageBox.information(self, "生成成功", f"C代码已成功生成到:\n{c_file_path}\n")
#                QMessageBox.information(self, "生成成功", f"C代码已成功生成到:\n{c_file_path}\n\n注意：保留了 /* USER CODE BEGIN */ 和 /* USER CODE END */ 之间的用户代码")
                
                # 自动保存配置文件
                self.saveConfig()
            except Exception as e:
                self.statusBar().showMessage(f"生成失败: {str(e)}")
                QMessageBox.critical(self, "生成失败", f"生成C代码时发生错误:\n{str(e)}")
        else:
            # Get file save path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "生成C代码",
                "Easy_Menu_User.c",
                "C文件 (*.c);;所有文件 (*)"
            )
            
            if not file_path:
                return
            
            try:
                # 构建树形结构数据
                tree_data = self.buildTreeData()
                
                # 生成C文件内容
                c_content = self.generateCFileContent(tree_data)
                
                # 保存C文件
                with open(file_path, 'w', encoding=self.encoding_setting) as f:
                    f.write(c_content)
                
                self.statusBar().showMessage(f"C代码已生成到: {file_path}")
                QMessageBox.information(self, "生成成功", f"C代码已成功生成到:\n{file_path}")
                
                # 自动保存配置文件
                self.saveConfig()
            except Exception as e:
                self.statusBar().showMessage(f"生成失败: {str(e)}")
                QMessageBox.critical(self, "生成失败", f"生成C代码时发生错误:\n{str(e)}")
    
    def generateCFileContent(self, tree_data, basename=None):
        """生成C文件内容"""
        # Initialize collections
        self.page_definitions = []  # 页面和条目定义
        self.enum_definitions = []  # 枚举定义
        self.item_callbacks = []    # 条目回调函数
        self.page_callbacks = []    # 页面回调函数
        self.setup_lists = {}       # 页面设置列表
        self.init_code = []         # 初始化代码
        self.variables = {}         # 占位变量
        
        # 遍历树形数据，收集信息
        self.collectCodeInfo(tree_data, None, 0)
        
        # Clean up the flag after collection is complete
        if hasattr(self, '_initialized_collections'):
            delattr(self, '_initialized_collections')
        
        # 生成代码各部分
        code_parts = []
        
        # 添加文件头注释
        if basename:
            code_parts.append(f"""/* Easy Menu User Configuration File */
/* This file is auto-generated by Easy Menu Builder */
/* Configuration: {basename} */

/* USER CODE PUBLIC BEGIN */

/* USER CODE PUBLIC END */
""")
        else:
            code_parts.append("""/* Easy Menu User Configuration File */
/* This file is auto-generated by Easy Menu Builder */

""")
        
        # 1. 占位变量部分
        code_parts.append(self.generatePlaceholderVariables())
        
        # 2. 页面、条目定义部分
        code_parts.append(self.generatePageDefinitions())
        
        # 3. 枚举列表
        code_parts.append(self.generateEnumLists())
        
        # 4. 回调函数（条目）
        code_parts.append(self.generateItemCallbacks())
        
        # 5. 回调函数（页面）
        code_parts.append(self.generatePageCallbacks())
        
        # 6. 设置列表（普通页面）
        code_parts.append(self.generateSetupLists())
        
        # 7. 系统初始化
        code_parts.append(self.generateSystemInit())
        
        # 组合所有部分
        c_content = """#include "Easy_Menu_User.h"

"""
        c_content += "\n".join(code_parts)
        
        return c_content
    
    def collectCodeInfo(self, tree_data, parent_page_var=None, indent_level=0):
        """收集代码生成所需的信息"""
        # Initialize collections only once per complete collection process
        # This ensures that collections are not reset during recursive calls
        if not hasattr(self, '_initialized_collections'):
            self._initialized_collections = True
            self.page_definitions = []  # 页面和条目定义
            self.enum_definitions = []  # 枚举定义
            self.item_callbacks = []    # 条目回调函数
            self.page_callbacks = []    # 页面回调函数
            self.setup_lists = {}       # 页面设置列表
            self.init_code = []         # 初始化代码
            self.variables = {}         # 占位变量
        
        for item_data in tree_data:
            item_type = item_data.get("type", "普通页面")
            item_name = item_data.get("name", "")
            properties = item_data.get("properties", {})
            children = item_data.get("children", [])
            
            # 生成变量名（根据参考文件格式）
            if item_type == "普通页面":
                page_var = properties.get("变量名", "")
                if not page_var:
                    # 根据参考文件格式生成变量名
                    page_var = item_name.lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
                
                # 页面定义
                page_def = {
                    "type": "Ordinary_Page",
                    "var_name": page_var,
                    "display_name": item_name,
                    "indent": indent_level,
                    "parent": parent_page_var,
                    "properties": properties,
                    "children": []
                }
                self.page_definitions.append(page_def)
                
                # 收集子项信息
                child_index = 1
                for child in children:
                    child_type = child.get("type", "")
                    child_name = child.get("name", "")
                    child_props = child.get("properties", {})
                    
                    if child_type == "普通页面":
                        # 子页面，需要生成跳转条目
                        child_page_var = child_props.get("变量名", "")
                        if not child_page_var:
                            child_page_var = child_name.lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
                        
                        # 生成跳转条目变量名（根据参考文件格式）
                        item_var = f"{page_var}_{child_index}_item"
                        
                        # 添加跳转条目定义
                        self.page_definitions.append({
                            "type": "Goto_Item",
                            "var_name": item_var,
                            "display_name": child_name,
                            "indent": indent_level + 1,
                            "parent": page_var,
                            "properties": child_props,
                            "target_page": child_page_var
                        })
                        
                        # 记录子页面关系
                        page_def["children"].append({
                            "type": "Goto_Item",
                            "var_name": item_var,
                            "target_page": child_page_var
                        })
                        
                        child_index += 1
                    elif child_type == "跳转条目":
                        # 跳转条目
                        item_var = f"{page_var}_{child_index}_item"
                        target_page = child_props.get("目标页面", "NULL")
                        
                        self.page_definitions.append({
                            "type": "Goto_Item",
                            "var_name": item_var,
                            "display_name": child_name,
                            "indent": indent_level + 1,
                            "parent": page_var,
                            "properties": child_props,
                            "target_page": target_page
                        })
                        
                        # 记录子条目关系
                        page_def["children"].append({
                            "type": "Goto_Item",
                            "var_name": item_var,
                            "target_page": target_page
                        })
                        
                        child_index += 1
                    elif child_type == "展示页面":
                        # 展示页面作为子页面，需要生成跳转条目
                        child_page_var = child_props.get("变量名", "")
                        if not child_page_var:
                            child_page_var = child_name.lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
                        
                        # 生成跳转条目变量名（根据参考文件格式）
                        item_var = f"{page_var}_{child_index}_item"
                        
                        # 添加跳转条目定义
                        self.page_definitions.append({
                            "type": "Goto_Item",
                            "var_name": item_var,
                            "display_name": child_name,
                            "indent": indent_level + 1,
                            "parent": page_var,
                            "properties": child_props,
                            "target_page": child_page_var
                        })
                        
                        # 记录子页面关系
                        page_def["children"].append({
                            "type": "Goto_Item",
                            "var_name": item_var,
                            "target_page": child_page_var
                        })
                        
                        child_index += 1
                    else:
                        # 普通条目
                        item_var = f"{page_var}_{child_index}_item"
                        type_map = {
                            "文本条目": "Text_Item",
                            "开关条目": "Switch_Item",
                            "数据条目": "Data_Item",
                            "枚举条目": "Enum_Item",
                            "展示条目": "Show_Item"
                        }
                        item_type_name = type_map.get(child_type, "Text_Item")
                        
                        # 添加条目定义
                        self.page_definitions.append({
                            "type": item_type_name,
                            "var_name": item_var,
                            "display_name": child_name,
                            "indent": indent_level + 1,
                            "parent": page_var,
                            "properties": child_props
                        })
                        
                        # 记录子条目关系
                        page_def["children"].append({
                            "type": item_type_name,
                            "var_name": item_var
                        })
                        
                        # 收集回调函数信息（根据参考文件格式）
                        if child_props.get("回调函数"):
                            # For all entries, we need to generate the callback name to match reference format
                            # Check if a custom callback name is provided
                            custom_callback_name = child_props.get("回调函数名", "")
                            if custom_callback_name:
                                callback_name = custom_callback_name
                            else:
                                # Use the actual item variable name for callback name generation
                                # Convert the item variable name to proper format (e.g., switch_page_1_item -> Switch_Page_1_Item)
                                item_var_parts = item_var.split('_')
                                formatted_item_var = '_'.join([part.capitalize() for part in item_var_parts])
                                
                                # Generate callback name in format: ItemVariableName_Callback
                                callback_name = f"{formatted_item_var}_Callback"
                            self.item_callbacks.append({
                                "item_type": child_type,
                                "item_name": child_name,
                                "item_var": item_var,  # Add the item variable name for lookup
                                "parent_page": page_var,
                                "callback_name": callback_name,
                                "properties": child_props
                            })
                        
                        # 收集枚举定义
                        if child_type == "枚举条目":
                            enum_strings = child_props.get("枚举字符串", [])
                            if enum_strings:
                                # 生成枚举数组名称（根据参考文件格式）
                                enum_array_name = f"{item_var}_enum_str"
                                self.enum_definitions.append({
                                    "var_name": enum_array_name,
                                    "strings": enum_strings,
                                    "parent_page": page_var,
                                    "item_name": child_name,
                                    "item_var": item_var  # Add the item variable name for reference
                                })
                        
                        # 收集变量信息
                        if child_type == "开关条目":
                            data_var = child_props.get("变量名", "")
                            if data_var:
                                initial_value = child_props.get("初始值", "0")
                                self.variables[data_var] = {
                                    "type": "unsigned char",
                                    "init_value": initial_value
                                }
                        elif child_type == "数据条目":
                            data_var = child_props.get("变量名", "")
                            var_type = child_props.get("变量类型", "uint8_val")
                            if data_var:
                                type_map = {
                                    "uint8_val": "unsigned char",
                                    "int8_val": "signed char",
                                    "uint16_val": "unsigned short int",
                                    "int16_val": "signed short int",
                                    "uint32_val": "unsigned int",
                                    "int32_val": "signed int",
                                    "float_val": "float"
                                }
                                c_type = type_map.get(var_type, "unsigned char")
                                initial_value = child_props.get("初始值", "0")
                                if var_type == "float_val":
                                    # Ensure float values have 'f' suffix
                                    if not initial_value.endswith('f'):
                                        if '.' not in initial_value and initial_value.replace('-', '', 1).isdigit():
                                            initial_value += '.0f'
                                        else:
                                            initial_value += 'f'
                                self.variables[data_var] = {
                                    "type": c_type,
                                    "init_value": initial_value
                                }
                        elif child_type == "展示条目":
                            data_var = child_props.get("变量名", "")
                            var_type = child_props.get("变量类型", "uint8_val")
                            if data_var:
                                type_map = {
                                    "uint8_val": "unsigned char",
                                    "int8_val": "signed char",
                                    "uint16_val": "unsigned short int",
                                    "int16_val": "signed short int",
                                    "uint32_val": "unsigned int",
                                    "int32_val": "signed int",
                                    "float_val": "float"
                                }
                                c_type = type_map.get(var_type, "unsigned char")
                                initial_value = child_props.get("初始值", "0")
                                if var_type == "float_val":
                                    # Ensure float values have 'f' suffix
                                    if not initial_value.endswith('f'):
                                        if '.' not in initial_value and initial_value.replace('-', '', 1).isdigit():
                                            initial_value += '.0f'
                                        else:
                                            initial_value += 'f'
                                self.variables[data_var] = {
                                    "type": c_type,
                                    "init_value": initial_value
                                }
                        
                        child_index += 1
                
                # 收集设置列表信息
                if page_def["children"]:
                    self.setup_lists[page_var] = {
                        "page_var": page_var,
                        "display_name": item_name,
                        "items": page_def["children"],
                        "item_count": len(page_def["children"])
                    }
                
                # 递归处理子页面
                for child in children:
                    if child.get("type") == "普通页面":
                        self.collectCodeInfo([child], page_var, indent_level + 2)
                    elif child.get("type") == "展示页面":
                        self.collectCodeInfo([child], page_var, indent_level + 2)
            
            elif item_type == "展示页面":
                page_var = properties.get("变量名", "")
                if not page_var:
                    page_var = item_name.lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
                
                self.page_definitions.append({
                    "type": "Show_Page",
                    "var_name": page_var,
                    "display_name": item_name,
                    "indent": indent_level,
                    "parent": parent_page_var,
                    "properties": properties
                })
                
                # 收集页面回调函数信息（根据参考文件格式）
                # Convert page variable name to proper title case (each word capitalized)
                page_parts = page_var.split('_')
                formatted_page_name = '_'.join([part.capitalize() for part in page_parts])
                
                if properties.get("进入回调函数"):
                    callback_name = f"{formatted_page_name}_Enter_Callback"
                    self.page_callbacks.append({
                        "page_var": page_var,
                        "callback_type": "enter",
                        "callback_name": callback_name
                    })
                
                if properties.get("周期回调函数"):
                    callback_name = f"{formatted_page_name}_Period_Callback"
                    self.page_callbacks.append({
                        "page_var": page_var,
                        "callback_type": "period",
                        "callback_name": callback_name
                    })
                
                if properties.get("退出回调函数"):
                    callback_name = f"{formatted_page_name}_Exit_Callback"
                    self.page_callbacks.append({
                        "page_var": page_var,
                        "callback_type": "exit",
                        "callback_name": callback_name
                    })
                
                # 收集初始化代码信息
                period = properties.get("周期", "100")
                # Convert page variable name to title case for callback names
                page_parts = page_var.split('_')
                page_name_for_callback = '_'.join([part.capitalize() for part in page_parts])
                enter_callback = f"{page_name_for_callback}_Enter_Callback" if properties.get("进入回调函数") else "NULL"
                period_callback = f"{page_name_for_callback}_Period_Callback" if properties.get("周期回调函数") else "NULL"
                exit_callback = f"{page_name_for_callback}_Exit_Callback" if properties.get("退出回调函数") else "NULL"
                parent_page = parent_page_var if parent_page_var else "NULL"
                
                # 添加初始化代码
                self.init_code.append({
                    "page_var": page_var,
                    "display_name": item_name,
                    "period": period,
                    "enter_callback": enter_callback,
                    "period_callback": period_callback,
                    "exit_callback": exit_callback,
                    "parent_page": parent_page,
                    "indent": indent_level
                })
                
                # 递归处理子项目（展示页面可以有子项目吗？根据需求，展示页面不能有子项目）
                # 但为了完整性，我们仍然处理
                if children:
                    self.collectCodeInfo(children, page_var, indent_level + 1)
            else:
                # 其他类型的处理（应该不会执行到这里，因为所有类型都已处理）
                pass
        
        # Don't reset collections during recursive calls - only initialize once
    
    def generateCallbackName(self, item_type, item_name, parent_page_var):
        """生成回调函数名称"""
        # 根据参考文件.c的命名规则生成回调函数名称
        # 规则：下划线分隔，每个单词的首字母大写
        # 例如：Text_Page_2_Item_Callback, Switch_Page_1_Item_Callback
        
        # 清理名称：移除特殊字符，用下划线替换空格
        item_name_clean = item_name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
        parent_page_clean = parent_page_var.replace(' ', '_') if parent_page_var else ""
        
        # 根据条目类型确定前缀
        type_prefix_map = {
            "文本条目": "Text",
            "开关条目": "Switch",
            "数据条目": "Data",
            "枚举条目": "Enum",
            "展示条目": "Show"
        }
        
        prefix = type_prefix_map.get(item_type, "Item")
        
        # 构建回调函数名：前缀_页面名_条目名_Callback
        # 注意：参考文件中，文本条目的回调函数名是 Text_Page_2_Item_Callback
        # 其中"Page_2"是页面名，"Item"是固定标识
        # 我们需要根据实际结构调整
        
        # 对于文本条目，参考文件中的格式是：Text_Page_2_Item_Callback
        # 其中"Page_2"来自页面名，"Item"是固定标识
        if item_type == "文本条目":
            # 文本条目的回调函数名格式：Text_页面名_条目名_Callback
            # 但参考文件中是 Text_Page_2_Item_Callback，其中"Page_2"是页面名
            # 我们需要从parent_page_var中提取页面名
            if parent_page_clean:
                # 将页面名转换为首字母大写的格式
                page_parts = parent_page_clean.split('_')
                page_name_formatted = '_'.join([part.capitalize() for part in page_parts])
                
                # 将条目名转换为首字母大写的格式
                item_parts = item_name_clean.split('_')
                item_name_formatted = '_'.join([part.capitalize() for part in item_parts])
                
                # 简化文本条目回调函数名 to match reference format
                return f"Text_{page_name_formatted}_{item_name_formatted}_Callback"
            else:
                return f"Text_{item_name_clean.capitalize()}_Callback"
        else:
            # 其他类型的回调函数名格式：前缀_页面名_条目名_Callback
            if parent_page_clean:
                # 将页面名转换为首字母大写的格式
                page_parts = parent_page_clean.split('_')
                page_name_formatted = '_'.join([part.capitalize() for part in page_parts])
                
                # 将条目名转换为首字母大写的格式
                item_parts = item_name_clean.split('_')
                item_name_formatted = '_'.join([part.capitalize() for part in item_parts])
                
                return f"{prefix}_{page_name_formatted}_{item_name_formatted}_Callback"
            else:
                return f"{prefix}_{item_name_clean.capitalize()}_Callback"
    
    def generatePlaceholderVariables(self):
        """生成占位变量部分"""
        code_lines = ["/* ================================================================= 占位变量 ================================================================= */"]
        code_lines.append("struct {")
        
        # 使用动态收集的变量
        for var_name, var_info in self.variables.items():
            var_type = var_info.get("type", "unsigned char")
            code_lines.append(f"    {var_type} {var_name};")
        
        code_lines.append("} Easy_Menu_Ui_Data = {")
        
        # 添加变量初始化
        for var_name, var_info in self.variables.items():
            init_value = var_info.get("init_value", "0")
            code_lines.append(f"    .{var_name} = {init_value},")
        
        code_lines.append("};")
        
        return "\n".join(code_lines)
    
    def generatePageDefinitions(self):
        """生成页面、条目定义部分"""
        if not self.page_definitions:
            return "/* ============================================================== 页面、条目定义 ============================================================== */    \n/* No page definitions */"
        
        lines = ["/* ============================================================== 页面、条目定义 ============================================================== */    "]
        
        # 按照树形结构排序：先按父页面，再按缩进级别
        # 首先构建页面树
        page_tree = {}
        for definition in self.page_definitions:
            parent = definition.get("parent")  # Don't default to "" since parent might be None
            if parent is None:
                parent = ""
            if parent not in page_tree:
                page_tree[parent] = []
            page_tree[parent].append(definition)
        
        # 递归生成树形结构
        def generate_tree(parent_var, indent_level):
            if parent_var not in page_tree:
                return []
            
            tree_lines = []
            for definition in page_tree[parent_var]:
                item_type = definition.get("type", "")
                var_name = definition.get("var_name", "")
                indent_str = "    " * indent_level
                
                if item_type and var_name:
                    tree_lines.append(f"{indent_str}{item_type} {var_name};")
                    
                    # 递归处理子页面 - handle all page types that can have children
                    if item_type in ["Ordinary_Page", "Show_Page"]:
                        # 普通页面和展示页面可能有子条目
                        child_lines = generate_tree(var_name, indent_level + 1)
                        tree_lines.extend(child_lines)
            
            return tree_lines
        
        # 从根节点开始生成（父页面为None或空字符串）
        root_lines = generate_tree("", 0)
        lines.extend(root_lines)
        
        return "\n".join(lines)
    
    def generateEnumLists(self):
        """生成枚举列表部分"""
        if not self.enum_definitions:
            return "/* ================================================================= 枚举列表 ================================================================= */\n/* No enum definitions */"
        
        lines = ["/* ================================================================= 枚举列表 ================================================================= */"]
        
        for enum_def in self.enum_definitions:
            var_name = enum_def.get("var_name", "")
            strings = enum_def.get("strings", [])
            
            if var_name and strings:
                # 生成数组定义
                lines.append(f'char *{var_name}[{len(strings)}] = {{')
                
                # 添加每个字符串
                for i, string in enumerate(strings):
                    if i < len(strings) - 1:
                        lines.append(f'    "{string}",')
                    else:
                        lines.append(f'    "{string}"')
                
                lines.append("};")
                lines.append("")  # 空行分隔
        
        return "\n".join(lines)
    
    def generateItemCallbacks(self):
        """生成回调函数（条目）部分"""
        if not self.item_callbacks:
            return "/* ============================================================== 回调函数（条目） ============================================================ */\n/* No item callbacks */"
        
        lines = ["/* ============================================================== 回调函数（条目） ============================================================ */"]
        
        for callback in self.item_callbacks:
            item_type = callback.get("item_type", "")
            callback_name = callback.get("callback_name", "")
            properties = callback.get("properties", {})
            
            if not callback_name:
                continue
            
            # 根据条目类型生成不同的函数签名
            if item_type == "开关条目":
                lines.append(f"void {callback_name}(unsigned char data)")
                lines.append("{")
                lines.append("    /* USER CODE BEGIN */")
                lines.append("")
                lines.append("    /* USER CODE END */")
                lines.append("}")
                lines.append("")
            
            elif item_type == "数据条目":
                var_type = properties.get("变量类型", "uint8_val")
                # 根据变量类型生成注释
                type_comment_map = {
                    "uint8_val": "// *((unsigned char*)data)",
                    "int8_val": "// *((signed char*)data)",
                    "uint16_val": "// *((unsigned short int*)data)",
                    "int16_val": "// *((signed short int*)data)",
                    "uint32_val": "// *((unsigned int*)data)",
                    "int32_val": "// *((signed int*)data)",
                    "float_val": "// *((float*)data)"
                }
                comment = type_comment_map.get(var_type, "// *((unsigned char*)data)")
                
                lines.append(f"void {callback_name}(void *data) {comment}")
                lines.append("{")
                lines.append("    /* USER CODE BEGIN */")
                lines.append("")
                lines.append("    /* USER CODE END */")
                lines.append("}")
                lines.append("")
            
            elif item_type == "枚举条目":
                lines.append(f"void {callback_name}(char *str)")
                lines.append("{")
                lines.append("    /* USER CODE BEGIN */")
                lines.append("")
                lines.append("    /* USER CODE END */")
                lines.append("}")
                lines.append("")
            
            elif item_type == "展示条目":
                lines.append(f"void {callback_name}(void)")
                lines.append("{")
                lines.append("    /* USER CODE BEGIN */")
                lines.append("")
                lines.append("    /* USER CODE END */")
                lines.append("}")
                lines.append("")
            
            elif item_type == "文本条目":
                lines.append(f"void {callback_name}(char *str)")
                lines.append("{")
                lines.append("    /* USER CODE BEGIN */")
                lines.append("")
                lines.append("    /* USER CODE END */")
                lines.append("}")
                lines.append("")
        
        return "\n".join(lines)
    
    def generatePageCallbacks(self):
        """生成回调函数（页面）部分"""
        if not self.page_callbacks:
            return "/* ============================================================== 回调函数（页面） ============================================================ */\n/* No page callbacks */"
        
        lines = ["/* ============================================================== 回调函数（页面） ============================================================ */"]
        
        # 添加私有变量部分（如果有展示页面）
        show_pages = [defn for defn in self.page_definitions if defn.get("type") == "Show_Page"]
        if show_pages:
            lines.append("/* Private variables ---------------------------------------------------------*/")
            lines.append("/* USER CODE VALUE BEGIN */")
            lines.append("/* USER CODE VALUE END */")
            lines.append("/* Private function ----------------------------------------------------------*/")
        
        # 生成每个页面回调函数
        for callback in self.page_callbacks:
            callback_name = callback.get("callback_name", "")
            callback_type = callback.get("callback_type", "")
            
            if not callback_name:
                continue
            
            # 根据回调类型生成函数
            if callback_type == "enter":
                lines.append(f"void {callback_name}(void)")
                lines.append("{")
                lines.append("    /* USER CODE BEGIN */")
                lines.append("")
                lines.append("    /* USER CODE END */")
                lines.append("}")
                lines.append("")
            elif callback_type == "period":
                lines.append(f"void {callback_name}(void* temp, Easy_Menu_Input_TYPE user_input)")
                lines.append("{")
                lines.append("    /* USER CODE BEGIN */")
                lines.append("")
                lines.append("    /* USER CODE END */")
                lines.append("}")
                lines.append("")
            elif callback_type == "exit":
                lines.append(f"void {callback_name}(void)")
                lines.append("{")
                lines.append("    /* USER CODE BEGIN */")
                lines.append("")
                lines.append("    /* USER CODE END */")
                lines.append("}")
                lines.append("")
        
        return "\n".join(lines)
    
    def generateSetupLists(self):
        """生成设置列表（普通页面）部分"""
        if not self.setup_lists:
            return "/* =========================================================== 设置列表（普通页面） =========================================================== */\n/* No setup lists */"
        
        lines = ["/* =========================================================== 设置列表（普通页面） =========================================================== */"]
        
        # 为每个普通页面生成设置列表
        for page_var, page_info in self.setup_lists.items():
            display_name = page_info.get("display_name", "")
            items = page_info.get("items", [])
            item_count = page_info.get("item_count", 0)
            
            if item_count > 0:
                # 生成数组定义
                lines.append(f"Item *{page_var}_items[{item_count}] = {{")
                
                # 添加每个条目
                for i, item in enumerate(items):
                    item_var = item.get("var_name", "")
                    if item_var:
                        if i < item_count - 1:
                            lines.append(f"    ITEM({item_var}),")
                        else:
                            lines.append(f"    ITEM({item_var})")
                
                lines.append("};")
                lines.append("")  # 空行分隔
        
        return "\n".join(lines)
    
    def newConfig(self):
        """新建配置，回到初始状态"""
        # 检查是否有未保存的更改
        if self.tree_widget.topLevelItemCount() > 0:
            reply = QMessageBox.question(
                self, '确认新建',
                '新建配置将清除现有数据，是否继续？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # 清除现有数据
        self.tree_widget.clear()
        self.property_editor.setItem(None)
        
        # 重置计数器
        self.item_counters = {
            "普通页面": 1,
            "展示页面": 1,
            "文本条目": 1,
            "开关条目": 1,
            "数据条目": 1,
            "枚举条目": 1,
            "展示条目": 1,
            "跳转条目": 1
        }
        
        # 清除导入文件信息
        self.import_dir = None
        self.import_basename = None
        
        # 更新状态栏
        self.statusBar().showMessage("已新建配置")
        
        # 显示提示信息
        QMessageBox.information(self, "新建成功", "已成功新建配置，可以开始创建新的菜单结构。")
    
    def saveConfig(self):
        """保存配置"""
        # 检查是否有数据需要保存
        if self.tree_widget.topLevelItemCount() == 0:
            QMessageBox.information(self, "无数据", "当前没有配置数据需要保存。")
            self.statusBar().showMessage("无数据可保存")
            return
        
        # 检查是否有导入文件信息
        if self.import_dir is not None and self.import_basename is not None:
            # 有导入文件，直接保存到原文件
            import os
            json_file_path = os.path.join(self.import_dir, f"{self.import_basename}.json")
            
            try:
                # 构建树形结构数据
                tree_data = self.buildTreeData()
                
                # 保存JSON文件
                with open(json_file_path, 'w', encoding=self.encoding_setting) as f:
                    json.dump(tree_data, f, ensure_ascii=False, indent=2)
                
                self.statusBar().showMessage(f"配置已保存到: {json_file_path}")
                QMessageBox.information(self, "保存成功", 
                    f"配置已成功保存到:\n{json_file_path}")
                
            except Exception as e:
                self.statusBar().showMessage(f"保存失败: {str(e)}")
                QMessageBox.critical(self, "保存失败", f"保存配置时发生错误:\n{str(e)}")
        else:
            # 没有导入文件，调用导出功能
            self.statusBar().showMessage("未导入文件，调用导出功能")
            self.exportConfig()
    

    def openSettingsDialog(self):
        """打开设置对话框，用于选择编码""" 
        dialog = QDialog(self)
        dialog.setWindowTitle("编码设置")
        dialog.setGeometry(200, 200, 300, 150)
        dialog.setModal(True)  # Ensure it's modal
        
        layout = QVBoxLayout()
        
        # 编码选择标签
        label = QLabel("请选择文件编码:")
        layout.addWidget(label)
        
        # 编码选择组合框
        combo = QComboBox()
        combo.addItem("UTF-8", "utf-8")
        combo.addItem("GB2312", "gb2312")
        
        # 设置当前选中项
        current_index = combo.findData(self.encoding_setting)
        if current_index >= 0:
            combo.setCurrentIndex(current_index)
        
        layout.addWidget(combo)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 连接按钮信号
        def accept_settings():
            self.applyEncodingSetting(combo.currentData(), dialog)
        ok_btn.clicked.connect(accept_settings)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()

    def applyEncodingSetting(self, encoding, dialog):
        """应用编码设置""" 
        self.encoding_setting = encoding
        dialog.close()
        self.statusBar().showMessage(f"编码设置已更改为: {encoding}")

    def generateSystemInit(self):
        """生成系统初始化部分"""
        lines = ["/* ================================================================ 系统初始化 ================================================================ */"]
        lines.append("void Easy_Menu_Ui_Init(void)")
        lines.append("{")
        
        # 按原始顺序处理所有页面和条目初始化（保持配置顺序）
        for definition in self.page_definitions:
            item_type = definition.get("type", "")
            var_name = definition.get("var_name", "")
            display_name = definition.get("display_name", "")
            parent = definition.get("parent", "")
            properties = definition.get("properties", {})
            
            if item_type == "Show_Page":
                # 展示页面初始化
                period = properties.get("周期", "100")
                # Look up the properly formatted callback names from collected page callbacks
                enter_callback = "NULL"  # Default to NULL
                period_callback = "NULL"  # Default to NULL
                exit_callback = "NULL"  # Default to NULL
                
                # Find the properly formatted callback names
                for callback in self.page_callbacks:
                    if callback.get("page_var") == var_name:
                        callback_type = callback.get("callback_type")
                        callback_name = callback.get("callback_name", f"{var_name}_Callback")
                        if callback_type == "enter":
                            enter_callback = callback_name
                        elif callback_type == "period":
                            period_callback = callback_name
                        elif callback_type == "exit":
                            exit_callback = callback_name
                
                parent_page = f"PAGE({parent})" if parent else "NULL"
                
                lines.append(f"    Show_Page_Init({parent_page}, PAGE({var_name}), \"{display_name}\", {period}, {enter_callback}, {period_callback}, {exit_callback});")
            
            elif item_type == "Ordinary_Page":
                # 普通页面初始化
                parent_page = f"PAGE({parent})" if parent else "NULL"
                items_array = f"{var_name}_items"
                item_count = len(self.setup_lists.get(var_name, {}).get("items", [])) if var_name in self.setup_lists else 0
                
                lines.append(f"    Ordinary_Page_Init({parent_page}, PAGE({var_name}), \"{display_name}\", {items_array}, {item_count});")
            
            elif item_type == "Goto_Item":
                # 跳转条目初始化
                target_page = definition.get("target_page", "")
                if target_page and target_page != "NULL":
                    lines.append(f"        Goto_Item_Init(PAGE({parent}), ITEM({var_name}), \"{display_name}\", PAGE({target_page}));")
                else:
                    # 当目标页面为 NULL 时，应使用 NULL 而不是 PAGE(NULL)
                    lines.append(f"        Goto_Item_Init(PAGE({parent}), ITEM({var_name}), \"{display_name}\", NULL);")
            
            elif item_type == "Text_Item":
                # 文本条目初始化
                callback_name = None
                # 检查是否有回调函数
                for callback in self.item_callbacks:
                    if callback.get("parent_page") == parent and callback.get("item_var") == var_name:
                        callback_name = callback.get("callback_name")
                        break
                    
                callback = callback_name if callback_name else "NULL"
                lines.append(f"        Text_Item_Init(PAGE({parent}), ITEM({var_name}), \"{display_name}\", {callback});")
            
            elif item_type == "Switch_Item":
                # 开关条目初始化
                data_var = properties.get("变量名", "")
                callback_name = None
                # 检查是否有回调函数
                for callback in self.item_callbacks:
                    if callback.get("parent_page") == parent and callback.get("item_var") == var_name:
                        callback_name = callback.get("callback_name")
                        break
                    
                callback = callback_name if callback_name else "NULL"
                if data_var:
                    lines.append(f"        Switch_Item_Init(PAGE({parent}), ITEM({var_name}), \"{display_name}\", &Easy_Menu_Ui_Data.{data_var}, {callback});")
            
            elif item_type == "Data_Item":
                # 数据条目初始化
                data_var = properties.get("变量名", "")
                var_type = properties.get("变量类型", "uint8_val")
                step = properties.get("步进", "1")
                min_val = properties.get("最小值", "NULL")
                max_val = properties.get("最大值", "NULL")
                callback_name = None
                    
                # 检查是否有回调函数
                for callback in self.item_callbacks:
                    if callback.get("parent_page") == parent and callback.get("item_var") == var_name:
                        callback_name = callback.get("callback_name")
                        break
                    
                # 映射变量类型到Easy_Menu类型
                type_map = {
                    "uint8_val": "UNSIGNED_CHAR",
                    "int8_val": "SIGNED_CHAR",
                    "uint16_val": "UNSIGNED_SHORT_INT",
                    "int16_val": "SIGNED_SHORT_INT",
                    "uint32_val": "UNSIGNED_INT",
                    "int32_val": "SIGNED_INT",
                    "float_val": "FLOAT"
                }
                easy_menu_type = type_map.get(var_type, "UNSIGNED_CHAR")
                    
                callback = callback_name if callback_name else "NULL"
                if data_var:
                    # Format the min/max values according to reference file format
                    formatted_min_val = f"{easy_menu_type}_VAL({min_val})" if min_val != "NULL" else f"{easy_menu_type}_VAL(0)"
                    formatted_max_val = f"{easy_menu_type}_VAL({max_val})" if max_val != "NULL" else f"{easy_menu_type}_VAL(0)"
                    # Check if min/max values are set to determine enable flags
                    min_enable_flag = 1 if min_val != "NULL" else 0
                    max_enable_flag = 1 if max_val != "NULL" else 0
                    lines.append(f"        Data_Item_Init(PAGE({parent}), ITEM({var_name}), \"{display_name}\", {easy_menu_type}, &Easy_Menu_Ui_Data.{data_var}, {easy_menu_type}_VAL({step}), 1, {formatted_min_val}, {min_enable_flag}, {formatted_max_val}, {max_enable_flag}, {callback});")
            
            elif item_type == "Enum_Item":
                # 枚举条目初始化
                enum_count = properties.get("枚举数量", "1")
                enum_strings = properties.get("枚举字符串", [])
                callback_name = None
                    
                # 检查是否有回调函数
                for callback in self.item_callbacks:
                    if callback.get("parent_page") == parent and callback.get("item_var") == var_name:
                        callback_name = callback.get("callback_name")
                        break
                    
                # 查找对应的枚举数组
                enum_array_name = None
                for enum_def in self.enum_definitions:
                    if var_name in enum_def.get("var_name", ""):
                        enum_array_name = enum_def.get("var_name")
                        break
                    
                if enum_array_name:
                    callback = callback_name if callback_name else "NULL"
                    lines.append(f"        Enum_Item_Init(PAGE({parent}), ITEM({var_name}), \"{display_name}\", {enum_array_name}, {enum_count}, {callback});")
            
            elif item_type == "Show_Item":
                # 展示条目初始化
                period = properties.get("周期", "100")
                data_var = properties.get("变量名", "")
                var_type = properties.get("变量类型", "uint8_val")
                callback_name = None
                    
                # 检查是否有回调函数
                for callback in self.item_callbacks:
                    if callback.get("parent_page") == parent and callback.get("item_var") == var_name:
                        callback_name = callback.get("callback_name")
                        break
                    
                # 映射变量类型到Easy_Menu类型
                type_map = {
                    "uint8_val": "UNSIGNED_CHAR",
                    "int8_val": "SIGNED_CHAR",
                    "uint16_val": "UNSIGNED_SHORT_INT",
                    "int16_val": "SIGNED_SHORT_INT",
                    "uint32_val": "UNSIGNED_INT",
                    "int32_val": "SIGNED_INT",
                    "float_val": "FLOAT"
                }
                easy_menu_type = type_map.get(var_type, "UNSIGNED_CHAR")
                    
                callback = callback_name if callback_name else "NULL"
                if data_var:
                    lines.append(f"        Show_Item_Init(PAGE({parent}), ITEM({var_name}), \"{display_name}\", {easy_menu_type}, &Easy_Menu_Ui_Data.{data_var}, {period}, {callback});")
            
        
        # 获取第一个页面变量作为首页
        first_page_var = None
        for definition in self.page_definitions:
            item_type = definition.get("type", "")
            if item_type in ["Show_Page", "Ordinary_Page"]:  # 查找第一个页面
                first_page_var = definition.get("var_name", "")
                if first_page_var:  # 找到第一个页面就跳出
                    break
        
        # 添加跳转到首页的语句
        if first_page_var:
            lines.append(f"    ")
            lines.append(f"    Easy_Menu_Goto_Page(PAGE({first_page_var}));")
        
        lines.append("}\n")
        
        return "\n".join(lines)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    app.setWindowIcon(QIcon("图标.png"))  # 使用.ico文件
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
