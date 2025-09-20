#ifndef MENU_NAVIGATOR_C_H
#define MENU_NAVIGATOR_C_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct navigator navigator_t;
typedef struct menu_item menu_item_t;

/**
 * @defgroup MenuConfig 菜单配置宏定义
 * @brief 菜单系统的基本配置参数
 * @{
 */

/** @brief 每行显示的最大字符数 */
#define MAX_DISPLAY_CHAR 64U

/** @brief 屏幕显示的最大行数 */
#define MAX_DISPLAY_ITEM 5U

/** @brief 静态菜单项的最大数量 */
#define MAX_STATIC_MENU_ITEMS 64

/** @brief 菜单选择光标指示符 */
#define MENU_SELECT_CURSOR "->"

/** @brief 菜单子项指示符 */
#define MENU_HAS_SUBMENU_INDICATOR ">>"

/** @} */

/**
 * @brief 显示行状态枚举
 * @details 用于标记显示行是否需要更新
 */
typedef enum {
    LINE_STATE_UNCHANGED = 0,    /**< 行内容未改变 */
    LINE_STATE_FORCE_UPDATE      /**< 强制更新行内容 */
} line_state_t;

/**
 * @brief 显示行数据结构
 * @details 存储每行的显示内容、状态和哈希值
 */
typedef struct {
    char content[MAX_DISPLAY_CHAR];  /**< 行显示内容 */
    line_state_t state;              /**< 行状态 */
    uint32_t hash;                   /**< 内容哈希值，用于快速比较 */
} display_line_t;

/**
 * @brief 菜单项类型枚举
 * @details 定义了菜单系统支持的所有菜单项类型
 */
typedef enum {
    MENU_TYPE_NORMAL = 0,    /**< 普通菜单项，可包含子菜单 */
    MENU_TYPE_CHANGEABLE,    /**< 可变值菜单项，支持数值调整 */
    MENU_TYPE_TOGGLE,        /**< 开关菜单项，支持布尔值切换 */
    MENU_TYPE_EXHIBITION     /**< 展示菜单项，支持分页显示 */
} menu_item_type_t;

/**
 * @brief 按键值枚举
 * @details 定义了菜单系统支持的按键类型
 */
typedef enum {
    KEY_UP = 0,     /**< 上键 */
    KEY_DOWN,       /**< 下键 */
    KEY_LEFT,       /**< 左键 */
    KEY_RIGHT,      /**< 右键 */
    KEY_UP_RepeatPress,     /**< 数值改变时长按上键 */
    KEY_DOWN_RepeatPress,  /**<  数值改变时长按下键 */
    KEY_NONE        /**< 无按键 */
} key_value_t;

/**
 * @brief 数据类型枚举
 * @details 定义了可变值菜单项支持的数据类型
 */
typedef enum {
    DATA_TYPE_UINT8 = 0,    /**< 8位无符号整数 */
    DATA_TYPE_UINT16,       /**< 16位无符号整数 */
    DATA_TYPE_UINT32,       /**< 32位无符号整数 */
    DATA_TYPE_UINT64,       /**< 64位无符号整数 */
    DATA_TYPE_INT8,         /**< 8位有符号整数 */
    DATA_TYPE_INT16,        /**< 16位有符号整数 */
    DATA_TYPE_INT32,        /**< 32位有符号整数 */
    DATA_TYPE_INT64,        /**< 64位有符号整数 */
    DATA_TYPE_FLOAT,        /**< 单精度浮点数 */
    DATA_TYPE_DOUBLE        /**< 双精度浮点数 */
} data_type_t;

/**
 * @brief 可变值数据结构
 * @details 用于MENU_TYPE_CHANGEABLE类型菜单项的数据配置
 */
typedef struct {
    void* ref;                      /**< 指向实际变量的指针 */
    void* min_val;                  /**< 最小值指针 */
    void* max_val;                  /**< 最大值指针 */
    void* step_val;                 /**< 步长值指针 */
    void* RepeatPress_press_val;      /**< 长按步长值指针 */
    data_type_t data_type;          /**< 数据类型 */
    void (*on_change)(void* value); /**< 值改变时的回调函数 */
} changeable_data_t;

