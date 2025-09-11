from enum import Enum
from typing import List, Optional, Any
import uuid


class MenuItemType(Enum):
    NORMAL = "Normal"
    CHANGEABLE = "Changeable"
    TOGGLE = "Toggle"
    APPLICATION = "Application"
    EXHIBITION = "Exhibition"


class DataType(Enum):
    UINT8 = "uint8"
    UINT16 = "uint16"
    UINT32 = "uint32"
    UINT64 = "uint64"
    INT8 = "int8"
    INT16 = "int16"
    INT32 = "int32"
    INT64 = "int64"
    FLOAT = "float"
    DOUBLE = "double"


class MenuItemModel:
    def __init__(self, name: str, item_type: MenuItemType):
        self.name = name
        self.type = item_type
        self.id = str(uuid.uuid4())  # 添加唯一标识符
        self.children: List['MenuItemModel'] = []
        self.parent: Optional['MenuItemModel'] = None
        
        # Common attributes
        self.is_locked = True
        
        # Type-specific attributes
        if item_type == MenuItemType.CHANGEABLE:
            self.data_ref: Any = None
            self.min_val: Any = None
            self.max_val: Any = None
            self.step_val: Any = None
            self.data_type: DataType = DataType.FLOAT
            self.enable_callback: bool = False  # 是否启用回调函数
            self.variable_name: str = name  # 变量名称，默认与显示名称相同
        elif item_type == MenuItemType.TOGGLE:
            self.state: bool = False
            self.state_ref: Any = None
            self.enable_callback: bool = False  # 是否启用回调函数
            self.variable_name: str = name  # 变量名称，默认与显示名称相同
        elif item_type == MenuItemType.APPLICATION:
            self.app_args: Any = None
            self.enable_callback: bool = True  # 应用菜单项默认开启回调函数
        elif item_type == MenuItemType.EXHIBITION:
            self.total_pages: int = 1
            self.current_page: int = 0
            # 移除callback_type字段，不再区分Page和Nav模式
            self.enable_callback: bool = True  # 展示菜单项默认开启回调函数

    def add_child(self, child: 'MenuItemModel'):
        """添加子菜单项"""
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: 'MenuItemModel'):
        """移除子菜单项"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)

    def get_path(self) -> List[str]:
        """获取从根节点到当前节点的路径"""
        path = []
        current = self
        while current:
            path.append(current.name)
            current = current.parent
        return list(reversed(path))

    def to_dict(self) -> dict:
        """将菜单项转换为字典表示"""
        result = {
            "name": self.name,
            "type": self.type.value,
            "id": self.id,  # 添加id到字典
            "is_locked": self.is_locked
        }
        
        # 添加变量名称（如果存在）
        if hasattr(self, 'variable_name'):
            result["variable_name"] = self.variable_name
        
        if self.type == MenuItemType.CHANGEABLE:
            result.update({
                "data_type": self.data_type.value if self.data_type else None,
                "min_val": self.min_val,
                "max_val": self.max_val,
                "step_val": self.step_val,
                "enable_callback": self.enable_callback
            })
        elif self.type == MenuItemType.TOGGLE:
            result.update({
                "state": self.state,
                "enable_callback": self.enable_callback
            })
        elif self.type == MenuItemType.APPLICATION:
            result["enable_callback"] = self.enable_callback  # 应用菜单项默认开启回调函数
        elif self.type == MenuItemType.EXHIBITION:
            result.update({
                "total_pages": self.total_pages,
                "enable_callback": self.enable_callback
            })
            
        # 递归添加子菜单项
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
            
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'MenuItemModel':
        """从字典创建菜单项"""
        item = cls(data["name"], MenuItemType(data["type"]))
        item.id = data.get("id", str(uuid.uuid4()))  # 从字典读取id，如果没有则生成新的
        item.is_locked = data.get("is_locked", True)
        
        # 设置变量名称（如果存在）
        if "variable_name" in data:
            item.variable_name = data["variable_name"]
        
        if item.type == MenuItemType.CHANGEABLE:
            item.data_type = DataType(data.get("data_type", "float"))
            item.min_val = data.get("min_val")
            item.max_val = data.get("max_val")
            item.step_val = data.get("step_val")
            item.enable_callback = data.get("enable_callback", False)
        elif item.type == MenuItemType.TOGGLE:
            item.state = data.get("state", False)
            item.enable_callback = data.get("enable_callback", False)
        elif item.type == MenuItemType.APPLICATION:
            item.enable_callback = data.get("enable_callback", True)  # 应用菜单项默认开启回调函数
        elif item.type == MenuItemType.EXHIBITION:
            item.total_pages = data.get("total_pages", 1)
            # 从数据中读取enable_callback，如果没有则默认为True
            item.enable_callback = data.get("enable_callback", True)
            
        # 递归创建子菜单项
        if "children" in data:
            for child_data in data["children"]:
                child = cls.from_dict(child_data)
                item.add_child(child)
                
        return item
