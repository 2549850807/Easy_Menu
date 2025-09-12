from PyQt6.QtWidgets import (QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox, 
                             QInputDialog, QDialog, QVBoxLayout, QFormLayout, 
                             QLineEdit, QComboBox, QCheckBox, QDialogButtonBox, 
                             QSpinBox, QDoubleSpinBox)
from PyQt6.QtCore import pyqtSignal, Qt
from ..controllers.menu_controller import MenuController
from ..models.menu_item_model import MenuItemModel, MenuItemType, DataType


class MenuTreeView(QTreeWidget):
    item_selected = pyqtSignal(object)
    status_message = pyqtSignal(str)

    def __init__(self, controller: MenuController):
        super().__init__()
        self.controller = controller
        self.init_ui()
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def init_ui(self):
        """初始化界面"""
        self.setHeaderLabels(['菜单项', '类型'])
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemSelectionChanged.connect(self.on_item_selected)
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.refresh_tree()

    def set_controller(self, controller: MenuController):
        """设置控制器"""
        self.controller = controller
        self.refresh_tree()

    def refresh_tree(self):
        """刷新树视图"""
        self.clear()
        root_item = self.controller.get_menu_structure()
        if root_item:
            self.add_item_to_tree(None, root_item)
        self.expandAll()

    def add_item_to_tree(self, parent_widget, item: MenuItemModel):
        """将菜单项添加到树视图"""
        tree_item = QTreeWidgetItem([item.name, item.type.value])
        tree_item.setData(0, Qt.ItemDataRole.UserRole, item)
        
        if parent_widget:
            parent_widget.addChild(tree_item)
        else:
            self.addTopLevelItem(tree_item)
            
        for child in item.children:
            self.add_item_to_tree(tree_item, child)

    def on_item_selected(self):
        """处理项选择"""
        selected_items = self.selectedItems()
        if selected_items:
            item = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
            self.item_selected.emit(item)

    def show_context_menu(self, position):
        """显示上下文菜单"""
        menu = QMenu()
        
        add_menu = menu.addMenu('添加菜单项')
        
        add_normal_action = add_menu.addAction('普通菜单项')
        add_normal_action.triggered.connect(lambda: self.add_menu_item(MenuItemType.NORMAL))
        
        add_toggle_action = add_menu.addAction('切换菜单项')
        add_toggle_action.triggered.connect(lambda: self.add_menu_item(MenuItemType.TOGGLE))
        
        add_changeable_action = add_menu.addAction('可变菜单项')
        add_changeable_action.triggered.connect(lambda: self.add_menu_item(MenuItemType.CHANGEABLE))
        
        add_app_action = add_menu.addAction('应用菜单项')
        add_app_action.triggered.connect(lambda: self.add_menu_item(MenuItemType.APPLICATION))
        
        add_exhibition_action = add_menu.addAction('展示菜单项')
        add_exhibition_action.triggered.connect(lambda: self.add_menu_item(MenuItemType.EXHIBITION))
        
        menu.addSeparator()
        
        selected_items = self.selectedItems()
        if selected_items:
            tree_item = selected_items[0]
            menu_item = tree_item.data(0, Qt.ItemDataRole.UserRole)
            
            if menu_item.type != MenuItemType.NORMAL:
                edit_action = menu.addAction('编辑')
                edit_action.triggered.connect(self.edit_selected_item)
                
                delete_action = menu.addAction('删除')
                delete_action.triggered.connect(self.delete_selected_item)
            else:
                delete_action = menu.addAction('删除')
                delete_action.triggered.connect(self.delete_selected_item)
        else:
            edit_action = menu.addAction('编辑')
            edit_action.setEnabled(False)
            
            delete_action = menu.addAction('删除')
            delete_action.setEnabled(False)
        
        menu.addSeparator()
        
        move_up_action = menu.addAction('上移')
        move_up_action.triggered.connect(self.move_item_up)
        
        move_down_action = menu.addAction('下移')
        move_down_action.triggered.connect(self.move_item_down)
        
        menu.exec(self.viewport().mapToGlobal(position))

    def add_menu_item(self, item_type: MenuItemType):
        """添加菜单项"""
        selected_items = self.selectedItems()
        parent_item = None
        parent_model = None
        
        if selected_items:
            parent_item = selected_items[0]
            parent_model = parent_item.data(0, Qt.ItemDataRole.UserRole)
            
            if parent_model.type != MenuItemType.NORMAL:
                parent_item = parent_item.parent()
                parent_model = parent_model.parent if parent_model.parent else None
        
        name, ok = QInputDialog.getText(self, '添加菜单项', '请输入菜单项名称:')
        if not ok or not name:
            return
            
        new_item = self.controller.create_new_menu_item(name, item_type)
        
        self.controller.add_menu_item(parent_model, new_item)
        
        self.refresh_tree()
        self.status_message.emit(f'已添加菜单项: {name}')

    def edit_selected_item(self):
        """编辑选中的菜单项"""
        selected_items = self.selectedItems()
        if not selected_items:
            return
            
        tree_item = selected_items[0]
        menu_item = tree_item.data(0, Qt.ItemDataRole.UserRole)
        
        dialog = MenuItemEditDialog(menu_item, self)
        if dialog.exec():
            tree_item.setText(0, menu_item.name)
            tree_item.setText(1, menu_item.type.value)
            self.status_message.emit(f'已更新菜单项: {menu_item.name}')

    def delete_selected_item(self):
        """删除选中的菜单项"""
        selected_items = self.selectedItems()
        if not selected_items:
            return
            
        tree_item = selected_items[0]
        menu_item = tree_item.data(0, Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, '确认删除', f'确定要删除菜单项 "{menu_item.name}" 吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.controller.remove_menu_item(menu_item)
            self.refresh_tree()
            self.status_message.emit(f'已删除菜单项: {menu_item.name}')

    def move_item_up(self):
        """上移菜单项"""
        selected_items = self.selectedItems()
        if not selected_items:
            return
            
        tree_item = selected_items[0]
        menu_item = tree_item.data(0, Qt.ItemDataRole.UserRole)
        
        self.controller.move_menu_item_up(menu_item)
        self.refresh_tree()
        self.status_message.emit('菜单项已上移')

    def move_item_down(self):
        """下移菜单项"""
        selected_items = self.selectedItems()
        if not selected_items:
            return
            
        tree_item = selected_items[0]
        menu_item = tree_item.data(0, Qt.ItemDataRole.UserRole)
        
        self.controller.move_menu_item_down(menu_item)
        self.refresh_tree()
        self.status_message.emit('菜单项已下移')

    def dragMoveEvent(self, event):
        """处理拖拽移动事件"""
        super().dragMoveEvent(event)

    def dropEvent(self, event):
        """处理拖拽释放事件"""
        super().dropEvent(event)
        
        self._fix_illegal_parent_child_relationships()
        
        self.update_model_from_tree()
        self.refresh_tree()
        self.status_message.emit('菜单项已移动')

    def _fix_illegal_parent_child_relationships(self):
        """修复非法的父子关系"""
        root_tree_item = self.invisibleRootItem()
        self._check_and_fix_item(root_tree_item)

    def _check_and_fix_item(self, tree_item):
        """递归检查并修复项的非法关系"""
        for i in range(tree_item.childCount() - 1, -1, -1):
            child_tree_item = tree_item.child(i)
            child_model_item = child_tree_item.data(0, Qt.ItemDataRole.UserRole)
            
            if child_model_item and child_model_item.type != MenuItemType.NORMAL and child_tree_item.childCount() > 0:
                insert_index = i + 1
                while child_tree_item.childCount() > 0:
                    sub_child_tree_item = child_tree_item.child(child_tree_item.childCount() - 1)
                    
                    child_tree_item.removeChild(sub_child_tree_item)
                    
                    tree_item.insertChild(insert_index, sub_child_tree_item)
            
            self._check_and_fix_item(child_tree_item)
            
    def update_model_from_tree(self):
        """根据树视图更新数据模型"""
        root_item = self.controller.get_menu_structure()
        if not root_item:
            return
            
        self._rebuild_children_from_tree(root_item, self.invisibleRootItem())
        
    def _rebuild_children_from_tree(self, model_item: MenuItemModel, tree_item):
        """根据树视图项重新构建模型项的子项"""
        model_item.children.clear()
        
        for i in range(tree_item.childCount()):
            child_tree_item = tree_item.child(i)
            child_model_item = child_tree_item.data(0, Qt.ItemDataRole.UserRole)
            
            child_model_item.parent = model_item
            
            model_item.add_child(child_model_item)
            
            self._rebuild_children_from_tree(child_model_item, child_tree_item)
            
    def startDrag(self, supportedActions):
        """开始拖拽操作"""
        super().startDrag(supportedActions)


class MenuItemEditDialog(QDialog):
    def __init__(self, menu_item: MenuItemModel, parent=None):
        super().__init__(parent)
        self.menu_item = menu_item
        self.original_type = menu_item.type
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle(f'编辑菜单项 - {self.menu_item.name}')
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit(self.menu_item.name)
        form_layout.addRow('名称:', self.name_edit)
        
        self.type_combo = QComboBox()
        if self.menu_item.type != MenuItemType.NORMAL:
            for item_type in MenuItemType:
                if item_type != MenuItemType.NORMAL:
                    self.type_combo.addItem(item_type.value, item_type)
            index = self.type_combo.findData(self.menu_item.type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
            self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        else:
            self.type_combo.addItem(self.menu_item.type.value, self.menu_item.type)
            self.type_combo.setEnabled(False)
        form_layout.addRow('类型:', self.type_combo)
        
        self.type_specific_widgets = {}
        self.create_type_specific_widgets(form_layout)
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def create_type_specific_widgets(self, form_layout):
        """根据类型创建特定控件"""
        for widget in self.type_specific_widgets.values():
            form_layout.removeWidget(widget)
        self.type_specific_widgets.clear()
        
        current_type = self.type_combo.currentData() if self.type_combo.isEnabled() else self.menu_item.type
        
        if current_type == MenuItemType.CHANGEABLE:
            self.data_type_combo = QComboBox()
            for data_type in DataType:
                self.data_type_combo.addItem(data_type.value, data_type)
            if hasattr(self.menu_item, 'data_type') and self.menu_item.data_type:
                index = self.data_type_combo.findData(self.menu_item.data_type)
                if index >= 0:
                    self.data_type_combo.setCurrentIndex(index)
            form_layout.addRow('数据类型:', self.data_type_combo)
            self.type_specific_widgets['data_type'] = self.data_type_combo
            
            self.min_val_edit = QDoubleSpinBox()
            self.min_val_edit.setRange(-999999, 999999)
            self.min_val_edit.setValue(getattr(self.menu_item, 'min_val', 0) or 0)
            form_layout.addRow('最小值:', self.min_val_edit)
            self.type_specific_widgets['min_val'] = self.min_val_edit
            
            self.max_val_edit = QDoubleSpinBox()
            self.max_val_edit.setRange(-999999, 999999)
            self.max_val_edit.setValue(getattr(self.menu_item, 'max_val', 100) or 100)
            form_layout.addRow('最大值:', self.max_val_edit)
            self.type_specific_widgets['max_val'] = self.max_val_edit
            
            self.step_val_edit = QDoubleSpinBox()
            self.step_val_edit.setRange(0.001, 999999)
            self.step_val_edit.setSingleStep(0.1)
            self.step_val_edit.setValue(getattr(self.menu_item, 'step_val', 1) or 1)
            form_layout.addRow('步长:', self.step_val_edit)
            self.type_specific_widgets['step_val'] = self.step_val_edit
            
        elif current_type == MenuItemType.TOGGLE:
            self.state_checkbox = QCheckBox()
            self.state_checkbox.setChecked(getattr(self.menu_item, 'state', False))
            form_layout.addRow('状态:', self.state_checkbox)
            self.type_specific_widgets['state'] = self.state_checkbox
            
        elif current_type == MenuItemType.EXHIBITION:
            self.total_pages_spin = QSpinBox()
            self.total_pages_spin.setRange(1, 100)
            self.total_pages_spin.setValue(getattr(self.menu_item, 'total_pages', 1))
            form_layout.addRow('总页数:', self.total_pages_spin)
            self.type_specific_widgets['total_pages'] = self.total_pages_spin
            
            self.callback_type_combo = QComboBox()
            self.callback_type_combo.addItem('导航器回调', 'nav')
            self.callback_type_combo.addItem('分页回调', 'page')
            callback_type = getattr(self.menu_item, 'callback_type', 'nav')
            index = self.callback_type_combo.findData(callback_type)
            if index >= 0:
                self.callback_type_combo.setCurrentIndex(index)
            form_layout.addRow('回调类型:', self.callback_type_combo)
            self.type_specific_widgets['callback_type'] = self.callback_type_combo

    def on_type_changed(self, index):
        """类型改变时的处理"""
        form_layout = self.layout().itemAt(0).layout()
        self.create_type_specific_widgets(form_layout)

    def accept(self):
        """接受对话框"""
        self.menu_item.name = self.name_edit.text()
        
        if self.type_combo.isEnabled():
            new_type = self.type_combo.currentData()
            if new_type != self.original_type:
                self.menu_item.type = new_type
                self._reinitialize_item_properties()
        
        current_type = self.menu_item.type
        if current_type == MenuItemType.CHANGEABLE:
            self.menu_item.data_type = self.data_type_combo.currentData()
            self.menu_item.min_val = self.min_val_edit.value()
            self.menu_item.max_val = self.max_val_edit.value()
            self.menu_item.step_val = self.step_val_edit.value()
        elif current_type == MenuItemType.TOGGLE:
            self.menu_item.state = self.state_checkbox.isChecked()
        elif current_type == MenuItemType.EXHIBITION:
            self.menu_item.total_pages = self.total_pages_spin.value()
            self.menu_item.callback_type = self.callback_type_combo.currentData()
        
        super().accept()

    def _reinitialize_item_properties(self):
        """重新初始化菜单项的特定属性"""
        attrs_to_remove = ['data_ref', 'min_val', 'max_val', 'step_val', 'data_type', 
                          'state', 'state_ref', 'app_args', 'total_pages', 
                          'current_page', 'callback_type', 'enable_callback', 'variable_name']
        for attr in attrs_to_remove:
            if hasattr(self.menu_item, attr):
                delattr(self.menu_item, attr)
        
        if self.menu_item.type == MenuItemType.CHANGEABLE:
            self.menu_item.data_ref = None
            self.menu_item.min_val = None
            self.menu_item.max_val = None
            self.menu_item.step_val = None
            self.menu_item.data_type = DataType.FLOAT
            self.menu_item.enable_callback = False
            self.menu_item.variable_name = self.menu_item.name
        elif self.menu_item.type == MenuItemType.TOGGLE:
            self.menu_item.state = False
            self.menu_item.state_ref = None
            self.menu_item.enable_callback = False
            self.menu_item.variable_name = self.menu_item.name
        elif self.menu_item.type == MenuItemType.APPLICATION:
            self.menu_item.app_args = None
            self.menu_item.enable_callback = False
        elif self.menu_item.type == MenuItemType.EXHIBITION:
            self.menu_item.total_pages = 1
            self.menu_item.current_page = 0
            self.menu_item.callback_type = "nav"
            self.menu_item.enable_callback = True