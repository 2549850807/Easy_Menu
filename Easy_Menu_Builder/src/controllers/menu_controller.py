from typing import Optional, List
from ..models.menu_config_model import MenuConfigModel
from ..models.menu_item_model import MenuItemModel, MenuItemType
from ..utils.code_generator import CodeGenerator


class MenuController:
    def __init__(self):
        self.config = MenuConfigModel()
        self.current_item: Optional[MenuItemModel] = None
        self.clipboard_item: Optional[MenuItemModel] = None

    def create_new_menu_item(self, name: str, item_type: MenuItemType) -> MenuItemModel:
        """创建新的菜单项"""
        item = MenuItemModel(name, item_type)
        return item

    def new_file(self):
        """创建新文件"""
        # 清除当前配置
        self.config = MenuConfigModel()
        
        # 创建默认的根菜单项
        root_item = self.create_new_menu_item("Main", MenuItemType.NORMAL)
        self.config.set_root_item(root_item)
        
        # 设置当前项
        self.current_item = root_item

    def add_menu_item(self, parent: Optional[MenuItemModel], item: MenuItemModel):
        """添加菜单项到指定父项"""
        if parent is None:
            # 如果没有父项，且根项不存在，则设置为根项
            if self.config.root_item is None:
                self.config.set_root_item(item)
                self.current_item = item
            else:
                # 如果根项已存在，将新项添加为根项的子项
                self.config.root_item.add_child(item)
        else:
            parent.add_child(item)

    def remove_menu_item(self, item: MenuItemModel):
        """移除菜单项"""
        if item.parent:
            item.parent.remove_child(item)
        elif self.config.root_item == item:
            self.config.root_item = None
            self.current_item = None

    def move_menu_item_up(self, item: MenuItemModel):
        """向上移动菜单项"""
        if item.parent and item in item.parent.children:
            idx = item.parent.children.index(item)
            if idx > 0:
                item.parent.children[idx], item.parent.children[idx-1] = \
                    item.parent.children[idx-1], item.parent.children[idx]

    def move_menu_item_down(self, item: MenuItemModel):
        """向下移动菜单项"""
        if item.parent and item in item.parent.children:
            idx = item.parent.children.index(item)
            if idx < len(item.parent.children) - 1:
                item.parent.children[idx], item.parent.children[idx+1] = \
                    item.parent.children[idx+1], item.parent.children[idx]

    def copy_menu_item(self, item: MenuItemModel):
        """复制菜单项到剪贴板"""
        self.clipboard_item = item

    def paste_menu_item(self, parent: MenuItemModel) -> Optional[MenuItemModel]:
        """从剪贴板粘贴菜单项"""
        if self.clipboard_item:
            # 创建副本
            new_item = self._clone_menu_item(self.clipboard_item)
            self.add_menu_item(parent, new_item)
            return new_item
        return None

    def _clone_menu_item(self, item: MenuItemModel) -> MenuItemModel:
        """克隆菜单项及其子项"""
        cloned = MenuItemModel(item.name, item.type)
        cloned.is_locked = item.is_locked
        
        # 复制类型特定属性
        if item.type == MenuItemType.CHANGEABLE:
            cloned.data_type = item.data_type
            cloned.min_val = item.min_val
            cloned.max_val = item.max_val
            cloned.step_val = item.step_val
            cloned.enable_callback = item.enable_callback
        elif item.type == MenuItemType.TOGGLE:
            cloned.state = item.state
            cloned.enable_callback = item.enable_callback
        elif item.type == MenuItemType.APPLICATION:
            cloned.enable_callback = item.enable_callback
        elif item.type == MenuItemType.EXHIBITION:
            cloned.total_pages = item.total_pages
            cloned.callback_type = item.callback_type
            cloned.enable_callback = item.enable_callback
            
        # 递归克隆子项
        for child in item.children:
            cloned_child = self._clone_menu_item(child)
            cloned.add_child(cloned_child)
            
        return cloned

    def update_menu_item_properties(self, item: MenuItemModel, properties: dict):
        """更新菜单项属性"""
        for key, value in properties.items():
            if hasattr(item, key):
                setattr(item, key, value)

    def get_menu_structure(self) -> Optional[MenuItemModel]:
        """获取菜单结构"""
        return self.config.root_item

    def generate_c_code(self) -> str:
        """生成C代码"""
        generator = CodeGenerator(self.config)
        return generator.generate_c_code()

    def set_current_item(self, item: MenuItemModel):
        """设置当前选中的菜单项"""
        self.current_item = item