/**
 * @brief 开关数据结构
 * @details 用于MENU_TYPE_TOGGLE类型菜单项的数据配置
 */
typedef struct {
    bool state;                     /**< 当前开关状态 */
    bool* ref;                      /**< 指向实际布尔变量的指针 */
    void (*on_toggle)(bool state);  /**< 开关切换时的回调函数 */
} toggle_data_t;

/**
 * @brief 展示数据结构
 * @details 用于MENU_TYPE_EXHIBITION类型菜单项的数据配置
 */
typedef struct {
    uint8_t current_page;   /**< 当前页码（从0开始） */
    uint8_t total_pages;    /**< 总页数 */
    uint8_t lines_per_page; /**< 每页行数 */
} exhibition_data_t;

/**
 * @brief 菜单项结构体
 * @details 菜单系统的核心数据结构，定义了菜单项的所有属性
 */
struct menu_item {
    bool is_locked;                     /**< 是否锁定（锁定时不可编辑） */
    const char* item_name;              /**< 菜单项名称 */
    struct menu_item* parent_item;      /**< 父菜单项指针 */
    struct menu_item** children_items;  /**< 子菜单项指针数组 */
    uint8_t children_count;             /**< 子菜单项数量 */
    uint8_t saved_selected_index;       /**< 保存的选中索引 */
    uint8_t saved_first_visible_item;   /**< 保存的首个可见项索引 */
    menu_item_type_t type;              /**< 菜单项类型 */
    
    /** @brief 菜单项数据联合体，根据类型使用不同的数据结构 */
    union {
        changeable_data_t changeable;   /**< 可变值数据 */
        toggle_data_t toggle;           /**< 开关数据 */
        exhibition_data_t exhibition;   /**< 展示数据 */
    } data;
    
    void (*app_func)(void** args);      /**< 应用程序函数指针 */
    void (*periodic_callback_with_page)(navigator_t* nav, uint8_t current_page, uint8_t total_pages); /**< 分页回调函数 */
    void** app_args;                    /**< 应用程序参数 */
};

/**
 * @brief 导航器结构体
 * @details 菜单导航器的核心数据结构，管理菜单显示和导航状态
 */
struct navigator {
    char display_buffer[MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM];   /**< 显示缓冲区 */
    display_line_t display_lines[MAX_DISPLAY_ITEM];             /**< 显示行数组 */
    menu_item_t* current_menu;                                  /**< 当前菜单项指针 */
    bool in_app_mode;                                           /**< 是否处于应用模式 */
    uint8_t selected_index;                                     /**< 当前选中的菜单项索引 */
    uint8_t first_visible_item;                                 /**< 首个可见菜单项索引 */
    uint8_t app_saved_selected_index;                           /**< 应用模式保存的选中索引 */
    uint8_t saved_first_visible_item_before_exhibition;         /**< 展示模式前保存的首个可见项索引 */
};

/**
 * @defgroup NavigatorCore 导航器核心函数
 * @brief 导航器的创建、销毁和基本操作
 * @{
 */

/**
 * @brief 创建导航器
 * @param main_item 主菜单项指针
 * @return 导航器指针，失败返回NULL
 * @details 初始化导航器并设置主菜单项
 */
navigator_t* navigator_create(menu_item_t* main_item);

/**
 * @brief 销毁导航器
 * @param nav 导航器指针
 * @details 清理导航器资源（静态版本中为空操作）
 */
void navigator_destroy(navigator_t* nav);

/**
 * @brief 处理按键输入
 * @param nav 导航器指针
 * @param key_value 按键值
 * @details 根据按键值执行相应的菜单操作
 */
void navigator_handle_input(navigator_t* nav, key_value_t key_value);

/**
 * @brief 刷新显示内容
 * @param nav 导航器指针
 * @details 更新显示缓冲区内容
 */
