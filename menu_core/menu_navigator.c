#include "menu_navigator.h"
#include <string.h>
#include <stdio.h>

/** @brief 静态导航器实例，避免动态内存分配 */
static navigator_t g_static_navigator = {0};

/**
 * @defgroup UtilityFunctions 工具函数
 * @brief 内部使用的优化工具函数
 * @{
 */

/**
 * @brief 快速字符填充函数
 * @param dest 目标缓冲区
 * @param c 要填充的字符
 * @param len 填充长度
 * @details 使用指针递增方式快速填充字符，比标准memset更高效
 */
static inline void fast_memset_char(char* dest, char c, size_t len) {
    char* end = dest + len;
    while (dest < end) {
        *dest++ = c;
    }
}

/**
 * @brief 快速字符串复制函数
 * @param dest 目标缓冲区
 * @param src 源字符串
 * @param max_len 最大复制长度
 * @return 实际复制的字符数
 * @details 边复制边计算长度，避免重复遍历
 */
static inline size_t fast_copy_string(char* dest, const char* src, size_t max_len) {
    if (!dest || !src || max_len == 0) return 0;
    
    size_t i = 0;
    while (i < max_len && src[i] != '\0') {
        dest[i] = src[i];
        i++;
    }
    return i;
}

/**
 * @brief 快速字符串复制并填充空格
 * @param dest 目标缓冲区
 * @param src 源字符串
 * @param len 目标长度
 * @details 复制字符串并用空格填充剩余位置，确保固定长度输出
 */
static inline void fast_strncpy_pad(char* dest, const char* src, size_t len) {
    if (!dest || !src || len == 0) return;
    
    size_t copied = fast_copy_string(dest, src, len);
    
    if (copied < len) {
        fast_memset_char(dest + copied, ' ', len - copied);
    }
}

/**
 * @brief 快速哈希计算函数
 * @param str 输入字符串
 * @param len 最大计算长度
 * @return 32位哈希值
 * @details 使用djb2算法计算字符串哈希值，用于快速内容比较
 */
static uint32_t fast_hash(const char* str, size_t len) {
    if (!str) return 0;
    
    uint32_t hash = 5381;
    const char* end = str + len;
    
    while (str < end && *str != '\0') {
        hash = ((hash << 5) + hash) + (uint8_t)*str++;
    }
    
    return hash;
}

/**
 * @brief 快速字符串构建函数
 * @param dest 目标缓冲区
 * @param dest_size 目标缓冲区大小
 * @param prefix 前缀字符串
 * @param main_str 主字符串
 * @param suffix 后缀字符串
 * @details 高效地将三个字符串拼接到目标缓冲区中
 */
static void fast_string_build(char* dest, size_t dest_size, const char* prefix, const char* main_str, const char* suffix) {
    if (!dest || dest_size == 0) return;
    
    char* pos = dest;
    char* end = dest + dest_size - 1;
    
    if (prefix) {
        while (pos < end && *prefix != '\0') {
            *pos++ = *prefix++;
        }
    }
    
    if (main_str) {
        while (pos < end && *main_str != '\0') {
            *pos++ = *main_str++;
        }
    }
    
    if (suffix) {
        while (pos < end && *suffix != '\0') {
            *pos++ = *suffix++;
        }
    }
    
    *pos = '\0';
}

/**
 * @brief 检查字符串内容是否改变
 * @param old_str 旧字符串
 * @param new_str 新字符串
 * @param len 比较长度
 * @return 内容是否改变
 * @details 用于优化显示更新，只有内容改变时才重新渲染
 */
static bool string_content_changed(const char* old_str, const char* new_str, size_t len) {
    if (!old_str || !new_str) return true;
    return strncmp(old_str, new_str, len) != 0;
}

/** @} */

/**
 * @defgroup DataTypeOperations 数据类型操作函数
 * @brief 支持多种数据类型的通用操作函数
 * @{
 */

/**
 * @brief 按数据类型递增值
 * @param ref 变量指针
 * @param step 步长指针
 * @param type 数据类型
 * @details 根据数据类型对变量进行递增操作
 */
static void increment_value_by_type(void* ref, void* step, data_type_t type) {
    switch (type) {
        case DATA_TYPE_UINT8: *(uint8_t*)ref += *(uint8_t*)step; break;
        case DATA_TYPE_UINT16: *(uint16_t*)ref += *(uint16_t*)step; break;
        case DATA_TYPE_UINT32: *(uint32_t*)ref += *(uint32_t*)step; break;
        case DATA_TYPE_UINT64: *(uint64_t*)ref += *(uint64_t*)step; break;
        case DATA_TYPE_INT8: *(int8_t*)ref += *(int8_t*)step; break;
        case DATA_TYPE_INT16: *(int16_t*)ref += *(int16_t*)step; break;
        case DATA_TYPE_INT32: *(int32_t*)ref += *(int32_t*)step; break;
        case DATA_TYPE_INT64: *(int64_t*)ref += *(int64_t*)step; break;
        case DATA_TYPE_FLOAT: *(float*)ref += *(float*)step; break;
        case DATA_TYPE_DOUBLE: *(double*)ref += *(double*)step; break;
    }
}

