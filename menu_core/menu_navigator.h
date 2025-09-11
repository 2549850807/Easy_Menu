#ifndef MENU_NAVIGATOR_C_H
#define MENU_NAVIGATOR_C_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>


typedef struct navigator navigator_t;
typedef struct menu_item menu_item_t;

// 显示的长宽（字符数量）
#define MAX_DISPLAY_CHAR 20U
#define MAX_DISPLAY_ITEM 8U

// 内存池配置
#define MENU_POOL_SIZE 64           // 菜单项内存池大小
#define ENABLE_STATIC_ALLOCATION 1  // 启用静态分配模式

// 提示字符
#define MENU_SELECT_CURSOR "->"
#define MENU_HAS_SUBMENU_INDICATOR ">>"

/**
 * @brief 显示行状态枚举
 */
typedef enum {
    LINE_STATE_UNCHANGED = 0,
    LINE_STATE_DIRTY,
    LINE_STATE_FORCE_UPDATE
} line_state_t;

/**
 * @brief 显示缓冲区管理结构
 */
typedef struct {
    char content[MAX_DISPLAY_CHAR];     // 行内容
    line_state_t state;                 // 行状态
    uint32_t hash;                      // 内容哈希值用于快速比较
} display_line_t;

/**
 * @brief 菜单项类型枚举
 */
typedef enum {
    MENU_TYPE_NORMAL = 0,
    MENU_TYPE_CHANGEABLE,
    MENU_TYPE_TOGGLE,
    MENU_TYPE_EXHIBITION
} menu_item_type_t;

/**
 * @brief 按键值枚举
 */
typedef enum {
    KEY_UP = 0,
    KEY_DOWN,
    KEY_LEFT,
    KEY_RIGHT,
    KEY_NONE
} key_value_t;

/**
 * @brief 可变项数据类型枚举
 */
typedef enum {
    DATA_TYPE_UINT8 = 0,
    DATA_TYPE_UINT16,
    DATA_TYPE_UINT32,
    DATA_TYPE_UINT64,
    DATA_TYPE_INT8,
    DATA_TYPE_INT16,
    DATA_TYPE_INT32,
    DATA_TYPE_INT64,
    DATA_TYPE_FLOAT,
    DATA_TYPE_DOUBLE
} data_type_t;

/**
 * @brief 可变项数据结构
 */
typedef struct {
    void* ref;                          // 数据引用指针
    void* min_val;                      // 最小值指针
    void* max_val;                      // 最大值指针
    void* step_val;                     // 步长指针
    data_type_t data_type;             // 数据类型
    void (*on_change)(void* value);    // 变化回调函数
} changeable_data_t;

/**
 * @brief 切换项数据结构
 */
typedef struct {
    bool state;                        // 当前状态
    bool* ref;                         // 状态引用指针
    void (*on_toggle)(bool state);     // 切换回调函数
} toggle_data_t;

/**
 * @brief 展示项数据结构
 */
typedef struct {
    uint8_t current_page;              // 当前页码
    uint8_t total_pages;               // 总页数
    uint8_t lines_per_page;            // 每页行数
} exhibition_data_t;

/**
 * @brief 菜单项结构体
 */
struct menu_item {
    bool is_locked;                                    // 是否锁定
    const char* item_name;                            // 菜单项名称
    struct menu_item* parent_item;                    // 父菜单项
    struct menu_item** children_items;               // 子菜单项数组
    uint8_t children_count;                           // 子菜单项数量
    uint8_t saved_selected_index;                     // 保存的选中索引
    uint8_t saved_first_visible_item;                 // 保存的首个可见项索引
    menu_item_type_t type;                            // 菜单项类型
    
    // 类型特定数据
    union {
        changeable_data_t changeable;                 // 可变项数据
        toggle_data_t toggle;                         // 切换项数据
        exhibition_data_t exhibition;                 // 展示项数据
    } data;
    
    // 回调函数指针
    void (*app_func)(void** args);                    // 应用函数
    void (*periodic_callback)(void);                  // 周期回调
    void (*periodic_callback_with_nav)(navigator_t* nav);  // 带导航器的周期回调
    void (*periodic_callback_with_page)(navigator_t* nav, uint8_t current_page, uint8_t total_pages);  // 带分页的周期回调
    void** app_args;                                  // 应用参数
};

