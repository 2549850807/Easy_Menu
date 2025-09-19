from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                             QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox, 
                             QLabel, QGroupBox, QTextEdit)
from PyQt6.QtCore import QTimer, pyqtSignal
from ..controllers.menu_controller import MenuController
from ..models.menu_item_model import MenuItemModel, MenuItemType, DataType


class PropertyPanel(QWidget):
    properties_changed = pyqtSignal()

    def __init__(self, controller: MenuController):
        super().__init__()
        self.controller = controller
        self.current_item: MenuItemModel = None
        self.init_ui()
        
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setSingleShot(True)
        self.auto_save_timer.timeout.connect(self.save_properties)
        
        self.control_change_listeners = []

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('属性面板')
        
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel('请选择一个菜单项')
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)
        
        self.form_group = QGroupBox('属性')
        self.form_layout = QFormLayout(self.form_group)
        layout.addWidget(self.form_group)
        
        self.variables_group = QGroupBox('变量定义')
        self.variables_layout = QVBoxLayout(self.variables_group)
        self.variables_text = QTextEdit()
        self.variables_text.textChanged.connect(self.on_variables_changed)
        self.variables_layout.addWidget(self.variables_text)
        layout.addWidget(self.variables_group)
        
        self.callbacks_group = QGroupBox('回调函数')
        self.callbacks_layout = QVBoxLayout(self.callbacks_group)
        self.callbacks_text = QTextEdit()
        self.callbacks_text.textChanged.connect(self.on_callbacks_changed)
        self.callbacks_layout.addWidget(self.callbacks_text)
        layout.addWidget(self.callbacks_group)
        
        
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
        self.auto_save_timer.stop()
        
        for listener in self.control_change_listeners:
            listener()
        self.control_change_listeners.clear()
        
        for i in reversed(range(self.form_layout.rowCount())):
            self.form_layout.removeRow(i)
            
        if not self.current_item:
            self.title_label.setText('请选择一个菜单项')
            self.form_group.setVisible(False)
            self.variables_group.setVisible(False)
            self.callbacks_group.setVisible(False)
            return
            
        self.title_label.setText(f'属性 - {self.current_item.name} ({self.current_item.type.value})')
        
        self.name_edit = QLineEdit(self.current_item.name)
        self.name_edit.textChanged.connect(self.schedule_auto_save)
        self.form_layout.addRow('显示名称:', self.name_edit)
        
        if self.current_item.type in [MenuItemType.TOGGLE, MenuItemType.CHANGEABLE]:
            var_name = getattr(self.current_item, 'variable_name', self.current_item.name.lower())
            self.variable_name_edit = QLineEdit(var_name)
            self.variable_name_edit.textChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('变量名称:', self.variable_name_edit)
        
        if self.current_item.type == MenuItemType.CHANGEABLE:
            self.data_type_combo = QComboBox()
            # Changeable 菜单项只支持数值类型，不支持 bool 类型
            for data_type in DataType:
                if data_type != DataType.BOOL:  # 排除 bool 类型
                    self.data_type_combo.addItem(data_type.value, data_type)
            if self.current_item.data_type:
                index = self.data_type_combo.findData(self.current_item.data_type)
                if index >= 0:
                    self.data_type_combo.setCurrentIndex(index)
            self.data_type_combo.currentIndexChanged.connect(self.on_data_type_changed)
            self.form_layout.addRow('数据类型:', self.data_type_combo)
            
            # 正确显示float类型的默认值
            min_val_display = str(self.current_item.min_val) if self.current_item.min_val is not None else "0.0"
            self.min_val_edit = QLineEdit(min_val_display)
            self.min_val_edit.textChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('最小值:', self.min_val_edit)
            
            max_val_display = str(self.current_item.max_val) if self.current_item.max_val is not None else "100.0"
            self.max_val_edit = QLineEdit(max_val_display)
            self.max_val_edit.textChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('最大值:', self.max_val_edit)
            
            step_val_display = str(self.current_item.step_val) if self.current_item.step_val is not None else "1.0"
            self.step_val_edit = QLineEdit(step_val_display)
            self.step_val_edit.textChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('步长:', self.step_val_edit)
            
            self.enable_callback_checkbox = QCheckBox()
            self.enable_callback_checkbox.setChecked(getattr(self.current_item, 'enable_callback', False))
            self.enable_callback_checkbox.stateChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('启用回调函数:', self.enable_callback_checkbox)
            
        elif self.current_item.type == MenuItemType.TOGGLE:
            self.state_checkbox = QCheckBox()
            self.state_checkbox.setChecked(self.current_item.state)
            self.state_checkbox.stateChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('状态:', self.state_checkbox)
            
            self.enable_callback_checkbox = QCheckBox()
            self.enable_callback_checkbox.setChecked(getattr(self.current_item, 'enable_callback', False))
            self.enable_callback_checkbox.stateChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('启用回调函数:', self.enable_callback_checkbox)
            
        elif self.current_item.type == MenuItemType.APPLICATION:
            self.enable_callback_checkbox = QCheckBox()
            self.enable_callback_checkbox.setChecked(getattr(self.current_item, 'enable_callback', True))
            self.enable_callback_checkbox.stateChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('启用回调函数:', self.enable_callback_checkbox)
            
        elif self.current_item.type == MenuItemType.EXHIBITION:
            self.total_pages_edit = QLineEdit(str(self.current_item.total_pages))
            self.total_pages_edit.textChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('总页数:', self.total_pages_edit)
            
            
            self.enable_callback_checkbox = QCheckBox()
            self.enable_callback_checkbox.setChecked(getattr(self.current_item, 'enable_callback', True))
            self.enable_callback_checkbox.stateChanged.connect(self.schedule_auto_save)
            self.form_layout.addRow('启用回调函数:', self.enable_callback_checkbox)
        
        if not self.current_item.parent and self.current_item.type != MenuItemType.NORMAL:
            self.variables_group.setVisible(True)
            self.callbacks_group.setVisible(True)
            
            variables_text = ""
            for var_name, var_value in self.controller.config.get_all_variables().items():
                variables_text += f"{var_name} = {var_value}\n"
            self.variables_text.setPlainText(variables_text)
            
            callbacks_text = ""
            for callback_name, callback_code in self.controller.config.get_all_callbacks().items():
                callbacks_text += f"{callback_name}:\n{callback_code}\n\n"
            self.callbacks_text.setPlainText(callbacks_text)
        else:
            self.variables_group.setVisible(False)
            self.callbacks_group.setVisible(False)
        
        self.form_group.setVisible(True)

    def on_callback_type_changed(self, index):
        """回调类型更改时的处理"""
        pass

    def on_data_type_changed(self, index):
        """数据类型更改时的处理"""
        if not self.current_item or self.current_item.type != MenuItemType.CHANGEABLE:
            return
        
        # 获取新的数据类型
        new_data_type = self.data_type_combo.currentData()
        if new_data_type:
            self.current_item.set_data_type(new_data_type)
            
            # 更新界面显示
            self.update_changeable_values_display()
            
            # 显示数据类型范围提示
            self.show_data_type_range_info(new_data_type)
        
        # 触发自动保存
        self.schedule_auto_save()

    def show_data_type_range_info(self, data_type: DataType):
        """显示数据类型范围信息"""
        min_val, max_val = DataType.get_range(data_type)
        
        # 更新最小值和最大值输入框的提示文本
        if hasattr(self, 'min_val_edit') and self.min_val_edit:
            if DataType.is_integer_type(data_type):
                self.min_val_edit.setPlaceholderText(f"范围: {int(min_val)} ~ {int(max_val)}")
            else:
                self.min_val_edit.setPlaceholderText(f"范围: {min_val:.2e} ~ {max_val:.2e}")
        
        if hasattr(self, 'max_val_edit') and self.max_val_edit:
            if DataType.is_integer_type(data_type):
                self.max_val_edit.setPlaceholderText(f"范围: {int(min_val)} ~ {int(max_val)}")
            else:
                self.max_val_edit.setPlaceholderText(f"范围: {min_val:.2e} ~ {max_val:.2e}")

    def on_variables_changed(self):
        """变量定义更改时的处理"""
        self.schedule_auto_save()

    def on_callbacks_changed(self):
        """回调函数更改时的处理"""
        self.schedule_auto_save()

    def update_changeable_values_display(self):
        """更新可变菜单项的数值显示"""
        if not self.current_item or self.current_item.type != MenuItemType.CHANGEABLE:
            return
        
        # 更新最小值显示
        if hasattr(self, 'min_val_edit') and self.min_val_edit and \
           self.min_val_edit.isVisible() and self.current_item.min_val is not None:
            try:
                self.min_val_edit.setText(str(self.current_item.min_val))
            except RuntimeError:
                pass
        
        # 更新最大值显示
        if hasattr(self, 'max_val_edit') and self.max_val_edit and \
           self.max_val_edit.isVisible() and self.current_item.max_val is not None:
            try:
                self.max_val_edit.setText(str(self.current_item.max_val))
            except RuntimeError:
                pass
        
        # 更新步长值显示
        if hasattr(self, 'step_val_edit') and self.step_val_edit and \
           self.step_val_edit.isVisible() and self.current_item.step_val is not None:
            try:
                self.step_val_edit.setText(str(self.current_item.step_val))
            except RuntimeError:
                pass

    def schedule_auto_save(self):
        """安排自动保存"""
        self.auto_save_timer.start(500)

    def save_properties(self):
        """保存属性"""
        if not self.current_item:
            return
            
        try:
            if hasattr(self, 'name_edit') and self.name_edit and not self.name_edit.isHidden():
                self.current_item.name = self.name_edit.text()
        except RuntimeError:
            pass
        
        try:
            if hasattr(self, 'variable_name_edit') and self.variable_name_edit and not self.variable_name_edit.isHidden():
                self.current_item.variable_name = self.variable_name_edit.text()
        except RuntimeError:
            pass
        
        if self.current_item.type == MenuItemType.CHANGEABLE:
            # 保存数据类型
            if hasattr(self, 'data_type_combo') and self.data_type_combo and \
               self.data_type_combo.isVisible():
                try:
                    self.current_item.set_data_type(self.data_type_combo.currentData())
                except RuntimeError:
                    pass
            
            # 保存最小值
            if hasattr(self, 'min_val_edit') and self.min_val_edit and \
               self.min_val_edit.isVisible():
                try:
                    self.current_item.set_min_val(float(self.min_val_edit.text()))
                except (ValueError, RuntimeError):
                    self.current_item.set_min_val(0.0)
            
            # 保存最大值
            if hasattr(self, 'max_val_edit') and self.max_val_edit and \
               self.max_val_edit.isVisible():
                try:
                    self.current_item.set_max_val(float(self.max_val_edit.text()))
                except (ValueError, RuntimeError):
                    self.current_item.set_max_val(100.0)
            
            # 保存步长值
            if hasattr(self, 'step_val_edit') and self.step_val_edit and \
               self.step_val_edit.isVisible():
                try:
                    self.current_item.set_step_val(float(self.step_val_edit.text()))
                except (ValueError, RuntimeError):
                    self.current_item.set_step_val(1.0)
            
            # 更新界面显示为限制后的值
            self.update_changeable_values_display()
            
            # 保存回调设置
            if hasattr(self, 'enable_callback_checkbox') and self.enable_callback_checkbox and \
               self.enable_callback_checkbox.isVisible():
                try:
                    self.current_item.enable_callback = self.enable_callback_checkbox.isChecked()
                except RuntimeError:
                    pass
        elif self.current_item.type == MenuItemType.TOGGLE:
            if hasattr(self, 'state_checkbox') and self.state_checkbox and \
               self.state_checkbox.isVisible():
                try:
                    self.current_item.state = self.state_checkbox.isChecked()
                except RuntimeError:
                    pass
            if hasattr(self, 'enable_callback_checkbox') and self.enable_callback_checkbox and \
               self.enable_callback_checkbox.isVisible():
                try:
                    self.current_item.enable_callback = self.enable_callback_checkbox.isChecked()
                except RuntimeError:
                    pass
        elif self.current_item.type == MenuItemType.APPLICATION:
            if hasattr(self, 'enable_callback_checkbox') and self.enable_callback_checkbox and \
               self.enable_callback_checkbox.isVisible():
                try:
                    self.current_item.enable_callback = self.enable_callback_checkbox.isChecked()
                except RuntimeError:
                    pass
        elif self.current_item.type == MenuItemType.EXHIBITION:
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
                    pass
        
        if not self.current_item.parent and self.current_item.type != MenuItemType.NORMAL:
            if hasattr(self, 'variables_text') and self.variables_text and hasattr(self, 'callbacks_text') and self.callbacks_text:
                variables_text = self.variables_text.toPlainText()
                for line in variables_text.split('\n'):
                    if '=' in line:
                        parts = line.split('=')
                        if len(parts) == 2:
                            var_name = parts[0].strip()
                            var_value_str = parts[1].strip()
                            
                            if var_value_str.lower() in ('true', 'false'):
                                var_value = var_value_str.lower() == 'true'
                            else:
                                try:
                                    if '.' in var_value_str:
                                        var_value = float(var_value_str)
                                    else:
                                        var_value = int(var_value_str)
                                except ValueError:
                                    var_value = var_value_str
                                    
                            self.controller.config.add_variable(var_name, var_value)
                
                callbacks_text = self.callbacks_text.toPlainText()
                lines = callbacks_text.split('\n')
                current_callback = None
                current_code = []
                
                for line in lines:
                    if line.endswith(':'):
                        if current_callback:
                            self.controller.config.add_callback(current_callback, '\n'.join(current_code))
                        current_callback = line[:-1]
                        current_code = []
                    elif line.strip():
                        current_code.append(line)
                        
                if current_callback:
                    self.controller.config.add_callback(current_callback, '\n'.join(current_code))
        
        self.properties_changed.emit()