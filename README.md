

# 项目说明

* 本项目包含了两个部分，菜单的底层框架以及配套的可视化配置器
* 视频教程：https://www.bilibili.com/video/BV1EFpmzMEN8
* 必备环境：需要保证编译器支持 C99 。（Keil MDK……）

## 快速开始

1. 下载界面右侧发行版中的 `Easy_Menu v1.0.0.zip` 并解压。
2. 将 `src` 中的文件都添加进工程中。
3. 准备好当前显示设备显示字符串的函数，并测试固定字体下，最大为几行，每行可以容纳多少个字符，根据测试结果修改以下参数：

```C
/* menu_navigator.h */

// 显示的长宽（字符数量）
#define MAX_DISPLAY_CHAR 20U
#define MAX_DISPLAY_ITEM 8U
```

4. 在自己的工程中实现 `void menu_show_string(unsigned char line, char* str)` ，添加自己的显示字符串函数即可。

```C
#include "menu_wrapper.h"
/**
 * @brief 在显示器上显示字符串
 * @param line 当前行（Y 轴）
 * @param str 需要显示的字符串
 */
void menu_show_string(unsigned char line, char* str)
{
  OLED_ShowStr(0, line, str, 8);
}
```

4. 根据以下代码构建使用程序

### 基本使用流程

```c
#include "menu_navigator.h"
#include "menu_wrapper.h"
#include "generated_header.h"

// 1. 创建导航器
void* navigator;

int main(void) {
    // 2. 获取主菜单项
    navigator = menu_builder(getMainItem());
    
    // 3. 主循环（更新和显示菜单）
    while(1) {
        // 处理按键输入
        uint8_t key = get_key_input(); // 用户实现的按键获取函数
        menu_handle_input(navigator, key);
        
        // 刷新显示菜单
        menu_display(navigator);
        
        delay_ms(50); // 适当延时
    }
    
    // 3. 清理资源
    menu_delete(navigator);
    return 0;
}
```
6. 菜单构建文件为 `generated_code.c` 可以将在 `Easy_Menu_Builder` 生成的代码直接复制过去使用。

### 按键定义

```c
enum {
    UP,    // 上键：向上导航或增加数值
    DOWN,  // 下键：向下导航或减少数值  
    LEFT,  // 左键：返回上级或退出编辑模式
    RIGHT, // 右键：进入下级或进入编辑模式
    NONE   // 无按键
};

extern void* navigator;

menu_handle_input(navigator, UP); // 按键输入
```

# Easy Menu Builder - 可视化菜单配置生成器

## 项目概述

Easy Menu Builder是一个专为嵌入式设备设计的菜单配置生成器。它提供了一个直观的图形界面，允许开发者轻松创建和配置复杂的菜单结构，并自动生成相应的C语言代码，并提供实时仿真功能，可直接用于嵌入式项目中。

### 核心特性

- **图形化菜单设计界面**：通过拖拽和属性配置快速构建菜单
- **多种菜单项类型支持**：
  - 普通菜单项（Normal）：用于构建菜单层次结构
  - 切换菜单项（Toggle）：用于布尔值的开关控制
  - 可变菜单项（Changeable）：用于数值类型的参数调节
  - 应用菜单项（Application）：用于执行特定功能操作
  - 展示菜单项（Exhibition）：用于显示动态信息，支持分页显示
- **实时代码预览**：即时查看生成的C代码
- **配置文件保存和加载**：支持JSON格式的菜单配置文件
- **代码生成**：自动生成完整的C语言菜单代码
- **仿真器预览**：内置仿真器预览菜单效果
- **零代码依赖**：生成的C代码无外部依赖，适用于资源受限的嵌入式环境

## 目录结构

```
Easy_Menu/
├── Easy_Menu_Builder/          # Python应用程序源代码
│   ├── src/                    # 源代码目录
│   │   ├── controllers/        # 控制器模块
│   │   ├── models/             # 数据模型
│   │   ├── utils/              # 工具类
│   │   └── views/              # 视图组件
│   ├── main.py                 # 程序入口
│   ├── requirements.txt        # 依赖列表
├── examples/                   # 示例文件
│   └── test.json              # 示例配置文件
├── generated/                  # 生成的代码文件
│   ├── generated_code.c       # 生成的C代码示例
│   └── generated_header.h     # 生成的头文件示例
├── menu_core/                  # 菜单核心C代码
│   ├── menu_navigator.c       # 菜单导航器核心实现
│   ├── menu_navigator.h       # 菜单导航器头文件
│   ├── menu_wrapper.c         # 菜单包装器实现
│   └── menu_wrapper.h         # 菜单包装器头文件
└── README.md                  # 项目说明文档
```

