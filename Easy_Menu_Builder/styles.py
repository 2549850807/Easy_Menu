
# iOS Blue
ACCENT_COLOR = "#007AFF"
ACCENT_HOVER = "#0062CC"
ACCENT_PRESSED = "#004999"

# Light Theme Colors
LIGHT_BG = "#F2F2F7"        # iOS System Grouped Background
LIGHT_SURFACE = "#FFFFFF"    # iOS System Background
LIGHT_TEXT = "#000000"
LIGHT_BORDER = "#D1D1D6"
LIGHT_HOVER = "#E5E5EA"

# Dark Theme Colors
DARK_BG = "#000000"          # iOS Dark System Background
DARK_SURFACE = "#1C1C1E"     # iOS Dark Secondary System Background
DARK_TEXT = "#FFFFFF"
DARK_BORDER = "#38383A"
DARK_HOVER = "#2C2C2E"

LIGHT_THEME = f"""
    /* Global Reset */
    * {{
        font-family: "Segoe UI", "San Francisco", "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 13px;
        color: {LIGHT_TEXT};
    }}

    /* Main Window & Dialogs */
    QMainWindow, QDialog {{
        background-color: {LIGHT_BG};
    }}

    /* Specific Containers Transparent */
    #CentralWidget, #PropertyEditor {{
        background-color: transparent;
    }}
    
    /* Splitter Handle */
    QSplitter::handle {{
        background-color: {LIGHT_BORDER};
        width: 1px;
    }}

    /* Menu Bar - Removed Border Bottom */
    QMenuBar {{
        background-color: {LIGHT_BG};
        border: none;
    }}
    QMenuBar::item {{
        background-color: transparent;
        padding: 8px 12px;
        color: {LIGHT_TEXT};
    }}
    QMenuBar::item:selected {{
        background-color: {LIGHT_SURFACE};
        border-radius: 4px;
    }}

    /* ToolBar - Added Border Bottom */
    QToolBar {{
        background-color: {LIGHT_BG};
        border: none;
        border-bottom: 1px solid {LIGHT_BORDER};
        spacing: 5px;
        padding: 5px;
    }}
    QToolButton {{
        background-color: transparent;
        border: none;
        border-radius: 4px;
        padding: 4px;
        color: {LIGHT_TEXT};
    }}
    QToolButton:hover {{
        background-color: {LIGHT_HOVER};
    }}
    QToolButton:pressed {{
        background-color: {LIGHT_BORDER};
    }}

    /* Menus */
    QMenu {{
        background-color: {LIGHT_SURFACE};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 8px;
        padding: 4px;
    }}
    QMenu::item {{
        padding: 6px 24px 6px 12px;
        border-radius: 4px;
        color: {LIGHT_TEXT};
    }}
    QMenu::item:selected {{
        background-color: {ACCENT_COLOR};
        color: white;
    }}
    QMenu::separator {{
        height: 1px;
        background-color: {LIGHT_BORDER};
        margin: 4px 0;
    }}

    /* ToolTips */
    QToolTip {{
        background-color: {LIGHT_TEXT};
        color: {LIGHT_BG};
        border: none;
        border-radius: 4px;
        padding: 4px;
    }}

    /* Tree Widget */
    QTreeWidget {{
        background-color: {LIGHT_SURFACE};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 10px;
        outline: none;
        padding: 5px;
    }}
    QTreeWidget::item {{
        padding: 4px;
        border-radius: 6px;
    }}
    QTreeWidget::item:selected {{
        background-color: {ACCENT_COLOR};
        color: white;
    }}
    QTreeWidget::item:hover:!selected {{
        background-color: {LIGHT_HOVER};
    }}
    
    QHeaderView::section {{
        background-color: {LIGHT_BG};
        color: {LIGHT_TEXT};
        padding: 4px;
        border: none;
        border-bottom: 1px solid {LIGHT_BORDER};
        font-weight: bold;
    }}

    /* Group Box */
    QGroupBox {{
        background-color: {LIGHT_SURFACE};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 10px;
        margin-top: 10px;
        padding-top: 15px;
        font-weight: bold;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        left: 10px;
        color: {LIGHT_TEXT};
    }}

    /* Inputs */
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
        background-color: {LIGHT_BG};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 8px;
        padding: 6px;
        selection-background-color: {ACCENT_COLOR};
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 1px solid {ACCENT_COLOR};
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {ACCENT_COLOR};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 6px 16px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {ACCENT_HOVER};
    }}
    QPushButton:pressed {{
        background-color: {ACCENT_PRESSED};
    }}
    
    /* ScrollBars */
    QScrollBar:vertical {{
        border: none;
        background: {LIGHT_BG};
        width: 10px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: #C1C1C1;
        min-height: 20px;
        border-radius: 5px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
"""

