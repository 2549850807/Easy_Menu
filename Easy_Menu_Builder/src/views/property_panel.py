from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                             QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox, 
                             QLabel, QGroupBox, QTextEdit)
from PyQt6.QtCore import QTimer, pyqtSignal
from ..controllers.menu_controller import MenuController
from ..models.menu_item_model import MenuItemModel, MenuItemType, DataType


class PropertyPanel(QWidget):
    properties_changed = pyqtSignal()  # 属性更改信号

    def __init__(self, controller: MenuController):
        super().__init__()
        self.controller = controller
        self.current_item: MenuItemModel = None
        self.init_ui()
        
        # 创建自动保存定时器
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setSingleShot(True)
        self.auto_save_timer.timeout.connect(self.save_properties)
        
        # 创建控件变化监听器
        self.control_change_listeners = []

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('属性面板')
        
        layout = QVBoxLayout(self)
        
        # 标题
        self.title_label = QLabel('请选择一个菜单项')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)
        
        # 属性表单
        self.form_group = QGroupBox('属性')
        self.form_layout = QFormLayout(self.form_group)
        layout.addWidget(self.form_group)
        
        # 变量定义区域
        self.variables_group = QGroupBox('变量定义')
        self.variables_layout = QVBoxLayout(self.variables_group)
        self.variables_text = QTextEdit()
        self.variables_text.textChanged.connect(self.on_variables_changed)
        self.variables_layout.addWidget(self.variables_text)
        layout.addWidget(self.variables_group)
        
        # 回调函数区域
        self.callbacks_group = QGroupBox('回调函数')
        self.callbacks_layout = QVBoxLayout(self.callbacks_group)
        self.callbacks_text = QTextEdit()
        self.callbacks_text.textChanged.connect(self.on_callbacks_changed)
        self.callbacks_layout.addWidget(self.callbacks_text)
        layout.addWidget(self.callbacks_group)
        
        # 注意：删除了保存按钮
        
        # 初始状态
        self.form_group.setVisible(False)
        self.variables_group.setVisible(False)
        self.callbacks_group.setVisible(False)

    def set_controller(self, controller: MenuController):
        """设置控制器"""
        self.controller = controller

    def set_current_item(self, item: MenuItemModel):
        """设置当前菜单项"""
        self.current_item = item
        self.update_property_panel()

    def update_property_panel(self):
        """更新属性面板"""
        # 停止自动保存定时器，防止访问已删除的控件
        self.auto_save_timer.stop()
        
        # 清除现有控件和监听器
        for listener in self.control_change_listeners:
            listener()
        self.control_change_listeners.clear()
        
        # 清除现有控件
        for i in reversed(range(self.form_layout.rowCount())):
            self.form_layout.removeRow(i)
            
        if not self.current_item:
            self.title_label.setText('请选择一个菜单项')
            self.form_group.setVisible(False)
            self.variables_group.setVisible(False)
            self.callbacks_group.setVisible(False)
            return
            
        # 设置标题
        self.title_label.setText(f'属性 - {self.current_item.name} ({self.current_item.type.value})')
        
        # 添加通用属性
        self.name_edit = QLineEdit(self.current_item.name)
        self.name_edit.textChanged.connect(self.schedule_auto_save)
        self.form_layout.addRow('显示名称:', self.name_edit)
        
        # 为需要变量的菜单项类型添加变量名称字段
        if self.current_item.type in [MenuItemType.TOGGLE, MenuItemType.CHANGEABLE]:
            # 变量名称
            var_name = getattr(self.current_item, 'variable_name', self.current_item.name)
            self.variable_name_edit = QLineEdit(var_name)
            self.variable_name_edit.textChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('变量名称:', self.variable_name_edit)
        
        # 添加类型特定属性
        if self.current_item.type == MenuItemType.CHANGEABLE:
            # 数据类型
            self.data_type_combo = QComboBox()
            for data_type in DataType:
                self.data_type_combo.addItem(data_type.value, data_type)
            if self.current_item.data_type:
                index = self.data_type_combo.findData(self.current_item.data_type)
                if index >= 0:
                    self.data_type_combo.setCurrentIndex(index)
            self.data_type_combo.currentIndexChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('数据类型:', self.data_type_combo)
            
            # 最小值
            self.min_val_edit = QLineEdit(str(self.current_item.min_val or 0))
            self.min_val_edit.textChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('最小值:', self.min_val_edit)
            
            # 最大值
            self.max_val_edit = QLineEdit(str(self.current_item.max_val or 100))
            self.max_val_edit.textChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('最大值:', self.max_val_edit)
            
            # 步长
            self.step_val_edit = QLineEdit(str(self.current_item.step_val or 1))
            self.step_val_edit.textChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('步长:', self.step_val_edit)
            
            # 回调函数启用
            self.enable_callback_checkbox = QCheckBox()
            self.enable_callback_checkbox.setChecked(getattr(self.current_item, 'enable_callback', False))
            self.enable_callback_checkbox.stateChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('启用回调函数:', self.enable_callback_checkbox)
            
        elif self.current_item.type == MenuItemType.TOGGLE:
            # 状态
            self.state_checkbox = QCheckBox()
            self.state_checkbox.setChecked(self.current_item.state)
            self.state_checkbox.stateChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('状态:', self.state_checkbox)
            
            # 回调函数启用
            self.enable_callback_checkbox = QCheckBox()
            self.enable_callback_checkbox.setChecked(getattr(self.current_item, 'enable_callback', False))
            self.enable_callback_checkbox.stateChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('启用回调函数:', self.enable_callback_checkbox)
            
        elif self.current_item.type == MenuItemType.APPLICATION:
            # 回调函数启用
            self.enable_callback_checkbox = QCheckBox()
            # 应用菜单项默认开启回调函数
            self.enable_callback_checkbox.setChecked(getattr(self.current_item, 'enable_callback', True))
            self.enable_callback_checkbox.stateChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('启用回调函数:', self.enable_callback_checkbox)
            
        elif self.current_item.type == MenuItemType.EXHIBITION:
            # 总页数 - 使用 QLineEdit 让用户直接输入
            self.total_pages_edit = QLineEdit(str(self.current_item.total_pages))
            self.total_pages_edit.textChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('总页数:', self.total_pages_edit)
            
            # 移除回调类型选择，不再区分Page和Nav模式
            
            # 回调函数启用
            self.enable_callback_checkbox = QCheckBox()
            self.enable_callback_checkbox.setChecked(getattr(self.current_item, 'enable_callback', True))
            self.enable_callback_checkbox.stateChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('启用回调函数:', self.enable_callback_checkbox)
        
        # 显示变量和回调区域（仅对根节点且非Normal类型）
        if not self.current_item.parent and self.current_item.type != MenuItemType.NORMAL:  # 根节点且非Normal类型
            self.variables_group.setVisible(True)
            self.callbacks_group.setVisible(True)
            
            # 显示变量定义
            variables_text = ""
            for var_name, var_value in self.controller.config.get_all_variables().items():
                variables_text += f"{var_name} = {var_value}\n"
            self.variables_text.setPlainText(variables_text)
            
            # 显示回调函数
            callbacks_text = ""
            for callback_name, callback_code in self.controller.config.get_all_callbacks().items():
                callbacks_text += f"{callback_name}:\n{callback_code}\n\n"
            self.callbacks_text.setPlainText(callbacks_text)
        else:
            self.variables_group.setVisible(False)
            self.callbacks_group.setVisible(False)
        
        # 显示表单
        self.form_group.setVisible(True)

    def on_callback_type_changed(self, index):
        """回调类型更改时的处理"""
        # 不再需要此函数，因为已合并Page和Nav模式
        pass

    def on_variables_changed(self):
        """变量定义更改时的处理"""
        self.schedule_auto_save()

    def on_callbacks_changed(self):
        """回调函数更改时的处理"""
        self.schedule_auto_save()

    def schedule_auto_save(self):
        """安排自动保存"""
        # 重启定时器，延迟500ms保存
        self.auto_save_timer.start(500)

    def save_properties(self):
        """保存属性"""
        # 检查控件是否仍然存在，防止访问已删除的控件
        if not self.current_item:
            return
            
        # 更新通用属性
        if hasattr(self, 'name_edit') and self.name_edit:
            self.current_item.name = self.name_edit.text()
        
        # 更新变量名称（如果存在）
        if hasattr(self, 'variable_name_edit') and self.variable_name_edit:
            self.current_item.variable_name = self.variable_name_edit.text()
        
        # 更新类型特定属性
        if self.current_item.type == MenuItemType.CHANGEABLE:
            # 检查控件是否存在且未被删除
            if hasattr(self, 'data_type_combo') and self.data_type_combo and \
               self.data_type_combo.isVisible():
                try:
                    self.current_item.data_type = self.data_type_combo.currentData()
                except RuntimeError:
                    # 控件已被删除，忽略
                    pass
            if hasattr(self, 'min_val_edit') and self.min_val_edit and \
               self.min_val_edit.isVisible():
                try:
                    self.current_item.min_val = float(self.min_val_edit.text())
                except (ValueError, RuntimeError):
                    self.current_item.min_val = 0
            if hasattr(self, 'max_val_edit') and self.max_val_edit and \
               self.max_val_edit.isVisible():
                try:
                    self.current_item.max_val = float(self.max_val_edit.text())
                except (ValueError, RuntimeError):
                    self.current_item.max_val = 100
            if hasattr(self, 'step_val_edit') and self.step_val_edit and \
               self.step_val_edit.isVisible():
                try:
                    self.current_item.step_val = float(self.step_val_edit.text())
                except (ValueError, RuntimeError):
                    self.current_item.step_val = 1
            if hasattr(self, 'enable_callback_checkbox') and self.enable_callback_checkbox and \
               self.enable_callback_checkbox.isVisible():
                try:
                    self.current_item.enable_callback = self.enable_callback_checkbox.isChecked()
                except RuntimeError:
                    # 控件已被删除，忽略
                    pass
        elif self.current_item.type == MenuItemType.TOGGLE:
            # 检查控件是否存在且未被删除
            if hasattr(self, 'state_checkbox') and self.state_checkbox and \
               self.state_checkbox.isVisible():
                try:
                    self.current_item.state = self.state_checkbox.isChecked()
                except RuntimeError:
                    # 控件已被删除，忽略
                    pass
            if hasattr(self, 'enable_callback_checkbox') and self.enable_callback_checkbox and \
               self.enable_callback_checkbox.isVisible():
                try:
                    self.current_item.enable_callback = self.enable_callback_checkbox.isChecked()
                except RuntimeError:
                    # 控件已被删除，忽略
                    pass
        elif self.current_item.type == MenuItemType.APPLICATION:
            # 检查控件是否存在且未被删除
            if hasattr(self, 'enable_callback_checkbox') and self.enable_callback_checkbox and \
               self.enable_callback_checkbox.isVisible():
                try:
                    self.current_item.enable_callback = self.enable_callback_checkbox.isChecked()
                except RuntimeError:
                    # 控件已被删除，忽略
                    pass
        elif self.current_item.type == MenuItemType.EXHIBITION:
            # 检查控件是否存在且未被删除
            if hasattr(self, 'total_pages_edit') and self.total_pages_edit and \
               self.total_pages_edit.isVisible():
                try:
                    self.current_item.total_pages = int(self.total_pages_edit.text())
                except (ValueError, RuntimeError):
                    self.current_item.total_pages = 1
            if hasattr(self, 'enable_callback_checkbox') and self.enable_callback_checkbox and \
               self.enable_callback_checkbox.isVisible():
                try:
                    self.current_item.enable_callback = self.enable_callback_checkbox.isChecked()
                except RuntimeError:
                    # 控件已被删除，忽略
                    pass
        
        # 如果是根节点且非Normal类型，保存变量和回调
        if not self.current_item.parent and self.current_item.type != MenuItemType.NORMAL:
            # 检查控件是否存在
            if hasattr(self, 'variables_text') and self.variables_text and hasattr(self, 'callbacks_text') and self.callbacks_text:
                # 解析变量定义
                variables_text = self.variables_text.toPlainText()
                for line in variables_text.split('\n'):
                    if '=' in line:
                        parts = line.split('=')
                        if len(parts) == 2:
                            var_name = parts[0].strip()
                            var_value_str = parts[1].strip()
                            
                            # 尝试解析值类型
                            if var_value_str.lower() in ('true', 'false'):
                                var_value = var_value_str.lower() == 'true'
                            else:
                                try:
                                    # 尝试解析为数字
                                    if '.' in var_value_str:
                                        var_value = float(var_value_str)
                                    else:
                                        var_value = int(var_value_str)
                                except ValueError:
                                    # 默认为字符串
                                    var_value = var_value_str
                                    
                            self.controller.config.add_variable(var_name, var_value)
                
                # 解析回调函数
                callbacks_text = self.callbacks_text.toPlainText()
                # 简单解析，按函数名:代码的方式
                lines = callbacks_text.split('\n')
                current_callback = None
                current_code = []
                
                for line in lines:
                    if line.endswith(':'):
                        # 新的回调函数
                        if current_callback:
                            self.controller.config.add_callback(current_callback, '\n'.join(current_code))
                        current_callback = line[:-1]  # 移除冒号
                        current_code = []
                    elif line.strip():
                        current_code.append(line)
                        
                # 保存最后一个回调函数
                if current_callback:
                    self.controller.config.add_callback(current_callback, '\n'.join(current_code))
        
        # 发出属性更改信号
        self.properties_changed.emit()