/**
 * @brief 按数据类型递减值
 * @param ref 变量指针
 * @param step 步长指针
 * @param min_val 最小值指针（未使用，保留用于边界检查）
 * @param type 数据类型
 * @details 根据数据类型对变量进行递减操作
 */
static void decrement_value_by_type(void* ref, void* step, void* min_val, data_type_t type) {
    switch (type) {
        case DATA_TYPE_UINT8: *(uint8_t*)ref -= *(uint8_t*)step; break;
        case DATA_TYPE_UINT16: *(uint16_t*)ref -= *(uint16_t*)step; break;
        case DATA_TYPE_UINT32: *(uint32_t*)ref -= *(uint32_t*)step; break;
        case DATA_TYPE_UINT64: *(uint64_t*)ref -= *(uint64_t*)step; break;
        case DATA_TYPE_INT8: *(int8_t*)ref -= *(int8_t*)step; break;
        case DATA_TYPE_INT16: *(int16_t*)ref -= *(int16_t*)step; break;
        case DATA_TYPE_INT32: *(int32_t*)ref -= *(int32_t*)step; break;
        case DATA_TYPE_INT64: *(int64_t*)ref -= *(int64_t*)step; break;
        case DATA_TYPE_FLOAT: *(float*)ref -= *(float*)step; break;
        case DATA_TYPE_DOUBLE: *(double*)ref -= *(double*)step; break;
    }
}

/**
 * @brief 检查是否可以递增值
 * @param ref 变量指针
 * @param step 步长指针
 * @param max_val 最大值指针
 * @param type 数据类型
 * @return 是否可以递增
 * @details 检查递增后是否会超过最大值限制
 */
static bool can_increment_value(void* ref, void* step, void* max_val, data_type_t type) {
    switch (type) {
        case DATA_TYPE_UINT8: return (*(uint8_t*)ref + *(uint8_t*)step <= *(uint8_t*)max_val);
        case DATA_TYPE_UINT16: return (*(uint16_t*)ref + *(uint16_t*)step <= *(uint16_t*)max_val);
        case DATA_TYPE_UINT32: return (*(uint32_t*)ref + *(uint32_t*)step <= *(uint32_t*)max_val);
        case DATA_TYPE_UINT64: return (*(uint64_t*)ref + *(uint64_t*)step <= *(uint64_t*)max_val);
        case DATA_TYPE_INT8: return (*(int8_t*)ref + *(int8_t*)step <= *(int8_t*)max_val);
        case DATA_TYPE_INT16: return (*(int16_t*)ref + *(int16_t*)step <= *(int16_t*)max_val);
        case DATA_TYPE_INT32: return (*(int32_t*)ref + *(int32_t*)step <= *(int32_t*)max_val);
        case DATA_TYPE_INT64: return (*(int64_t*)ref + *(int64_t*)step <= *(int64_t*)max_val);
        case DATA_TYPE_FLOAT: return (*(float*)ref + *(float*)step <= *(float*)max_val);
        case DATA_TYPE_DOUBLE: return (*(double*)ref + *(double*)step <= *(double*)max_val);
    }
    return false;
}

/**
 * @brief 检查是否可以递减值
 * @param ref 变量指针
 * @param step 步长指针
 * @param min_val 最小值指针
 * @param type 数据类型
 * @return 是否可以递减
 * @details 检查递减后是否会低于最小值限制
 */
static bool can_decrement_value(void* ref, void* step, void* min_val, data_type_t type) {
    switch (type) {
        case DATA_TYPE_UINT8: return (*(uint8_t*)ref >= *(uint8_t*)step && *(uint8_t*)ref - *(uint8_t*)step >= *(uint8_t*)min_val);
        case DATA_TYPE_UINT16: return (*(uint16_t*)ref >= *(uint16_t*)step && *(uint16_t*)ref - *(uint16_t*)step >= *(uint16_t*)min_val);
        case DATA_TYPE_UINT32: return (*(uint32_t*)ref >= *(uint32_t*)step && *(uint32_t*)ref - *(uint32_t*)step >= *(uint32_t*)min_val);
        case DATA_TYPE_UINT64: return (*(uint64_t*)ref >= *(uint64_t*)step && *(uint64_t*)ref - *(uint64_t*)step >= *(uint64_t*)min_val);
        case DATA_TYPE_INT8: return (*(int8_t*)ref - *(int8_t*)step >= *(int8_t*)min_val);
        case DATA_TYPE_INT16: return (*(int16_t*)ref - *(int16_t*)step >= *(int16_t*)min_val);
        case DATA_TYPE_INT32: return (*(int32_t*)ref - *(int32_t*)step >= *(int32_t*)min_val);
        case DATA_TYPE_INT64: return (*(int64_t*)ref - *(int64_t*)step >= *(int64_t*)min_val);
        case DATA_TYPE_FLOAT: return (*(float*)ref - *(float*)step >= *(float*)min_val);
        case DATA_TYPE_DOUBLE: return (*(double*)ref - *(double*)step >= *(double*)min_val);
    }
    return false;
}