/**
 * @brief 内存池管理结构
 */
typedef struct {
    menu_item_t pool[MENU_POOL_SIZE];   // 内存池
    bool used[MENU_POOL_SIZE];          // 使用状态
    size_t next_free;                   // 下一个空闲位置提示
} memory_pool_t;

/**
 * @brief 导航器结构体
 */
struct navigator {
    char display_buffer[MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM];  // 兼容的显示缓冲区
    display_line_t display_lines[MAX_DISPLAY_ITEM];            // 增量更新的行管理
    menu_item_t* current_menu;                        // 当前菜单
    bool in_app_mode;                                // 应用模式标志
    uint8_t selected_index;                          // 选中索引
    uint8_t first_visible_item;                      // 首个可见项索引
    uint8_t app_saved_selected_index;                // 应用保存的选中索引
    uint8_t saved_first_visible_item_before_exhibition;  // 展示前保存的首个可见项
};

// 菜单项创建函数
menu_item_t* menu_create_normal_item(const char* name, menu_item_t** children_items, uint8_t count);
menu_item_t* menu_create_changeable_item(const char* name, void* ref, void* min_val, void* max_val, void* step_val, data_type_t data_type, void (*on_change)(void*));
menu_item_t* menu_create_toggle_item(const char* name, bool* ref, void (*on_toggle)(bool));
menu_item_t* menu_create_app_item(const char* name, void** app_args, void (*app_func)(void**));
menu_item_t* menu_create_exhibition_item(const char* name, uint8_t total_pages, void (*callback)(navigator_t*, uint8_t, uint8_t));

// 菜单项操作函数
void menu_item_toggle(menu_item_t* item);
void menu_item_increment(menu_item_t* item);
void menu_item_decrement(menu_item_t* item);
void menu_item_get_value_str(const menu_item_t* item, char* value_str, size_t size);
void menu_item_set_total_pages(menu_item_t* item, uint8_t total_pages);
uint8_t menu_item_get_current_page(const menu_item_t* item);
uint8_t menu_item_get_total_pages(const menu_item_t* item);
void menu_item_next_page(menu_item_t* item);
void menu_item_prev_page(menu_item_t* item);
void menu_item_reset_to_first_page(menu_item_t* item);

// 导航器函数
navigator_t* navigator_create(menu_item_t* main_item);
void navigator_destroy(navigator_t* nav);
void navigator_handle_input(navigator_t* nav, key_value_t key_value);
void navigator_refresh_display(navigator_t* nav);
void navigator_set_app_mode(navigator_t* nav, bool is_app_mode);
bool navigator_get_app_mode(const navigator_t* nav);
char* navigator_get_display_buffer(navigator_t* nav);
void navigator_write_display_buffer(navigator_t* nav, const char* buffer, size_t size, uint8_t first_line);
void navigator_write_display_line(navigator_t* nav, const char* buffer, uint8_t line);
void navigator_force_refresh_display(navigator_t* nav);
void navigator_mark_all_lines_dirty(navigator_t* nav);

// 展示项分页相关函数
bool navigator_is_exhibition_pageable(const navigator_t* nav);
void navigator_exhibition_next_page(navigator_t* nav);
void navigator_exhibition_prev_page(navigator_t* nav);
void navigator_exhibition_reset_to_first_page(navigator_t* nav);
uint8_t navigator_get_exhibition_current_page(const navigator_t* nav);
uint8_t navigator_get_exhibition_total_pages(const navigator_t* nav);
const char* navigator_get_current_page_name(const navigator_t* nav);
const char* navigator_get_current_selected_item_name(const navigator_t* nav);
bool navigator_is_in_exhibition_mode(const navigator_t* nav);

// 内存池管理函数
void memory_pool_init(void);
menu_item_t* memory_pool_alloc(void);
void memory_pool_free(menu_item_t* item);
size_t memory_pool_get_usage(void);

#endif // MENU_NAVIGATOR_C_H
