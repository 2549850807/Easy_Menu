import json
from typing import Dict, Any
from ..models.menu_config_model import MenuConfigModel


class JsonSerializer:
    @staticmethod
    def serialize_config(config: MenuConfigModel) -> str:
        """将菜单配置序列化为JSON字符串"""
        return json.dumps(config.to_dict(), indent=2, ensure_ascii=False)

    @staticmethod
    def deserialize_config(json_str: str) -> MenuConfigModel:
        """从JSON字符串反序列化菜单配置"""
        data = json.loads(json_str)
        return MenuConfigModel.from_dict(data)

    @staticmethod
    def save_config_to_file(config: MenuConfigModel, file_path: str):
        """将菜单配置保存到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_config_from_file(file_path: str) -> MenuConfigModel:
        """从文件加载菜单配置"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return MenuConfigModel.from_dict(data)