/**
 * @brief 按数据类型格式化值为字符串
 * @param ref 变量指针
 * @param type 数据类型
 * @param str 输出字符串缓冲区
 * @param size 缓冲区大小
 * @details 将不同数据类型的值格式化为可显示的字符串
 */
static void format_value_by_type(void* ref, data_type_t type, char* str, size_t size) {
    switch (type) {
        case DATA_TYPE_UINT8:
        case DATA_TYPE_UINT16: snprintf(str, size, "%u", *(uint16_t*)ref); break;
        case DATA_TYPE_UINT32: snprintf(str, size, "%lu", *(uint32_t*)ref); break;
        case DATA_TYPE_UINT64: snprintf(str, size, "%llu", *(uint64_t*)ref); break;
        case DATA_TYPE_INT8:
        case DATA_TYPE_INT16: snprintf(str, size, "%d", *(int16_t*)ref); break;
        case DATA_TYPE_INT32: snprintf(str, size, "%ld", *(int32_t*)ref); break;
        case DATA_TYPE_INT64: snprintf(str, size, "%lld", *(int64_t*)ref); break;
        case DATA_TYPE_FLOAT: {
            int32_t scaled = (int32_t)(*(float*)ref * 1000.0f);
            int32_t integer = scaled / 1000;
            int32_t fraction = scaled % 1000;
            if (fraction < 0) fraction = -fraction;
            snprintf(str, size, "%ld.%03ld", integer, fraction);
            break;
        }
        case DATA_TYPE_DOUBLE: {
            int64_t scaled = (int64_t)(*(double*)ref * 1000000.0);
            int64_t integer = scaled / 1000000;
            int64_t fraction = scaled % 1000000;
            if (fraction < 0) fraction = -fraction;
            snprintf(str, size, "%lld.%06lld", integer, fraction);
            break;
        }
        default: snprintf(str, size, "<?>");
    }
}

/** @} */

/**
 * @defgroup MenuItemOperations 菜单项操作函数
 * @brief 针对不同类型菜单项的操作函数
 * @{
 */

/**
 * @brief 切换开关菜单项状态
 * @param item 菜单项指针
 * @details 切换TOGGLE类型菜单项的开关状态，并调用回调函数
 */
static void menu_item_toggle(menu_item_t* item) {
    if (!item || item->type != MENU_TYPE_TOGGLE) return;
    
    if (item->data.toggle.ref) {
        *(item->data.toggle.ref) = !(*(item->data.toggle.ref));
        item->data.toggle.state = *(item->data.toggle.ref);
        
        if (item->data.toggle.on_toggle) {
            item->data.toggle.on_toggle(*(item->data.toggle.ref));
        }
    }
}

/**
 * @brief 递增可变菜单项的值
 * @param item 菜单项指针
 * @details 增加CHANGEABLE类型菜单项的值，检查边界并调用回调函数
 */
static void menu_item_increment(menu_item_t* item) {
    if (!item || item->type != MENU_TYPE_CHANGEABLE) return;
    
    changeable_data_t* data = &item->data.changeable;
    
    if (can_increment_value(data->ref, data->step_val, data->max_val, data->data_type)) {
        increment_value_by_type(data->ref, data->step_val, data->data_type);
        
        if (data->on_change) {
            data->on_change(data->ref);
        }
    }
}

/**
 * @brief 递减可变菜单项的值
 * @param item 菜单项指针
 * @details 减少CHANGEABLE类型菜单项的值，检查边界并调用回调函数
 */
static void menu_item_decrement(menu_item_t* item) {
    if (!item || item->type != MENU_TYPE_CHANGEABLE) return;
    
    changeable_data_t* data = &item->data.changeable;
    
    if (can_decrement_value(data->ref, data->step_val, data->min_val, data->data_type)) {
        decrement_value_by_type(data->ref, data->step_val, data->min_val, data->data_type);
        
        if (data->on_change) {
            data->on_change(data->ref);
        }
    }
}

/**
 * @brief 获取菜单项的值字符串
 * @param item 菜单项指针
 * @param value_str 输出字符串缓冲区
 * @param size 缓冲区大小
 * @details 将菜单项的当前值转换为显示字符串
 */
static void menu_item_get_value_str(const menu_item_t* item, char* value_str, size_t size) {
    if (!item || !value_str) return;
    
    memset(value_str, 0, size);
    
    switch (item->type) {
        case MENU_TYPE_TOGGLE:
            if (item->data.toggle.state) {
                strncpy(value_str, "ON ", size - 1);
            } else {
                strncpy(value_str, "OFF", size - 1);
            }
            break;
            
        case MENU_TYPE_CHANGEABLE:
            format_value_by_type(item->data.changeable.ref, item->data.changeable.data_type, value_str, size);
            break;
            
        default:
            break;
    }
}

