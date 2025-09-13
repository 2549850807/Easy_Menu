

# 项目说明

* 本项目包含了两个部分，菜单的底层框架以及配套的可视化配置器

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

- **内存池优化**：采用预分配内存池机制，减少内存碎片，提升性能
- **增量显示更新**：仅刷新变化的显示行，减少CPU和内存开销
- **快速字符串操作**：使用DJB2哈希算法和优化的字符串构建函数
- **零动态内存分配**：支持纯静态内存分配模式，适用于实时系统
- **多种菜单类型**：支持普通菜单、可变菜单、切换菜单、应用菜单和展示菜单

#### 菜单系统配置（在`menu_navigator_c.h`中修改以下宏定义：）

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `MAX_DISPLAY_CHAR` | 16 | 每行最大字符数 |
| `MAX_DISPLAY_ITEM` | 4 | 显示的最大行数 |
| `MENU_POOL_SIZE` | 64 | 内存池大小（菜单项数量） |
| `MENU_SELECT_CURSOR` | "->" | 默认选择指示符 |
| `MENU_HAS_SUBMENU_INDICATOR` | ">>" | 锁定指示符 |

### 菜单项类型

#### 普通菜单项 (MENU_TYPE_NORMAL)

用于构建菜单层次结构，可以包含子菜单项。

```c
// 创建子菜单项数组
static menu_item_t* children[3];
children[0] = menu_create_toggle_item("LED1", &led1_state, led1_callback);
children[1] = menu_create_toggle_item("LED2", &led2_state, led2_callback);
children[2] = menu_create_app_item("Save", NULL, save_config);

// 创建普通菜单项
menu_item_t* led_menu = menu_create_normal_item("LED Control", children, 3);
```

#### 切换菜单项 (MENU_TYPE_TOGGLE)

用于布尔值的开关控制。

```c
bool led_state = false;

void led_toggle_callback(bool state) {
    // 设置LED状态
    set_led(state);
}

menu_item_t* led_item = menu_create_toggle_item("LED", &led_state, led_toggle_callback);
```

**操作方式**:
- 右键进入编辑模式，显示`>>`前缀
- 上/下键切换ON/OFF状态
- 左键退出编辑模式

#### 可变菜单项 (MENU_TYPE_CHANGEABLE)

用于数值类型的参数调节。

```c
float kp_value = 1.0f;
float min_val = 0.0f;
float max_val = 100.0f;
float step_val = 0.1f;

void kp_change_callback(void* value) {
    // 参数改变时的处理
    update_pid_parameters();
}

menu_item_t* kp_item = menu_create_changeable_item(
    "Kp", &kp_value, &min_val, &max_val, &step_val, 
    DATA_TYPE_FLOAT, kp_change_callback);
```

**支持的数据类型**:
- `DATA_TYPE_UINT8/16/32/64`: 无符号整数
- `DATA_TYPE_INT8/16/32/64`: 有符号整数  
- `DATA_TYPE_FLOAT/DOUBLE`: 浮点数

#### 应用菜单项

用于执行特定的功能操作。

```c
void save_config_func(void** args) {
    // 执行保存配置的操作
    save_settings_to_flash();
    display_message("Config Saved!");
}

menu_item_t* save_item = menu_create_app_item("Save Config", NULL, save_config_func);
```

#### 展示菜单项 (MENU_TYPE_EXHIBITION)

用于显示动态信息，支持分页显示。

##### 带导航器的展示项

```c
void system_info_callback(navigator_t* nav) {
    char buffer[16];
    
    // 显示CPU使用率
    snprintf(buffer, sizeof(buffer), "CPU: %d%%", get_cpu_usage());
    navigator_write_display_line(nav, buffer, 1);
    
    // 显示内存使用率
    snprintf(buffer, sizeof(buffer), "MEM: %d%%", get_memory_usage());
    navigator_write_display_line(nav, buffer, 2);
}

menu_item_t* info_item = menu_create_exhibition_item_with_nav("System Info", system_info_callback);
```

##### 分页展示项

```c
void multi_page_callback(navigator_t* nav, uint8_t current_page, uint8_t total_pages) {
    char buffer[16];
    
    switch(current_page) {
        case 0: // 第一页：系统状态
            snprintf(buffer, sizeof(buffer), "Sys Status");
            navigator_write_display_line(nav, buffer, 1);
            snprintf(buffer, sizeof(buffer), "CPU: %d%%", get_cpu_usage());
            navigator_write_display_line(nav, buffer, 2);
            break;
            
        case 1: // 第二页：网络信息
            snprintf(buffer, sizeof(buffer), "Network Info");
            navigator_write_display_line(nav, buffer, 1);
            snprintf(buffer, sizeof(buffer), "IP: %s", get_ip_address());
            navigator_write_display_line(nav, buffer, 2);
            break;
    }
}

menu_item_t* multi_item = menu_create_exhibition_item_with_page("Multi Info", 2, multi_page_callback);
```

