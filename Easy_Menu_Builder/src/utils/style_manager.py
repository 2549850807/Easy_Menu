from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor, QPalette
import sys


class StyleManager:
    """样式管理器，负责应用UI美化样式"""
    
    # Fluent设计颜色调色板
    FLUENT_COLORS = {
        'primary': '#0078D4',      # 主要颜色 - 蓝色
        'secondary': '#4C4A48',    # 次要颜色 - 灰色
        'success': '#107C10',      # 成功颜色 - 绿色
        'warning': '#F2C811',      # 警告颜色 - 黄色
        'error': '#E81123',        # 错误颜色 - 红色
        'background': '#FFFFFF',   # 背景颜色 - 白色
        'surface': '#F3F2F1',      # 表面颜色 - 浅灰色
        'text_primary': '#201F1E', # 主要文字颜色 - 深灰色
        'text_secondary': '#605E5C' # 次要文字颜色 - 中灰色
    }
    
    # 苹果风格颜色调色板
    APPLE_COLORS = {
        'primary': '#007AFF',      # 主要颜色 - 蓝色
        'secondary': '#8E8E93',    # 次要颜色 - 灰色
        'success': '#34C759',      # 成功颜色 - 绿色
        'warning': '#FF9500',      # 警告颜色 - 橙色
        'error': '#FF3B30',        # 错误颜色 - 红色
        'background': '#F2F2F7',   # 背景颜色 - 浅灰色
        'surface': '#FFFFFF',      # 表面颜色 - 白色
        'text_primary': '#000000', # 主要文字颜色 - 黑色
        'text_secondary': '#8E8E93' # 次要文字颜色 - 灰色
    }
    
    # 清新简约配色方案
    FRESH_COLORS = {
        'primary': '#4A90E2',      # 清新蓝色
        'secondary': '#7B8A8B',    # 灰绿色
        'success': '#50C878',      # 翠绿色
        'warning': '#FFA500',      # 橙色
        'error': '#FF6347',        # 珊瑚红
        'background': '#F8F9FA',   # 极浅灰
        'surface': '#FFFFFF',      # 白色
        'text_primary': '#2C3E50', # 深蓝灰
        'text_secondary': '#7F8C8D' # 灰色
    }
    
    @staticmethod
    def apply_apple_fluent_style():
        """应用苹果风格与Fluent设计结合的样式"""
        app = QApplication.instance()
        if not app:
            return
            
        # 获取颜色调色板
        colors = StyleManager.FRESH_COLORS  # 使用清新的配色方案
        
        # 苹果风格与Fluent设计结合的样式表
        style_sheet = f"""
        /* 主窗口样式 */
        QMainWindow {{
            background-color: {colors['background']};
            font-family: "Segoe UI", "San Francisco", "PingFang SC", sans-serif;
        }}
        
        /* 菜单栏样式 */
        QMenuBar {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            padding: 2px;
        }}
        
        QMenuBar::item {{
            background: transparent;
            padding: 8px 12px;
            border-radius: 6px;
            margin: 0 2px;
        }}
        
        QMenuBar::item:selected {{
            background: rgba(74, 144, 226, 0.1);
        }}
        
        QMenuBar::item:pressed {{
            background: rgba(74, 144, 226, 0.2);
        }}
        
        /* 菜单样式 */
        QMenu {{
            background-color: {colors['surface']};
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            padding: 4px 0;
        }}
        
        QMenu::item {{
            padding: 6px 24px;
            color: {colors['text_primary']};
        }}
        
        QMenu::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        QMenu::separator {{
            height: 1px;
            background: rgba(0, 0, 0, 0.1);
            margin: 4px 0;
        }}
        
        /* 工具栏样式 */
        QToolBar {{
            background-color: {colors['surface']};
            border: none;
            padding: 4px;
        }}
        
        /* 按钮样式 */
        QPushButton {{
            background-color: {colors['surface']};
            border: 1px solid rgba(0, 0, 0, 0.1);
            color: {colors['text_primary']};
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: normal;
            min-height: 32px;
        }}
        
        QPushButton:hover {{
            background-color: rgba(74, 144, 226, 0.05);
            border-color: rgba(74, 144, 226, 0.3);
        }}
        
        QPushButton:pressed {{
            background-color: rgba(74, 144, 226, 0.1);
        }}
        
        QPushButton:disabled {{
            background-color: rgba(0, 0, 0, 0.02);
            color: {colors['text_secondary']};
            border-color: rgba(0, 0, 0, 0.05);
        }}
        
        QPushButton#primaryButton {{
            background-color: {colors['primary']};
            color: white;
            border: 1px solid {colors['primary']};
            font-weight: 500;
        }}
        
        QPushButton#primaryButton:hover {{
            background-color: #3A80D8;
            border-color: #3A80D8;
        }}
        
        QPushButton#primaryButton:pressed {{
            background-color: #2A70C8;
            border-color: #2A70C8;
        }}
        
        QPushButton#primaryButton:disabled {{
            background-color: rgba(74, 144, 226, 0.3);
            border-color: rgba(74, 144, 226, 0.3);
        }}
        
        /* 树形控件样式 */
        QTreeWidget {{
            background-color: {colors['surface']};
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 6px;
            alternate-background-color: {colors['background']};
            outline: 0px;
            selection-background-color: {colors['primary']};
            selection-color: white;
        }}
        
        QTreeWidget::item {{
            border-radius: 4px;
            padding: 6px;
        }}
        
        QTreeWidget::item:hover {{
            background-color: rgba(74, 144, 226, 0.03);
        }}
        
        QTreeWidget::item:selected {{
            background-color: {colors['primary']};
            color: white;
            border-radius: 4px;
        }}
        
        QTreeWidget::item:selected:active {{
            background-color: {colors['primary']};
        }}
        
        QTreeWidget::branch:has-siblings:!adjoins-item {{
            border-image: url(:/vline) 0;
        }}
        
        QTreeWidget::branch:has-siblings:adjoins-item {{
            border-image: url(:/branch-more) 0;
        }}
        
        QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {{
            border-image: url(:/branch-end) 0;
        }}
        
        QTreeWidget::branch:has-children:!has-siblings:closed,
        QTreeWidget::branch:closed:has-children:has-siblings {{
            border-image: none;
            image: url(:/branch-closed);
        }}
        
        QTreeWidget::branch:open:has-children:!has-siblings,
        QTreeWidget::branch:open:has-children:has-siblings {{
            border-image: none;
            image: url(:/branch-open);
        }}
        
        /* 分组框样式 */
        QGroupBox {{
            font-weight: 500;
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            margin-top: 1.5ex;
            background-color: {colors['surface']};
            padding-top: 10px;
        }}
        
        QGroupBox::title {{
            subcontrol-offset: -14px;
            padding: 0 10px;
            background-color: transparent;
            color: {colors['text_primary']};
        }}
        
        /* 输入控件样式 */
        QLineEdit, QComboBox, QTextEdit {{
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 6px;
            padding: 6px 8px;
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            selection-background-color: {colors['primary']};
            selection-color: white;
            min-height: 24px;
        }}
        
        QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
            border: 1px solid {colors['primary']};
            outline: none;
        }}
        
        QLineEdit:disabled, QComboBox:disabled, QTextEdit:disabled {{
            background-color: rgba(0, 0, 0, 0.02);
            color: {colors['text_secondary']};
        }}
        
        QComboBox {{
            padding-right: 20px;
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: url(:/arrow-down);
            width: 12px;
            height: 12px;
        }}
        
        QComboBox QAbstractItemView {{
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 4px;
            background-color: {colors['surface']};
            selection-background-color: {colors['primary']};
            selection-color: white;
        }}
        
        /* 微调按钮样式 */
        QSpinBox, QDoubleSpinBox {{
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 6px;
            padding: 6px 8px;
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            min-height: 24px;
        }}
        
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid rgba(0, 0, 0, 0.1);
            border-top-right-radius: 6px;
            background-color: transparent;
        }}
        
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 20px;
            border-left: 1px solid rgba(0, 0, 0, 0.1);
            border-bottom-right-radius: 6px;
            background-color: transparent;
        }}
        
        QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
            image: url(:/arrow-up);
            width: 12px;
            height: 12px;
        }}
        
        QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
            image: url(:/arrow-down);
            width: 12px;
            height: 12px;
        }}
        
        /* 复选框样式 */
        QCheckBox {{
            color: {colors['text_primary']};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 4px;
            background-color: {colors['surface']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors['primary']};
            border-color: {colors['primary']};
            image: url(:/checkmark);
        }}
        
        QCheckBox::indicator:unchecked:hover {{
            border-color: rgba(0, 0, 0, 0.2);
        }}
        
        QCheckBox::indicator:checked:hover {{
            background-color: #3A80D8;
            border-color: #3A80D8;
        }}
        
        QCheckBox::indicator:disabled {{
            background-color: rgba(0, 0, 0, 0.02);
            border-color: rgba(0, 0, 0, 0.05);
        }}
        
        QCheckBox::indicator:checked:disabled {{
            background-color: rgba(74, 144, 226, 0.3);
            border-color: rgba(74, 144, 226, 0.3);
        }}
        
        /* 标签页样式 */
        QTabWidget::pane {{
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            border-top-left-radius: 0;
        }}
        
        QTabBar::tab {{
            background-color: transparent;
            border: 1px solid transparent;
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding: 10px 20px;
            margin-right: 2px;
            color: {colors['text_secondary']};
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['surface']};
            border-color: rgba(0, 0, 0, 0.1);
            color: {colors['text_primary']};
            border-bottom: 1px solid {colors['surface']};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: rgba(74, 144, 226, 0.05);
            color: {colors['text_primary']};
        }}
        
        /* 状态栏样式 */
        QStatusBar {{
            background-color: {colors['surface']};
            border-top: 1px solid rgba(0, 0, 0, 0.1);
            color: {colors['text_secondary']};
        }}
        
        /* 标签样式 */
        QLabel {{
            color: {colors['text_primary']};
        }}
        
        QLabel#titleLabel {{
            color: {colors['text_primary']};
            font-weight: 600;
            font-size: 16px;
        }}
        
        /* 分割器样式 - 支持自适应拉伸 */
        QSplitter::handle {{
            background-color: rgba(0, 0, 0, 0.1);
            width: 3px;
            height: 3px;
        }}
        
        QSplitter::handle:hover {{
            background-color: {colors['primary']};
        }}
        
        QSplitter::handle:pressed {{
            background-color: {colors['primary']};
        }}
        
        /* 水平分割器 */
        QSplitter::handle:horizontal {{
            width: 3px;
            background-color: rgba(0, 0, 0, 0.1);
            margin: 0 2px;
        }}
        
        /* 垂直分割器 */
        QSplitter::handle:vertical {{
            height: 3px;
            background-color: rgba(0, 0, 0, 0.1);
            margin: 2px 0;
        }}
        
        /* 滚动条样式 */
        QScrollBar:vertical {{
            background: transparent;
            width: 14px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: rgba(0, 0, 0, 0.2);
            min-height: 20px;
            border-radius: 7px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: rgba(0, 0, 0, 0.3);
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background: none;
        }}
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
        
        QScrollBar:horizontal {{
            background: transparent;
            height: 14px;
            margin: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: rgba(0, 0, 0, 0.2);
            min-width: 20px;
            border-radius: 7px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: rgba(0, 0, 0, 0.3);
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            background: none;
        }}
        
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
        }}
        
        /* 对话框样式 */
        QDialog {{
            background-color: {colors['background']};
        }}
        
        /* 表单布局样式 */
        QFormLayout {{
            spacing: 12px;
        }}
        
        QFormLayout QLabel {{
            color: {colors['text_primary']};
            font-weight: 500;
        }}
        """
        
        app.setStyleSheet(style_sheet)
        
    @staticmethod
    def get_vscode_color_scheme():
        """获取更鲜明的VSCode配色方案"""
        return {
            'keyword': '#569CD6',      # 关键字 - 蓝色
            'function': '#DCDCAA',     # 函数 - 黄色
            'string': '#CE9178',       # 字符串 - 橙色
            'comment': '#6A9955',      # 注释 - 绿色
            'type': '#4EC9B0',         # 类型 - 青色
            'number': '#B5CEA8',       # 数字 - 浅绿色
            'operator': '#D4D4D4',     # 操作符 - 浅灰色
            'preprocessor': '#C586C0', # 预处理指令 - 紫色
            'default': '#D4D4D4'       # 默认文本 - 浅灰色
        }
        
    @staticmethod
    def get_brighter_color_scheme():
        """获取更鲜明的配色方案"""
        return {
            'keyword': '#0066CC',      # 关键字 - 鲜艳蓝色
            'function': '#FF9900',     # 函数 - 橙色
            'string': '#CC3333',       # 字符串 - 红色
            'comment': '#009900',      # 注释 - 绿色
            'type': '#9900CC',         # 类型 - 紫色
            'number': '#FF6600',       # 数字 - 橙红色
            'operator': '#333333',     # 操作符 - 深灰色
            'preprocessor': '#CC00CC', # 预处理指令 - 紫红色
            'default': '#000000'       # 默认文本 - 黑色
        }