/**
 * @brief 展示菜单项下一页
 * @param item 菜单项指针
 * @details 切换EXHIBITION类型菜单项到下一页，支持循环翻页
 */
static void menu_item_next_page(menu_item_t* item) {
    if (!item || item->type != MENU_TYPE_EXHIBITION || item->data.exhibition.total_pages <= 1) return;
    
    item->data.exhibition.current_page = (item->data.exhibition.current_page + 1) % item->data.exhibition.total_pages;
}

/**
 * @brief 展示菜单项上一页
 * @param item 菜单项指针
 * @details 切换EXHIBITION类型菜单项到上一页，支持循环翻页
 */
static void menu_item_prev_page(menu_item_t* item) {
    if (!item || item->type != MENU_TYPE_EXHIBITION || item->data.exhibition.total_pages <= 1) return;
    
    item->data.exhibition.current_page = (item->data.exhibition.current_page == 0) 
        ? (item->data.exhibition.total_pages - 1) 
        : (item->data.exhibition.current_page - 1);
}

/** @} */

/**
 * @defgroup NavigatorCore 导航器核心功能实现
 * @brief 导航器的创建、销毁和基本操作实现
 * @{
 */

/**
 * @brief 创建导航器
 * @param main_item 主菜单项指针
 * @return 导航器指针，失败返回NULL
 * @details 初始化静态导航器实例并设置主菜单项，避免动态内存分配
 */
navigator_t* navigator_create(menu_item_t* main_item) {
    if (!main_item) return NULL;
    
    navigator_t* nav = &g_static_navigator;
    
    memset(nav, 0, sizeof(navigator_t));
    nav->current_menu = main_item;
    nav->in_app_mode = false;
    nav->selected_index = 0;
    nav->first_visible_item = 0;
    nav->app_saved_selected_index = 0;
    nav->saved_first_visible_item_before_exhibition = 0;
    
    for (uint8_t i = 0; i < MAX_DISPLAY_ITEM; i++) {
        nav->display_lines[i].state = LINE_STATE_FORCE_UPDATE;
        nav->display_lines[i].hash = 0;
        memset(nav->display_lines[i].content, 0, MAX_DISPLAY_CHAR);
    }
    
    return nav;
}

/**
 * @brief 销毁导航器
 * @param nav 导航器指针
 * @details 静态版本中为空操作，保持接口兼容性
 */
void navigator_destroy(navigator_t* nav) {
    (void)nav;
}

/** @} */

/**
 * @defgroup NavigatorInput 导航器输入处理
 * @brief 按键输入处理和菜单导航逻辑
 * @{
 */

/**
 * @brief 处理按键输入
 * @param nav 导航器指针
 * @param key_value 按键值
 * @details 根据按键值和当前菜单项类型执行相应的操作
 * @note 支持四种按键：上下左右，每种按键在不同菜单项类型下有不同行为
 */