**展示项操作**:
- 右键进入展示模式
- 上/下键翻页（如果支持分页）
- 左键退出展示模式

### API参考

#### 核心导航器API

##### navigator_create()
```c
navigator_t* navigator_create(menu_item_t* main_item);
```
创建菜单导航器实例。

**参数**:
- `main_item`: 主菜单项指针

**返回值**: 导航器实例指针，失败返回NULL

##### navigator_handle_input()
```c
void navigator_handle_input(navigator_t* nav, key_value_t key_value);
```
处理按键输入。

**参数**:
- `nav`: 导航器实例
- `key_value`: 按键值（KEY_UP/DOWN/LEFT/RIGHT/NONE）

##### navigator_refresh_display()
```c
void navigator_refresh_display(navigator_t* nav);
```
刷新显示内容（使用增量更新优化）。

##### navigator_get_display_buffer()
```c
char* navigator_get_display_buffer(navigator_t* nav);
```
获取显示缓冲区指针。

**返回值**: 显示缓冲区数据，大小为`MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM`

#### 菜单项创建API

##### 基本菜单项
```c
menu_item_t* menu_create_normal_item(const char* name, menu_item_t** children_items, uint8_t count);
menu_item_t* menu_create_toggle_item(const char* name, bool* ref, void (*on_toggle)(bool));
menu_item_t* menu_create_changeable_item(const char* name, void* ref, void* min_val, void* max_val, void* step_val, data_type_t data_type, void (*on_change)(void*));
menu_item_t* menu_create_app_item(const char* name, void** app_args, void (*app_func)(void**));
```

##### 展示菜单项
```c
menu_item_t* menu_create_exhibition_item_with_nav(const char* name, void (*callback)(navigator_t*));
menu_item_t* menu_create_exhibition_item_with_page(const char* name, uint8_t total_pages, void (*callback)(navigator_t*, uint8_t, uint8_t));
```

#### 内存池管理API

```c
void memory_pool_init(void);                    // 初始化内存池
menu_item_t* memory_pool_alloc(void);          // 分配菜单项
void memory_pool_free(menu_item_t* item);      // 释放菜单项
size_t memory_pool_get_usage(void);            // 获取内存池使用率
```

### 高级功能

#### 内存池管理

系统采用内存池机制管理菜单项内存，预分配固定大小的内存块，避免内存碎片。

```c
// 检查内存池使用情况
size_t used_items = memory_pool_get_usage();
if (used_items > MENU_POOL_SIZE * 0.8) {
    // 内存池使用率超过80%，考虑优化
    warning("Memory pool usage high: %d/%d", used_items, MENU_POOL_SIZE);
}
```

#### 增量显示更新

系统使用哈希比较和行状态管理实现增量更新，仅刷新变化的显示行。

```c
// 手动标记所有行需要强制更新
navigator_mark_all_lines_dirty(nav);

// 写入特定行（自动进行增量更新检查）
navigator_write_display_line(nav, "New Content", 0);
```

#### 展示项分页控制

```c
// 检查当前选中项是否支持分页
if (navigator_is_exhibition_pageable(nav)) {
    uint8_t current = navigator_get_exhibition_current_page(nav);
    uint8_t total = navigator_get_exhibition_total_pages(nav);
    printf("Page %d/%d", current + 1, total);
}

// 程序化控制分页
navigator_exhibition_next_page(nav);      // 下一页
navigator_exhibition_prev_page(nav);      // 上一页
navigator_exhibition_reset_to_first_page(nav); // 重置到第一页
```

### 技术支持

如遇到技术问题，请检查：
1. 编译器是否支持C99标准
2. 头文件包含路径是否正确
3. 宏定义配置是否合理
4. 内存分配是否充足

## 参考项目

[RealTaseny/Easy_Menu_builder: An open source sofaware base on Qt, which you can easily build your own C++-based static menu navigator.](https://github.com/RealTaseny/Easy_Menu_builder)

# 作者

* 如果觉得有帮助，请动动手指点一个 ⭐，非常感谢！
* 在使用过程中出现 BUG 或者觉得哪里的使用不够方便的话，欢迎提交 issue

