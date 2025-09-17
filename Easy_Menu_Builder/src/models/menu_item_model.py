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
    BOOL = "bool"
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

    @staticmethod
    def get_range(data_type: 'DataType') -> tuple:
        """获取数据类型的有效范围 (min_val, max_val)"""
        ranges = {
            DataType.BOOL: (0, 1),
            DataType.UINT8: (0, 255),
            DataType.UINT16: (0, 65535),
            DataType.UINT32: (0, 4294967295),
            DataType.UINT64: (0, 18446744073709551615),
            DataType.INT8: (-128, 127),
            DataType.INT16: (-32768, 32767),
            DataType.INT32: (-2147483648, 2147483647),
            DataType.INT64: (-9223372036854775808, 9223372036854775807),
            DataType.FLOAT: (-3.4028235e+38, 3.4028235e+38),
            DataType.DOUBLE: (-1.7976931348623157e+308, 1.7976931348623157e+308)
        }
        return ranges.get(data_type, (float('-inf'), float('inf')))

    @staticmethod
    def clamp_value(value: float, data_type: 'DataType') -> float:
        """将值限制在数据类型的有效范围内"""
        min_val, max_val = DataType.get_range(data_type)
        return max(min_val, min(max_val, value))

    @staticmethod
    def is_integer_type(data_type: 'DataType') -> bool:
        """判断是否为整数类型"""
        return data_type in [DataType.BOOL, DataType.UINT8, DataType.UINT16, DataType.UINT32, DataType.UINT64,
                           DataType.INT8, DataType.INT16, DataType.INT32, DataType.INT64]