void navigator_handle_input(navigator_t* nav, key_value_t key_value) {
    if (!nav || !nav->current_menu || !nav->current_menu->children_items) return;
    
    // 应用模式下只响应左键退出
    if (nav->in_app_mode) {
        if (key_value == KEY_LEFT) {
            nav->in_app_mode = false;
        }
        return;
    }
    
    menu_item_t* current_item = nav->current_menu->children_items[nav->selected_index];
    
    switch (key_value) {
        case KEY_UP:
            switch (current_item->type) {
                case MENU_TYPE_EXHIBITION:
                    if (current_item->is_locked) {
                        // 锁定状态：向上移动光标
                        nav->selected_index = (nav->selected_index == 0) 
                            ? (nav->current_menu->children_count - 1) 
                            : (nav->selected_index - 1);
                    } else {
                        // 解锁状态：上一页
                        menu_item_prev_page(current_item);
                    }
                    break;
                case MENU_TYPE_CHANGEABLE:
                    if (!current_item->is_locked) {
                        // 解锁状态：增加值
                        menu_item_increment(current_item);
                    } else {
                        // 锁定状态：向上移动光标
                        nav->selected_index = (nav->selected_index == 0) 
                            ? (nav->current_menu->children_count - 1) 
                            : (nav->selected_index - 1);
                    }
                    break;
                case MENU_TYPE_TOGGLE:
                    if (!current_item->is_locked) {
                        // 解锁状态：切换开关
                        menu_item_toggle(current_item);
                    } else {
                        // 锁定状态：向上移动光标
                        nav->selected_index = (nav->selected_index == 0) 
                            ? (nav->current_menu->children_count - 1) 
                            : (nav->selected_index - 1);
                    }
                    break;
                default:
                    // 普通菜单项：向上移动光标
                    nav->selected_index = (nav->selected_index == 0) 
                        ? (nav->current_menu->children_count - 1) 
                        : (nav->selected_index - 1);
                    break;
            }
            
            // 整页翻页逻辑：确保新页面从第一行开始显示
            if (nav->selected_index < nav->first_visible_item) {
                nav->first_visible_item = (nav->selected_index / MAX_DISPLAY_ITEM) * MAX_DISPLAY_ITEM;
            } else if (nav->selected_index >= nav->first_visible_item + MAX_DISPLAY_ITEM) {
                nav->first_visible_item = (nav->selected_index / MAX_DISPLAY_ITEM) * MAX_DISPLAY_ITEM;
            }
            break;
            
        case KEY_DOWN:
            switch (current_item->type) {
                case MENU_TYPE_EXHIBITION:
                    if (current_item->is_locked) {
                        // 锁定状态：向下移动光标
                        nav->selected_index = (nav->selected_index + 1) % nav->current_menu->children_count;
                    } else {
                        // 解锁状态：下一页
                        menu_item_next_page(current_item);
                    }
                    break;
                case MENU_TYPE_CHANGEABLE:
                    if (!current_item->is_locked) {
                        // 解锁状态：减少值
                        menu_item_decrement(current_item);
                    } else {
                        // 锁定状态：向下移动光标
                        nav->selected_index = (nav->selected_index + 1) % nav->current_menu->children_count;
                    }
                    break;
                case MENU_TYPE_TOGGLE:
                    if (!current_item->is_locked) {
                        // 解锁状态：切换开关
                        menu_item_toggle(current_item);
                    } else {
                        // 锁定状态：向下移动光标
                        nav->selected_index = (nav->selected_index + 1) % nav->current_menu->children_count;
                    }
                    break;
                default:
                    // 普通菜单项：向下移动光标
                    nav->selected_index = (nav->selected_index + 1) % nav->current_menu->children_count;
                    break;
            }
            
            // 整页翻页逻辑
            if (nav->selected_index < nav->first_visible_item) {
                nav->first_visible_item = (nav->selected_index / MAX_DISPLAY_ITEM) * MAX_DISPLAY_ITEM;
            } else if (nav->selected_index >= nav->first_visible_item + MAX_DISPLAY_ITEM) {
                nav->first_visible_item = (nav->selected_index / MAX_DISPLAY_ITEM) * MAX_DISPLAY_ITEM;
            }
            break;
            
        case KEY_RIGHT:
            switch (current_item->type) {
                case MENU_TYPE_NORMAL:
                    if (current_item->children_count > 0) {
                        // 进入子菜单
                        memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                        navigator_mark_all_lines_dirty(nav);
                        nav->current_menu->saved_selected_index = nav->selected_index;
                        nav->current_menu->saved_first_visible_item = nav->first_visible_item;
                        nav->current_menu = current_item;
                        nav->selected_index = 0;
                        nav->first_visible_item = 0;
                    } else if (current_item->app_func) {
                        // 启动应用程序
                        memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                        navigator_mark_all_lines_dirty(nav);
                        nav->in_app_mode = true;
                        nav->app_saved_selected_index = nav->selected_index;
                        current_item->app_func(current_item->app_args);
                    }
                    break;
                case MENU_TYPE_EXHIBITION:
                    if (current_item->is_locked) {
                        // 进入展示模式
                        current_item->is_locked = false;
                        current_item->data.exhibition.current_page = 0;
                        nav->saved_first_visible_item_before_exhibition = nav->first_visible_item;
                        nav->first_visible_item = nav->selected_index;
                        memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                        navigator_mark_all_lines_dirty(nav);
                    }
                    break;
                case MENU_TYPE_CHANGEABLE:
                case MENU_TYPE_TOGGLE:
                    // 解锁编辑模式
                    current_item->is_locked = false;
                    break;
            }
            break;
            
        case KEY_LEFT:
            switch (current_item->type) {
                case MENU_TYPE_NORMAL:
                    if (nav->current_menu->parent_item) {
                        // 返回父菜单
                        memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                        navigator_mark_all_lines_dirty(nav);
                        nav->current_menu = nav->current_menu->parent_item;
                        nav->selected_index = nav->current_menu->saved_selected_index;
                        nav->first_visible_item = nav->current_menu->saved_first_visible_item;
                    }
                    break;
                case MENU_TYPE_EXHIBITION:
                    if (!current_item->is_locked) {
                        // 退出展示模式
                        current_item->is_locked = true;
                        nav->first_visible_item = nav->saved_first_visible_item_before_exhibition;
                        memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                        navigator_mark_all_lines_dirty(nav);
                    } else if (nav->current_menu->parent_item) {
                        // 返回父菜单
                        memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                        navigator_mark_all_lines_dirty(nav);
                        nav->current_menu = nav->current_menu->parent_item;
                        nav->selected_index = nav->current_menu->saved_selected_index;
                        nav->first_visible_item = nav->current_menu->saved_first_visible_item;
                    }
                    break;
                case MENU_TYPE_CHANGEABLE:
                case MENU_TYPE_TOGGLE:
                    if (!current_item->is_locked) {
                        // 锁定编辑模式
                        current_item->is_locked = true;
                    } else if (nav->current_menu->parent_item) {
                        // 返回父菜单
                        memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                        navigator_mark_all_lines_dirty(nav);
                        nav->current_menu = nav->current_menu->parent_item;
                        nav->selected_index = nav->current_menu->saved_selected_index;
                        nav->first_visible_item = nav->current_menu->saved_first_visible_item;
                    }
                    break;
            }
            break;
        default:
            break;
    }
}