## 安装与运行

### 方法1：使用预编译的应用程序（推荐）

直接运行打包好的Windows应用程序，无需安装Python环境：

```bash
Easy_Menu_Builder.exe
```

### 方法2：从源代码运行

#### 环境要求

- Python 3.8或更高版本
- PyQt6
- Windows/Linux/macOS

#### 安装依赖

```bash
pip install -r Easy_Menu_Builder/requirements.txt
```

#### 运行程序

```bash
cd Easy_Menu_Builder
python main.py
```

或者在Windows系统中直接运行：

## 使用说明

### 1. 创建菜单结构

- 右键点击树形视图添加菜单项
- 支持多级嵌套菜单结构
- 可通过右键菜单编辑、删除、移动菜单项

### 2. 配置菜单属性

- 选择菜单项后在右侧属性面板中编辑属性
- 不同类型的菜单项有不同的可配置属性：
  - **普通菜单项**：仅支持基本属性
  - **切换菜单项**：支持默认状态、变量名、回调函数等属性
  - **可变菜单项**：支持数据类型、最小值、最大值、步长、变量名、回调函数等属性
  - **应用菜单项**：支持回调函数属性
  - **展示菜单项**：支持总页数、回调函数等属性

### 3. 生成代码

- 点击"生成代码"按钮或使用菜单"文件->生成代码"
- 在代码预览区域查看生成的C代码（直接复制到 `generated_code.c` 中即可使用 ）
- 可将代码保存到文件

### 4. 仿真器预览

- 生成代码后，可以在代码预览标签页的右侧看到仿真器界面
- 仿真器可以模拟菜单在嵌入式设备上的显示效果
- 支持通过键盘方向键操作菜单导航

## 生成的代码结构

生成的代码包含以下部分：

- 变量定义结构体：包含所有菜单项所需的变量
- 回调函数模板：为需要回调的菜单项生成函数模板
- 菜单项创建函数：为每个菜单项生成创建函数
- 主菜单创建函数：创建整个菜单结构的入口函数
- 获取主菜单项函数：提供获取主菜单项的接口

## 技术架构

- **前端框架**：PyQt6
- **架构模式**：MVC（Model-View-Controller）
- **数据格式**：JSON（配置文件）
- **代码生成**：基于模板的代码生成器

## Easy_menu 系统使用指南

### 系统概述

Easy_Menu 是一个专为嵌入式设备设计的高效菜单管理框架，特别适用于资源受限的MCU环境。系统采用C语言实现，提供了完整的菜单构建、导航控制和显示管理功能。

#### 核心特性

- **多类型菜单项支持**：普通菜单、开关菜单、数值调节菜单、展示菜单
- **智能显示优化**：基于哈希值的增量更新，减少不必要的重绘
- **灵活的导航模式**：支持按键导航和应用程序模式
- **内存优化设计**：静态内存分配，避免动态内存管理
- **高性能实现**：优化的字符串操作和快速哈希算法
- **模块化架构**：清晰的代码结构，易于扩展和维护

#### 菜单系统配置（在`menu_navigator_c.h`中修改以下宏定义：）

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `MAX_DISPLAY_CHAR` | 16 | 每行最大字符数 |
| `MAX_DISPLAY_ITEM` | 4 | 显示的最大行数 |
| `MAX_STATIC_MENU_ITEMS` | 64 | 菜单项数量 |
| `MENU_SELECT_CURSOR` | "->" | 默认选择指示符 |
| `MENU_HAS_SUBMENU_INDICATOR` | ">>" | 锁定指示符 |

### 基本操作

1. 使用四方向按键进行导航
   - **上/下键**：在菜单项间移动光标
   - **右键**：进入子菜单或编辑模式
   - **左键**：返回上级菜单或退出编辑模式

2. 不同菜单项类型的操作
   - **普通菜单**：右键进入子菜单或启动应用
   - **开关菜单**：右键解锁，上/下键切换状态
   - **数值菜单**：右键解锁，上/下键调节数值
   - **展示菜单**：右键进入展示模式，上/下键翻页

### 技术支持

如遇到技术问题，请检查：
1. 编译器是否支持C99标准
2. 头文件包含路径是否正确
3. 宏定义配置是否合理
4. 内存分配是否充足

## 参考项目

[RealTaseny/Easy_Menu_builder: An open source sofaware base on Qt, which you can easily build your own C++-based static menu navigator.](https://github.com/RealTaseny/Easy_Menu_builder)

# 作者的话

* 如果觉得有帮助，请动动手指点一个 ⭐，非常感谢！
* 在使用过程中出现 BUG 或者觉得哪里的使用不够方便的话，欢迎提交 issue