DARK_THEME = f"""
    /* Global Reset */
    * {{
        font-family: "Segoe UI", "San Francisco", "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 13px;
        color: {DARK_TEXT};
    }}

    /* Main Window & Dialogs */
    QMainWindow, QDialog {{
        background-color: {DARK_BG};
    }}

    /* Specific Containers Transparent */
    #CentralWidget, #PropertyEditor {{
        background-color: transparent;
    }}
    
    /* Splitter Handle */
    QSplitter::handle {{
        background-color: {DARK_BORDER};
        width: 1px;
    }}

    /* Menu Bar - Removed Border Bottom */
    QMenuBar {{
        background-color: {DARK_BG};
        border: none;
    }}
    QMenuBar::item {{
        background-color: transparent;
        padding: 8px 12px;
        color: {DARK_TEXT};
    }}
    QMenuBar::item:selected {{
        background-color: {DARK_SURFACE};
        border-radius: 4px;
    }}

    /* ToolBar - Added Border Bottom */
    QToolBar {{
        background-color: {DARK_BG};
        border: none;
        border-bottom: 1px solid {DARK_BORDER};
        spacing: 5px;
        padding: 5px;
    }}
    QToolButton {{
        background-color: transparent;
        border: none;
        border-radius: 4px;
        padding: 4px;
        color: {DARK_TEXT};
    }}
    QToolButton:hover {{
        background-color: {DARK_HOVER};
    }}
    QToolButton:pressed {{
        background-color: {DARK_BORDER};
    }}

    /* Menus */
    QMenu {{
        background-color: {DARK_SURFACE};
        border: 1px solid {DARK_BORDER};
        border-radius: 8px;
        padding: 4px;
    }}
    QMenu::item {{
        padding: 6px 24px 6px 12px;
        border-radius: 4px;
        color: {DARK_TEXT};
    }}
    QMenu::item:selected {{
        background-color: {ACCENT_COLOR};
        color: white;
    }}
    QMenu::separator {{
        height: 1px;
        background-color: {DARK_BORDER};
        margin: 4px 0;
    }}

    /* ToolTips */
    QToolTip {{
        background-color: {DARK_TEXT};
        color: {DARK_BG};
        border: none;
        border-radius: 4px;
        padding: 4px;
    }}

    /* Tree Widget */
    QTreeWidget {{
        background-color: {DARK_SURFACE};
        border: 1px solid {DARK_BORDER};
        border-radius: 10px;
        outline: none;
        padding: 5px;
    }}
    QTreeWidget::item {{
        padding: 4px;
        border-radius: 6px;
    }}
    QTreeWidget::item:selected {{
        background-color: {ACCENT_COLOR};
        color: white;
    }}
    QTreeWidget::item:hover:!selected {{
        background-color: {DARK_HOVER};
    }}
    
    QHeaderView::section {{
        background-color: {DARK_BG};
        color: {DARK_TEXT};
        padding: 4px;
        border: none;
        border-bottom: 1px solid {DARK_BORDER};
        font-weight: bold;
    }}

    /* Group Box */
    QGroupBox {{
        background-color: {DARK_SURFACE};
        border: 1px solid {DARK_BORDER};
        border-radius: 10px;
        margin-top: 10px;
        padding-top: 15px;
        font-weight: bold;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        left: 10px;
        color: {DARK_TEXT};
    }}

    /* Inputs */
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
        background-color: {DARK_BG};
        border: 1px solid {DARK_BORDER};
        border-radius: 8px;
        padding: 6px;
        color: {DARK_TEXT};
        selection-background-color: {ACCENT_COLOR};
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 1px solid {ACCENT_COLOR};
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {ACCENT_COLOR};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 6px 16px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {ACCENT_HOVER};
    }}
    QPushButton:pressed {{
        background-color: {ACCENT_PRESSED};
    }}
    
    /* ScrollBars */
    QScrollBar:vertical {{
        border: none;
        background: {DARK_BG};
        width: 10px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: #555555;
        min-height: 20px;
        border-radius: 5px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
"""