/** @} */

/**
 * @defgroup NavigatorDisplay 导航器显示管理实现
 * @brief 显示内容生成和缓冲区管理
 * @{
 */

/**
 * @brief 刷新显示内容
 * @param nav 导航器指针
 * @details 根据当前菜单状态生成显示内容，支持普通菜单和展示模式
 */
void navigator_refresh_display(navigator_t* nav) {
    if (!nav || !nav->current_menu) return;
    
    menu_item_t* selected_item = nav->current_menu->children_items[nav->selected_index];
    
    // 展示模式特殊处理
    if (selected_item->type == MENU_TYPE_EXHIBITION && !selected_item->is_locked) {
        uint8_t title_line = nav->selected_index - nav->first_visible_item;
        char title_buffer[MAX_DISPLAY_CHAR];
        
        // 构建标题行
        if (selected_item->data.exhibition.total_pages > 1) {
            fast_string_build(title_buffer, MAX_DISPLAY_CHAR, MENU_HAS_SUBMENU_INDICATOR, selected_item->item_name, "");
            char page_info[16];
            snprintf(page_info, sizeof(page_info), "(%d/%d):", 
                    selected_item->data.exhibition.current_page + 1,
                    selected_item->data.exhibition.total_pages);
            size_t current_len = 0;
            while (current_len < MAX_DISPLAY_CHAR && title_buffer[current_len] != '\0') current_len++;
            fast_copy_string(title_buffer + current_len, page_info, MAX_DISPLAY_CHAR - current_len);
        } else {
            fast_string_build(title_buffer, MAX_DISPLAY_CHAR, MENU_HAS_SUBMENU_INDICATOR, selected_item->item_name, ":");
        }
        
        navigator_write_display_line(nav, title_buffer, title_line);
        
        // 清空其他行
        for (uint8_t i = 1; i < MAX_DISPLAY_ITEM; i++) {
            navigator_write_display_line(nav, "", i);
        }
        
        // 调用分页回调函数
        if (selected_item->periodic_callback_with_page) {
            selected_item->periodic_callback_with_page(nav, 
                selected_item->data.exhibition.current_page,
                selected_item->data.exhibition.total_pages);
        }
        return;
    }
    
    static char line_buffer[MAX_DISPLAY_CHAR];
    static char value_str[MAX_DISPLAY_CHAR];
    
    // 普通菜单显示
    if (!nav->in_app_mode) {
        uint8_t visible_count = (nav->current_menu->children_count - nav->first_visible_item < MAX_DISPLAY_ITEM)
            ? (nav->current_menu->children_count - nav->first_visible_item)
            : MAX_DISPLAY_ITEM;
            
        // 生成可见菜单项
        for (uint8_t i = 0; i < visible_count; i++) {
            menu_item_t* item = nav->current_menu->children_items[i + nav->first_visible_item];
            const char* indicator = (nav->selected_index - nav->first_visible_item == i) ? MENU_SELECT_CURSOR : "  ";
            
            memset(line_buffer, 0, MAX_DISPLAY_CHAR);
            
            switch (item->type) {
                case MENU_TYPE_NORMAL:
                    fast_string_build(line_buffer, MAX_DISPLAY_CHAR, indicator, item->item_name, "");
                    break;
                    
                case MENU_TYPE_CHANGEABLE:
                case MENU_TYPE_TOGGLE:
                    menu_item_get_value_str(item, value_str, MAX_DISPLAY_CHAR);
                    if (item->is_locked) {
                        fast_string_build(line_buffer, MAX_DISPLAY_CHAR, indicator, item->item_name, ": ");
                        size_t current_len = 0;
                        while (current_len < MAX_DISPLAY_CHAR && line_buffer[current_len] != '\0') current_len++;
                        fast_copy_string(line_buffer + current_len, value_str, MAX_DISPLAY_CHAR - current_len);
                    } else {
                        fast_string_build(line_buffer, MAX_DISPLAY_CHAR, MENU_HAS_SUBMENU_INDICATOR, item->item_name, ": ");
                        size_t current_len = 0;
                        while (current_len < MAX_DISPLAY_CHAR && line_buffer[current_len] != '\0') current_len++;
                        fast_copy_string(line_buffer + current_len, value_str, MAX_DISPLAY_CHAR - current_len);
                    }
                    break;
                    
                case MENU_TYPE_EXHIBITION:
                    if (item->is_locked) {
                        fast_string_build(line_buffer, MAX_DISPLAY_CHAR, indicator, item->item_name, "");
                    } else {
                        fast_string_build(line_buffer, MAX_DISPLAY_CHAR, MENU_HAS_SUBMENU_INDICATOR, item->item_name, ":");
                    }
                    break;
            }
            
            navigator_write_display_line(nav, line_buffer, i);
        }
        
        // 清空剩余行
        for (uint8_t i = visible_count; i < MAX_DISPLAY_ITEM; i++) {
            navigator_write_display_line(nav, "", i);
        }
    }
}