void navigator_refresh_display(navigator_t* nav);

/** @} */

/**
 * @defgroup NavigatorMode 导航器模式管理
 * @brief 应用模式的设置和获取
 * @{
 */

/**
 * @brief 设置应用模式
 * @param nav 导航器指针
 * @param is_app_mode 是否为应用模式
 * @details 设置导航器是否处于应用模式
 */
void navigator_set_app_mode(navigator_t* nav, bool is_app_mode);

/**
 * @brief 获取应用模式状态
 * @param nav 导航器指针
 * @return 是否处于应用模式
 */
bool navigator_get_app_mode(const navigator_t* nav);

/** @} */

/**
 * @defgroup NavigatorDisplay 导航器显示管理
 * @brief 显示缓冲区和显示行的管理
 * @{
 */

/**
 * @brief 获取显示缓冲区
 * @param nav 导航器指针
 * @return 显示缓冲区指针
 * @details 返回包含所有显示内容的缓冲区
 */
char* navigator_get_display_buffer(navigator_t* nav);

/**
 * @brief 写入显示行
 * @param nav 导航器指针
 * @param buffer 要写入的内容
 * @param line 行号（0-3）
 * @details 将内容写入指定的显示行
 */
void navigator_write_display_line(navigator_t* nav, const char* buffer, uint8_t line);

/**
 * @brief 强制刷新显示
 * @param nav 导航器指针
 * @details 清空显示缓冲区并强制更新所有显示行
 */
void navigator_force_refresh_display(navigator_t* nav);

/**
 * @brief 标记所有行为脏数据
 * @param nav 导航器指针
 * @details 标记所有显示行需要强制更新
 */
void navigator_mark_all_lines_dirty(navigator_t* nav);

/** @} */

/**
 * @defgroup NavigatorExhibition 展示模式管理
 * @brief 展示类型菜单项的分页管理
 * @{
 */

/**
 * @brief 检查是否可分页
 * @param nav 导航器指针
 * @return 当前选中项是否支持分页
 */
bool navigator_is_exhibition_pageable(const navigator_t* nav);

/**
 * @brief 下一页
 * @param nav 导航器指针
 * @details 切换到展示项的下一页
 */
void navigator_exhibition_next_page(navigator_t* nav);

/**
 * @brief 上一页
 * @param nav 导航器指针
 * @details 切换到展示项的上一页
 */
void navigator_exhibition_prev_page(navigator_t* nav);

/**
 * @brief 重置到第一页
 * @param nav 导航器指针
 * @details 将展示项重置到第一页
 */
void navigator_exhibition_reset_to_first_page(navigator_t* nav);

/**
 * @brief 获取当前页码
 * @param nav 导航器指针
 * @return 当前页码（从0开始）
 */
uint8_t navigator_get_exhibition_current_page(const navigator_t* nav);

/**
 * @brief 获取总页数
 * @param nav 导航器指针
 * @return 总页数
 */
uint8_t navigator_get_exhibition_total_pages(const navigator_t* nav);

/** @} */

/**
 * @defgroup NavigatorInfo 导航器信息获取
 * @brief 获取当前菜单状态信息
 * @{
 */

/**
 * @brief 获取当前页面名称
 * @param nav 导航器指针
 * @return 当前页面名称字符串
 * @details 返回当前菜单页面的名称，展示模式下包含页码信息
 */
const char* navigator_get_current_page_name(const navigator_t* nav);

/**
 * @brief 获取当前选中项名称
 * @param nav 导航器指针
 * @return 当前选中菜单项的名称
 */
const char* navigator_get_current_selected_item_name(const navigator_t* nav);

/**
 * @brief 检查是否处于展示模式
 * @param nav 导航器指针
 * @return 是否处于展示模式
 * @details 判断当前选中项是否为展示类型且处于解锁状态
 */
bool navigator_is_in_exhibition_mode(const navigator_t* nav);

/** @} */

#endif
