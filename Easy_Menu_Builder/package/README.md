# Easy Menu Navigator - 菜单配置生成器

基于PyQt6的可视化菜单配置工具，专为嵌入式设备设计，可生成C语言菜单代码。

## 功能特性

- 图形化菜单设计界面
- 支持多种菜单项类型：
  - 普通菜单项
  - 切换菜单项
  - 可变菜单项
  - 应用菜单项
  - 展示菜单项
- 实时预览生成的C代码
- 配置文件保存和加载（JSON格式）
- 拖拽式菜单结构编辑
- 属性面板配置

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python main.py
```

## 使用说明

1. **创建菜单结构**：
   - 右键点击树形视图添加菜单项
   - 支持多级嵌套菜单结构
   - 可通过右键菜单编辑、删除、移动菜单项

2. **配置菜单属性**：
   - 选择菜单项后在右侧属性面板中编辑属性
   - 不同类型的菜单项有不同的可配置属性

3. **生成代码**：
   - 点击"生成代码"按钮或使用菜单"文件->生成代码"
   - 在代码预览区域查看生成的C代码
   - 可将代码保存到文件

## 生成的代码结构

生成的代码包含以下部分：

- 变量定义结构体
- 回调函数模板
- 菜单项创建函数
- 主菜单创建函数

## 技术架构

- **前端框架**：PyQt6
- **架构模式**：MVC（Model-View-Controller）
- **数据格式**：JSON（配置文件）
- **代码生成**：基于模板的代码生成器

## 目录结构

```
easy_menu_navigator/
├── main.py                 # 程序入口
├── requirements.txt        # 依赖列表
├── README.md              # 说明文档
└── src/
    ├── models/            # 数据模型
    │   ├── menu_item_model.py
    │   └── menu_config_model.py
    ├── views/             # 视图组件
    │   ├── main_window.py
    │   ├── menu_tree_view.py
    │   └── property_panel.py
    ├── controllers/       # 控制器
    │   ├── menu_controller.py
    │   └── file_controller.py
    └── utils/             # 工具类
        ├── json_serializer.py
        └── code_generator.py
```

## 开发计划

- [ ] 添加撤销/重做功能
- [ ] 支持更多数据类型
- [ ] 添加代码模板自定义功能
- [ ] 支持更多菜单项属性配置
- [ ] 添加帮助文档和使用示例