/**
 * @brief 写入显示行
 * @param nav 导航器指针
 * @param buffer 要写入的内容
 * @param line 行号（0-3）
 * @details 使用哈希值优化，只有内容改变时才更新显示
 */
void navigator_write_display_line(navigator_t* nav, const char* buffer, uint8_t line) {
    if (!nav || !buffer || line >= MAX_DISPLAY_ITEM) return;
    
    uint32_t new_hash = fast_hash(buffer, MAX_DISPLAY_CHAR);
    
    // 只有内容改变或强制更新时才写入
    if (nav->display_lines[line].state == LINE_STATE_FORCE_UPDATE || 
        nav->display_lines[line].hash != new_hash ||
        string_content_changed(nav->display_lines[line].content, buffer, MAX_DISPLAY_CHAR)) {
        
        // 更新行内容
        fast_memset_char(nav->display_lines[line].content, 0, MAX_DISPLAY_CHAR);
        fast_strncpy_pad(nav->display_lines[line].content, buffer, MAX_DISPLAY_CHAR - 1);
        
        // 更新显示缓冲区
        fast_memset_char(&nav->display_buffer[MAX_DISPLAY_CHAR * line], 0, MAX_DISPLAY_CHAR);
        fast_strncpy_pad(&nav->display_buffer[MAX_DISPLAY_CHAR * line], buffer, MAX_DISPLAY_CHAR - 1);
        
        // 更新哈希值和状态
        nav->display_lines[line].hash = new_hash;
        nav->display_lines[line].state = LINE_STATE_UNCHANGED;
    }
}

/**
 * @brief 强制刷新显示
 * @param nav 导航器指针
 * @details 清空显示缓冲区并强制更新所有显示行
 */
void navigator_force_refresh_display(navigator_t* nav) {
    if (!nav) return;
    
    memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
    navigator_mark_all_lines_dirty(nav);
    navigator_refresh_display(nav);
}

/**
 * @brief 标记所有行为脏数据
 * @param nav 导航器指针
 * @details 标记所有显示行需要强制更新
 */
void navigator_mark_all_lines_dirty(navigator_t* nav) {
    if (!nav) return;
    
    for (uint8_t i = 0; i < MAX_DISPLAY_ITEM; i++) {
        nav->display_lines[i].state = LINE_STATE_FORCE_UPDATE;
    }
}

/**
 * @brief 获取显示缓冲区
 * @param nav 导航器指针
 * @return 显示缓冲区指针
 * @details 返回包含所有显示内容的缓冲区，出错时返回错误信息
 */
char* navigator_get_display_buffer(navigator_t* nav) {
    static char error_str[] = "No Menu Item";
    
    if (!nav || !nav->current_menu || !nav->current_menu->children_items) {
        return error_str;
    }
    
    return nav->display_buffer;
}

/** @} */

/**
 * @defgroup NavigatorMode 导航器模式管理实现
 * @brief 应用模式的设置和获取实现
 * @{
 */

/**
 * @brief 设置应用模式
 * @param nav 导航器指针
 * @param is_app_mode 是否为应用模式
 * @details 设置导航器是否处于应用模式
 */
void navigator_set_app_mode(navigator_t* nav, bool is_app_mode) {
    if (nav) {
        nav->in_app_mode = is_app_mode;
    }
}

/**
 * @brief 获取应用模式状态
 * @param nav 导航器指针
 * @return 是否处于应用模式
 */
bool navigator_get_app_mode(const navigator_t* nav) {
    return nav ? nav->in_app_mode : false;
}

/** @} */

/**
 * @defgroup NavigatorExhibition 展示模式管理实现
 * @brief 展示类型菜单项的分页管理实现
 * @{
 */

/**
 * @brief 检查是否可分页
 * @param nav 导航器指针
 * @return 当前选中项是否支持分页
 * @details 检查当前选中项是否为展示类型且处于解锁状态且有多页
 */
bool navigator_is_exhibition_pageable(const navigator_t* nav) {
    if (!nav || !nav->current_menu || !nav->current_menu->children_items || 
        nav->selected_index >= nav->current_menu->children_count) {
        return false;
    }
    
    menu_item_t* selected_item = nav->current_menu->children_items[nav->selected_index];
    return (selected_item->type == MENU_TYPE_EXHIBITION && 
            !selected_item->is_locked && 
            selected_item->data.exhibition.total_pages > 1);
}

/**
 * @brief 下一页
 * @param nav 导航器指针
 * @details 切换到展示项的下一页
 */
void navigator_exhibition_next_page(navigator_t* nav) {
    if (!nav || !nav->current_menu || !nav->current_menu->children_items || 
        nav->selected_index >= nav->current_menu->children_count) {
        return;
    }
    
    menu_item_t* selected_item = nav->current_menu->children_items[nav->selected_index];
    if (selected_item->type == MENU_TYPE_EXHIBITION && !selected_item->is_locked) {
        menu_item_next_page(selected_item);
    }
}