class MenuItemModel:
    def __init__(self, name: str, item_type: MenuItemType):
        self.name = name
        self.type = item_type
        self.id = str(uuid.uuid4())
        self.children: List['MenuItemModel'] = []
        self.parent: Optional['MenuItemModel'] = None
        
        self.is_locked = True
        
        if item_type == MenuItemType.CHANGEABLE:
            self.data_ref: Any = None
            self.min_val: Any = 0.0  # 默认最小值为0.0
            self.max_val: Any = 100.0  # 默认最大值为100.0
            self.step_val: Any = 1.0  # 默认步长为1.0，确保float类型
            self.current_val: Any = 0.0  # 默认初始值为最小值0.0
            self.data_type: DataType = DataType.FLOAT
            self.enable_callback: bool = False
            self.variable_name: str = name.lower()
        elif item_type == MenuItemType.TOGGLE:
            self.state: bool = False
            self.state_ref: Any = None
            self.enable_callback: bool = False
            self.variable_name: str = name.lower()
        elif item_type == MenuItemType.APPLICATION:
            self.app_args: Any = None
            self.enable_callback: bool = True
        elif item_type == MenuItemType.EXHIBITION:
            self.total_pages: int = 1
            self.current_page: int = 0
            self.enable_callback: bool = True

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

    def validate_and_clamp_values(self):
        """验证并限制可变菜单项的数值范围"""
        if self.type == MenuItemType.CHANGEABLE and hasattr(self, 'data_type'):
            # 获取数据类型的有效范围
            min_range, max_range = DataType.get_range(self.data_type)
            
            # 限制最小值
            if self.min_val is not None:
                self.min_val = DataType.clamp_value(float(self.min_val), self.data_type)
                if DataType.is_integer_type(self.data_type):
                    self.min_val = int(self.min_val)
            
            # 限制最大值
            if self.max_val is not None:
                self.max_val = DataType.clamp_value(float(self.max_val), self.data_type)
                if DataType.is_integer_type(self.data_type):
                    self.max_val = int(self.max_val)
            
            # 确保最小值不大于最大值
            if self.min_val is not None and self.max_val is not None:
                if self.min_val > self.max_val:
                    self.min_val, self.max_val = self.max_val, self.min_val
            
            # 限制步长值
            if self.step_val is not None:
                if DataType.is_integer_type(self.data_type):
                    self.step_val = max(1, int(abs(self.step_val)))
                else:
                    self.step_val = max(0.01, abs(float(self.step_val)))

    def set_data_type(self, data_type: DataType):
        """设置数据类型并验证数值范围"""
        if self.type == MenuItemType.CHANGEABLE:
            self.data_type = data_type
            self.validate_and_clamp_values()

    def set_min_val(self, min_val: float):
        """设置最小值并验证范围"""
        if self.type == MenuItemType.CHANGEABLE:
            self.min_val = min_val
            self.validate_and_clamp_values()
            
            # 根据新的逻辑设置初始值
            self._update_current_val_based_on_range()

    def set_max_val(self, max_val: float):
        """设置最大值并验证范围"""
        if self.type == MenuItemType.CHANGEABLE:
            self.max_val = max_val
            self.validate_and_clamp_values()
            
            # 根据新的逻辑设置初始值
            self._update_current_val_based_on_range()

    def _update_current_val_based_on_range(self):
        """根据最小值和最大值的范围更新当前值"""
        if self.type != MenuItemType.CHANGEABLE:
            return
            
        # 如果当前值未设置，需要设置初始值
        if not hasattr(self, 'current_val') or self.current_val is None:
            if hasattr(self, 'min_val') and self.min_val is not None and self.min_val > 0:
                # 当最小值大于0时，初始值等于最小值
                self.current_val = float(self.min_val)
            elif hasattr(self, 'max_val') and self.max_val is not None and self.max_val < 0:
                # 当最大值小于0时，初始值等于最大值
                self.current_val = float(self.max_val)
            else:
                # 其他情况，初始值为0
                self.current_val = 0.0
        else:
            # 如果当前值已设置，确保在有效范围内
            if hasattr(self, 'min_val') and self.min_val is not None and self.current_val < self.min_val:
                self.current_val = self.min_val
            if hasattr(self, 'max_val') and self.max_val is not None and self.current_val > self.max_val:
                self.current_val = self.max_val

    def set_step_val(self, step_val: float):
        """设置步长值并验证范围"""
        if self.type == MenuItemType.CHANGEABLE:
            self.step_val = step_val
            self.validate_and_clamp_values()

    def to_dict(self) -> dict:
        """将菜单项转换为字典表示"""
        result = {
            "name": self.name,
            "type": self.type.value,
            "id": self.id,
            "is_locked": self.is_locked
        }
        
        if hasattr(self, 'variable_name'):
            result["variable_name"] = self.variable_name
        
        if self.type == MenuItemType.CHANGEABLE:
            result.update({
                "data_type": self.data_type.value if self.data_type else None,
                "min_val": self.min_val,
                "max_val": self.max_val,
                "step_val": self.step_val,
                "current_val": getattr(self, 'current_val', 0),
                "enable_callback": self.enable_callback
            })
        elif self.type == MenuItemType.TOGGLE:
            result.update({
                "state": self.state,
                "enable_callback": self.enable_callback
            })
        elif self.type == MenuItemType.APPLICATION:
            result["enable_callback"] = self.enable_callback
        elif self.type == MenuItemType.EXHIBITION:
            result.update({
                "total_pages": self.total_pages,
                "enable_callback": self.enable_callback
            })
            
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
            
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'MenuItemModel':
        """从字典创建菜单项"""
        item = cls(data["name"], MenuItemType(data["type"]))
        item.id = data.get("id", str(uuid.uuid4()))
        item.is_locked = data.get("is_locked", True)
        
        if "variable_name" in data:
            item.variable_name = data["variable_name"]
        
        if item.type == MenuItemType.CHANGEABLE:
            item.data_type = DataType(data.get("data_type", "float"))
            item.min_val = data.get("min_val", 0.0)  # 默认最小值为0.0
            item.max_val = data.get("max_val", 100.0)  # 默认最大值为100.0
            item.step_val = data.get("step_val", 1.0)  # 默认步长为1.0
            item.current_val = data.get("current_val", 0.0)  # 默认初始值为0.0
            item.enable_callback = data.get("enable_callback", False)
            
            # 根据范围更新初始值
            item._update_current_val_based_on_range()
        elif item.type == MenuItemType.TOGGLE:
            item.state = data.get("state", False)
            item.enable_callback = data.get("enable_callback", False)
        elif item.type == MenuItemType.APPLICATION:
            item.enable_callback = data.get("enable_callback", True)
        elif item.type == MenuItemType.EXHIBITION:
            item.total_pages = data.get("total_pages", 1)
            item.enable_callback = data.get("enable_callback", True)
            
        if "children" in data:
            for child_data in data["children"]:
                child = cls.from_dict(child_data)
                item.add_child(child)
                
        return item