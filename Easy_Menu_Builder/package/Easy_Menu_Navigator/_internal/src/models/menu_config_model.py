from typing import Dict, Any, Optional
from .menu_item_model import MenuItemModel, MenuItemType


class MenuConfigModel:
    def __init__(self):
        self.root_item: Optional[MenuItemModel] = None
        self.variables: Dict[str, Any] = {}
        self.callbacks: Dict[str, str] = {}  # callback_name -> callback_code

    def set_root_item(self, item: MenuItemModel):
        """设置根菜单项"""
        self.root_item = item

    def add_variable(self, name: str, value: Any):
        """添加变量定义"""
        self.variables[name] = value

    def add_callback(self, name: str, code: str):
        """添加回调函数"""
        self.callbacks[name] = code

    def get_all_variables(self) -> Dict[str, Any]:
        """获取所有变量"""
        return self.variables.copy()

    def get_all_callbacks(self) -> Dict[str, str]:
        """获取所有回调函数"""
        return self.callbacks.copy()

    def to_dict(self) -> dict:
        """将配置转换为字典表示"""
        return {
            "root_item": self.root_item.to_dict() if self.root_item else None,
            "variables": self.variables,
            "callbacks": self.callbacks
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'MenuConfigModel':
        """从字典创建配置"""
        config = cls()
        if "root_item" in data and data["root_item"]:
            from .menu_item_model import MenuItemModel
            config.root_item = MenuItemModel.from_dict(data["root_item"])
        config.variables = data.get("variables", {}).copy()
        config.callbacks = data.get("callbacks", {}).copy()
        return config