/**
 * @brief 上一页
 * @param nav 导航器指针
 * @details 切换到展示项的上一页
 */
void navigator_exhibition_prev_page(navigator_t* nav) {
    if (!nav || !nav->current_menu || !nav->current_menu->children_items || 
        nav->selected_index >= nav->current_menu->children_count) {
        return;
    }
    
    menu_item_t* selected_item = nav->current_menu->children_items[nav->selected_index];
    if (selected_item->type == MENU_TYPE_EXHIBITION && !selected_item->is_locked) {
        menu_item_prev_page(selected_item);
    }
}

/**
 * @brief 重置到第一页
 * @param nav 导航器指针
 * @details 将展示项重置到第一页
 */
void navigator_exhibition_reset_to_first_page(navigator_t* nav) {
    if (!nav || !nav->current_menu || !nav->current_menu->children_items || 
        nav->selected_index >= nav->current_menu->children_count) {
        return;
    }
    
    menu_item_t* selected_item = nav->current_menu->children_items[nav->selected_index];
    if (selected_item->type == MENU_TYPE_EXHIBITION && !selected_item->is_locked) {
        selected_item->data.exhibition.current_page = 0;
    }
}

/**
 * @brief 获取当前页码
 * @param nav 导航器指针
 * @return 当前页码（从0开始）
 */
uint8_t navigator_get_exhibition_current_page(const navigator_t* nav) {
    if (!nav || !nav->current_menu || !nav->current_menu->children_items || 
        nav->selected_index >= nav->current_menu->children_count) {
        return 0;
    }
    
    menu_item_t* selected_item = nav->current_menu->children_items[nav->selected_index];
    if (selected_item->type == MENU_TYPE_EXHIBITION) {
        return selected_item->data.exhibition.current_page;
    }
    return 0;
}

/**
 * @brief 获取总页数
 * @param nav 导航器指针
 * @return 总页数
 */
uint8_t navigator_get_exhibition_total_pages(const navigator_t* nav) {
    if (!nav || !nav->current_menu || !nav->current_menu->children_items || 
        nav->selected_index >= nav->current_menu->children_count) {
        return 1;
    }
    
    menu_item_t* selected_item = nav->current_menu->children_items[nav->selected_index];
    if (selected_item->type == MENU_TYPE_EXHIBITION) {
        return selected_item->data.exhibition.total_pages;
    }
    return 1;
}

/** @} */

/**
 * @defgroup NavigatorInfo 导航器信息获取实现
 * @brief 获取当前菜单状态信息的实现
 * @{
 */

/**
 * @brief 获取当前页面名称
 * @param nav 导航器指针
 * @return 当前页面名称字符串
 * @details 返回当前菜单页面的名称，展示模式下包含页码信息
 */
const char* navigator_get_current_page_name(const navigator_t* nav) {
    static char page_name_buffer[MAX_DISPLAY_CHAR * 2] = {0};
    
    if (!nav || !nav->current_menu || !nav->current_menu->children_items || 
        nav->selected_index >= nav->current_menu->children_count) {
        return "Unknown";
    }
    
    menu_item_t* selected_item = nav->current_menu->children_items[nav->selected_index];
    
    if (selected_item->type == MENU_TYPE_EXHIBITION && !selected_item->is_locked) {
        if (selected_item->data.exhibition.total_pages > 1) {
            snprintf(page_name_buffer, sizeof(page_name_buffer), "%s(Page %d/%d)",
                     selected_item->item_name,
                     selected_item->data.exhibition.current_page + 1,
                     selected_item->data.exhibition.total_pages);
        } else {
            snprintf(page_name_buffer, sizeof(page_name_buffer), "%s", selected_item->item_name);
        }
        return page_name_buffer;
    } else {
        return nav->current_menu->item_name;
    }
}

/**
 * @brief 获取当前选中项名称
 * @param nav 导航器指针
 * @return 当前选中菜单项的名称
 */
const char* navigator_get_current_selected_item_name(const navigator_t* nav) {
    if (!nav || !nav->current_menu || !nav->current_menu->children_items || 
        nav->selected_index >= nav->current_menu->children_count) {
        return "Unknown";
    }
    
    return nav->current_menu->children_items[nav->selected_index]->item_name;
}

/**
 * @brief 检查是否处于展示模式
 * @param nav 导航器指针
 * @return 是否处于展示模式
 * @details 判断当前选中项是否为展示类型且处于解锁状态
 */
bool navigator_is_in_exhibition_mode(const navigator_t* nav) {
    if (!nav || !nav->current_menu || !nav->current_menu->children_items || 
        nav->selected_index >= nav->current_menu->children_count) {
        return false;
    }
    
    menu_item_t* selected_item = nav->current_menu->children_items[nav->selected_index];
    return (selected_item->type == MENU_TYPE_EXHIBITION && !selected_item->is_locked);
}
