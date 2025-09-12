from typing import Optional
from ..models.menu_config_model import MenuConfigModel
from ..models.menu_item_model import MenuItemModel, MenuItemType
from ..utils.json_serializer import JsonSerializer


class FileController:
    def __init__(self):
        self.current_file_path: Optional[str] = None
        self.config = MenuConfigModel()

    def new_file(self):
        """创建新文件"""
        from ..models.menu_item_model import MenuItemModel, MenuItemType
        root_item = MenuItemModel("Main", MenuItemType.NORMAL)
        
        self.config = MenuConfigModel()
        self.config.set_root_item(root_item)
        
        self.current_file_path = None

    def save_file(self, file_path: Optional[str] = None) -> bool:
        """保存文件"""
        path = file_path or self.current_file_path
        if not path:
            return False
            
        try:
            JsonSerializer.save_config_to_file(self.config, path)
            self.current_file_path = path
            return True
        except Exception as e:
            print(f"保存文件时出错: {e}")
            return False

    def load_file(self, file_path: str) -> Optional[MenuConfigModel]:
        """加载文件"""
        try:
            self.config = JsonSerializer.load_config_from_file(file_path)
            self.current_file_path = file_path
            return self.config
        except Exception as e:
            print(f"加载文件时出错: {e}")
            return None

    def get_current_config(self) -> MenuConfigModel:
        """获取当前配置"""
        return self.config

    def set_config(self, config: MenuConfigModel):
        """设置配置"""
        self.config = config