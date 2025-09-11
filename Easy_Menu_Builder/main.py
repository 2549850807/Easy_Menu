#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Easy Menu Navigator - 菜单配置生成器
基于PyQt6的可视化菜单配置工具，可生成嵌入式设备C语言菜单代码
"""

import sys
import os
import traceback

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PyQt6.QtWidgets import QApplication
    from src.views.main_window import MainWindow
except ImportError as e:
    print(f"导入PyQt6失败: {e}")
    print("请确保已安装PyQt6: pip install PyQt6")
    sys.exit(1)


def main():
    """主函数"""
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Easy Menu Navigator")
        app.setApplicationVersion("1.0.0")
        
        # 创建并显示主窗口
        window = MainWindow()
        window.show()
        
        # 运行应用
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"应用程序启动失败: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()