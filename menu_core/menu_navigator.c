#include "menu_navigator.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// 全局内存池
static memory_pool_t g_memory_pool = {0};
static bool g_pool_initialized = false;

// 字符串操作优化辅助函数
static uint32_t fast_hash(const char* str, size_t len);
static void fast_string_build(char* dest, size_t dest_size, const char* prefix, const char* main_str, const char* suffix);
static bool string_content_changed(const char* old_str, const char* new_str, size_t len);

// 数据类型操作辅助函数
static void increment_value_by_type(void* ref, void* step, data_type_t type);
static void decrement_value_by_type(void* ref, void* step, void* min_val, data_type_t type);
static bool is_value_in_range(void* ref, void* min_val, void* max_val, data_type_t type, bool is_increment);
static void format_value_by_type(void* ref, data_type_t type, char* str, size_t size);
static void copy_value_by_type(void* dest, void* src, data_type_t type);

/**
 * @brief 内存池初始化
 */
void memory_pool_init(void) {
    if (g_pool_initialized) return;
    
    memset(&g_memory_pool, 0, sizeof(memory_pool_t));
    g_memory_pool.next_free = 0;
    g_pool_initialized = true;
}

/**
 * @brief 从内存池分配菜单项
 */
menu_item_t* memory_pool_alloc(void) {
    if (!g_pool_initialized) {
        memory_pool_init();
    }
    
    // 从提示位置开始查找
    for (size_t i = g_memory_pool.next_free; i < MENU_POOL_SIZE; i++) {
        if (!g_memory_pool.used[i]) {
            g_memory_pool.used[i] = true;
            g_memory_pool.next_free = i + 1;
            memset(&g_memory_pool.pool[i], 0, sizeof(menu_item_t));
            return &g_memory_pool.pool[i];
        }
    }
    
    // 如果提示位置后面没有，从头开始查找
    for (size_t i = 0; i < g_memory_pool.next_free && i < MENU_POOL_SIZE; i++) {
        if (!g_memory_pool.used[i]) {
            g_memory_pool.used[i] = true;
            g_memory_pool.next_free = i + 1;
            memset(&g_memory_pool.pool[i], 0, sizeof(menu_item_t));
            return &g_memory_pool.pool[i];
        }
    }
    
    return NULL;  // 内存池已满
}

/**
 * @brief 释放菜单项到内存池
 */
void memory_pool_free(menu_item_t* item) {
    if (!item || !g_pool_initialized) return;
    
    // 检查是否在池范围内
    if (item >= g_memory_pool.pool && item < g_memory_pool.pool + MENU_POOL_SIZE) {
        size_t index = item - g_memory_pool.pool;
        g_memory_pool.used[index] = false;
        if (index < g_memory_pool.next_free) {
            g_memory_pool.next_free = index;  // 更新提示位置
        }
    }
}

/**
 * @brief 获取内存池使用率
 */
size_t memory_pool_get_usage(void) {
    if (!g_pool_initialized) return 0;
    
    size_t used_count = 0;
    for (size_t i = 0; i < MENU_POOL_SIZE; i++) {
        if (g_memory_pool.used[i]) {
            used_count++;
        }
    }
    return used_count;
}

/**
 * @brief 快速哈希函数 (DJB2算法)
 */
static uint32_t fast_hash(const char* str, size_t len) {
    uint32_t hash = 5381;
    for (size_t i = 0; i < len && str[i] != '\0'; i++) {
        hash = ((hash << 5) + hash) + (uint8_t)str[i];
    }
    return hash;
}

/**
 * @brief 快速字符串构建
 */
static void fast_string_build(char* dest, size_t dest_size, const char* prefix, const char* main_str, const char* suffix) {
    char* ptr = dest;
    size_t remaining = dest_size - 1;  // 保留\0空间
    
    // 复制前缀
    if (prefix && remaining > 0) {
        while (*prefix && remaining > 0) {
            *ptr++ = *prefix++;
            remaining--;
        }
    }
    
    // 复制主字符串
    if (main_str && remaining > 0) {
        while (*main_str && remaining > 0) {
            *ptr++ = *main_str++;
            remaining--;
        }
    }
    
    // 复制后缀
    if (suffix && remaining > 0) {
        while (*suffix && remaining > 0) {
            *ptr++ = *suffix++;
            remaining--;
        }
    }
    
    *ptr = '\0';
}

/**
 * @brief 检查字符串内容是否变化
 */
static bool string_content_changed(const char* old_str, const char* new_str, size_t len) {
    if (!old_str || !new_str) return true;
    return strncmp(old_str, new_str, len) != 0;
}

/**
 * @brief 创建普通菜单项
 */
menu_item_t* menu_create_normal_item(const char* name, menu_item_t** children_items, uint8_t count) {
    menu_item_t* item = memory_pool_alloc();
    if (!item) return NULL;
    
    memset(item, 0, sizeof(menu_item_t));
    item->is_locked = true;
    item->item_name = name;
    item->children_items = children_items;
    item->children_count = count;
    item->type = MENU_TYPE_NORMAL;
    
    // 设置父子关系
    if (children_items) {
        for (uint8_t i = 0; i < count; i++) {
            if (children_items[i]) {
                children_items[i]->parent_item = item;
            }
        }
    }
    
    return item;
}

/**
 * @brief 创建可变菜单项
 */
menu_item_t* menu_create_changeable_item(const char* name, void* ref, void* min_val, void* max_val, 
                                         void* step_val, data_type_t data_type, void (*on_change)(void*)) {
    menu_item_t* item = memory_pool_alloc();
    if (!item) return NULL;
    
    memset(item, 0, sizeof(menu_item_t));
    item->is_locked = true;
    item->item_name = name;
    item->type = MENU_TYPE_CHANGEABLE;
    
    item->data.changeable.ref = ref;
    item->data.changeable.min_val = min_val;
    item->data.changeable.max_val = max_val;
    item->data.changeable.step_val = step_val;
    item->data.changeable.data_type = data_type;
    item->data.changeable.on_change = on_change;
    
    return item;
}

/**
 * @brief 创建切换菜单项
 */
menu_item_t* menu_create_toggle_item(const char* name, bool* ref, void (*on_toggle)(bool)) {
    menu_item_t* item = memory_pool_alloc();
    if (!item) return NULL;
    
    memset(item, 0, sizeof(menu_item_t));
    item->is_locked = true;
    item->item_name = name;
    item->type = MENU_TYPE_TOGGLE;
    
    item->data.toggle.ref = ref;
    item->data.toggle.state = ref ? *ref : false;
    item->data.toggle.on_toggle = on_toggle;
    
    return item;
}

/**
 * @brief 创建应用菜单项
 */
menu_item_t* menu_create_app_item(const char* name, void** app_args, void (*app_func)(void**)) {
    menu_item_t* item = memory_pool_alloc();
    if (!item) return NULL;
    
    memset(item, 0, sizeof(menu_item_t));
    item->is_locked = true;
    item->item_name = name;
    item->type = MENU_TYPE_NORMAL;
    item->app_func = app_func;
    item->app_args = app_args;
    
    return item;
}

/**
 * @brief 创建展示菜单项
 * @param name 菜单项名称
 * @param total_pages 总页数，当页数为1时采用Nav模式显示，当页数大于1时采用Page模式显示
 * @param callback 回调函数，参数为(navigator_t* nav, uint8_t current_page, uint8_t total_pages)
 */
menu_item_t* menu_create_exhibition_item(const char* name, uint8_t total_pages, 
                                        void (*callback)(navigator_t*, uint8_t, uint8_t)) {
    menu_item_t* item = memory_pool_alloc();
    if (!item) return NULL;
    
    memset(item, 0, sizeof(menu_item_t));
    item->is_locked = true;
    item->item_name = name;
    item->type = MENU_TYPE_EXHIBITION;
    item->periodic_callback_with_page = callback;
    item->data.exhibition.total_pages = total_pages > 0 ? total_pages : 1;
    item->data.exhibition.current_page = 0;
    item->data.exhibition.lines_per_page = MAX_DISPLAY_ITEM - 1;
    
    return item;
}

/**
 * @brief 创建带导航器的展示菜单项（已废弃，为了兼容性保留）
 */
menu_item_t* menu_create_exhibition_item_with_nav(const char* name, void (*callback)(navigator_t*)) {
    // 为了兼容性，转换为新的统一接口
    // Nav模式相当于total_pages=1的情况
    return menu_create_exhibition_item(name, 1, (void (*)(navigator_t*, uint8_t, uint8_t))callback);
}

/**
 * @brief 创建带分页的展示菜单项（已废弃，为了兼容性保留）
 */
menu_item_t* menu_create_exhibition_item_with_page(const char* name, uint8_t total_pages, 
                                                   void (*callback)(navigator_t*, uint8_t, uint8_t)) {
    // 直接使用新的统一接口
    return menu_create_exhibition_item(name, total_pages, callback);
}

/**
 * @brief 菜单项切换操作
 */
void menu_item_toggle(menu_item_t* item) {
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
 * @brief 菜单项递增操作
 */
void menu_item_increment(menu_item_t* item) {
    if (!item || item->type != MENU_TYPE_CHANGEABLE) return;
    
    changeable_data_t* data = &item->data.changeable;
    
    if (is_value_in_range(data->ref, data->min_val, data->max_val, data->data_type, true)) {
        increment_value_by_type(data->ref, data->step_val, data->data_type);
        
        if (data->on_change) {
            data->on_change(data->ref);
        }
    }
}

/**
 * @brief 菜单项递减操作
 */
void menu_item_decrement(menu_item_t* item) {
    if (!item || item->type != MENU_TYPE_CHANGEABLE) return;
    
    changeable_data_t* data = &item->data.changeable;
    
    if (is_value_in_range(data->ref, data->min_val, data->max_val, data->data_type, false)) {
        decrement_value_by_type(data->ref, data->step_val, data->min_val, data->data_type);
        
        if (data->on_change) {
            data->on_change(data->ref);
        }
    }
}

/**
 * @brief 获取菜单项值字符串
 */
void menu_item_get_value_str(const menu_item_t* item, char* value_str, size_t size) {
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
 * @brief 设置展示项总页数
 */
void menu_item_set_total_pages(menu_item_t* item, uint8_t total_pages) {
    if (!item || item->type != MENU_TYPE_EXHIBITION) return;
    
    item->data.exhibition.total_pages = total_pages > 0 ? total_pages : 1;
    if (item->data.exhibition.current_page >= item->data.exhibition.total_pages) {
        item->data.exhibition.current_page = item->data.exhibition.total_pages - 1;
    }
}

/**
 * @brief 获取展示项当前页
 */
uint8_t menu_item_get_current_page(const menu_item_t* item) {
    if (!item || item->type != MENU_TYPE_EXHIBITION) return 0;
    return item->data.exhibition.current_page;
}

/**
 * @brief 获取展示项总页数
 */
uint8_t menu_item_get_total_pages(const menu_item_t* item) {
    if (!item || item->type != MENU_TYPE_EXHIBITION) return 1;
    return item->data.exhibition.total_pages;
}

/**
 * @brief 展示项下一页
 */
void menu_item_next_page(menu_item_t* item) {
    if (!item || item->type != MENU_TYPE_EXHIBITION || item->data.exhibition.total_pages <= 1) return;
    
    item->data.exhibition.current_page = (item->data.exhibition.current_page + 1) % item->data.exhibition.total_pages;
}

/**
 * @brief 展示项上一页
 */
void menu_item_prev_page(menu_item_t* item) {
    if (!item || item->type != MENU_TYPE_EXHIBITION || item->data.exhibition.total_pages <= 1) return;
    
    item->data.exhibition.current_page = (item->data.exhibition.current_page == 0) 
        ? (item->data.exhibition.total_pages - 1) 
        : (item->data.exhibition.current_page - 1);
}

/**
 * @brief 展示项重置到第一页
 */
void menu_item_reset_to_first_page(menu_item_t* item) {
    if (!item || item->type != MENU_TYPE_EXHIBITION) return;
    item->data.exhibition.current_page = 0;
}

/**
 * @brief 创建导航器
 */
navigator_t* navigator_create(menu_item_t* main_item) {
    if (!main_item) return NULL;
    
    navigator_t* nav = (navigator_t*)malloc(sizeof(navigator_t));
    if (!nav) return NULL;
    
    memset(nav, 0, sizeof(navigator_t));
    nav->current_menu = main_item;
    nav->in_app_mode = false;
    nav->selected_index = 0;
    nav->first_visible_item = 0;
    nav->app_saved_selected_index = 0;
    nav->saved_first_visible_item_before_exhibition = 0;
    
    // 初始化显示行管理
    for (uint8_t i = 0; i < MAX_DISPLAY_ITEM; i++) {
        nav->display_lines[i].state = LINE_STATE_FORCE_UPDATE;
        nav->display_lines[i].hash = 0;
        memset(nav->display_lines[i].content, 0, MAX_DISPLAY_CHAR);
    }
    
    return nav;
}

/**
 * @brief 销毁导航器
 */
void navigator_destroy(navigator_t* nav) {
    if (nav) {
        free(nav);
    }
}

/**
 * @brief 处理按键输入
 */
void navigator_handle_input(navigator_t* nav, key_value_t key_value) {
    if (!nav || !nav->current_menu || !nav->current_menu->children_items) return;
    
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
                case MENU_TYPE_NORMAL:
                    nav->selected_index = (nav->selected_index == 0) 
                        ? (nav->current_menu->children_count - 1) 
                        : (nav->selected_index - 1);
                    if (nav->selected_index == nav->current_menu->children_count - 1) {
                        if (nav->current_menu->children_count > MAX_DISPLAY_ITEM) {
                            memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                        }
                        nav->first_visible_item = nav->selected_index - (nav->selected_index % MAX_DISPLAY_ITEM);
                    }
                    break;
                    
                case MENU_TYPE_EXHIBITION:
                    if (current_item->is_locked) {
                        nav->selected_index = (nav->selected_index == 0) 
                            ? (nav->current_menu->children_count - 1) 
                            : (nav->selected_index - 1);
                        if (nav->selected_index == nav->current_menu->children_count - 1) {
                            if (nav->current_menu->children_count > MAX_DISPLAY_ITEM) {
                                memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                            }
                            nav->first_visible_item = nav->selected_index - (nav->selected_index % MAX_DISPLAY_ITEM);
                        }
                    } else {
                        menu_item_prev_page(current_item);
                    }
                    break;
                    
                case MENU_TYPE_CHANGEABLE:
                    if (!current_item->is_locked) {
                        menu_item_increment(current_item);
                    } else {
                        nav->selected_index = (nav->selected_index == 0) 
                            ? (nav->current_menu->children_count - 1) 
                            : (nav->selected_index - 1);
                        if (nav->selected_index == nav->current_menu->children_count - 1) {
                            if (nav->current_menu->children_count > MAX_DISPLAY_ITEM) {
                                memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                            }
                            nav->first_visible_item = nav->selected_index - (nav->selected_index % MAX_DISPLAY_ITEM);
                        }
                    }
                    break;
                    
                case MENU_TYPE_TOGGLE:
                    if (!current_item->is_locked) {
                        menu_item_toggle(current_item);
                    } else {
                        nav->selected_index = (nav->selected_index == 0) 
                            ? (nav->current_menu->children_count - 1) 
                            : (nav->selected_index - 1);
                        if (nav->selected_index == nav->current_menu->children_count - 1) {
                            if (nav->current_menu->children_count > MAX_DISPLAY_ITEM) {
                                memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                            }
                            nav->first_visible_item = nav->selected_index - (nav->selected_index % MAX_DISPLAY_ITEM);
                        }
                    }
                    break;
            }
            break;
            
        case KEY_DOWN:
            switch (current_item->type) {
                case MENU_TYPE_NORMAL:
                    nav->selected_index = (nav->selected_index + 1) % nav->current_menu->children_count;
                    if (nav->selected_index == 0) {
                        if (nav->current_menu->children_count > MAX_DISPLAY_ITEM) {
                            memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                        }
                        nav->first_visible_item = 0;
                    }
                    break;
                    
                case MENU_TYPE_EXHIBITION:
                    if (current_item->is_locked) {
                        nav->selected_index = (nav->selected_index + 1) % nav->current_menu->children_count;
                        if (nav->selected_index == 0) {
                            if (nav->current_menu->children_count > MAX_DISPLAY_ITEM) {
                                memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                            }
                            nav->first_visible_item = 0;
                        }
                    } else {
                        menu_item_next_page(current_item);
                    }
                    break;
                    
                case MENU_TYPE_CHANGEABLE:
                    if (!current_item->is_locked) {
                        menu_item_decrement(current_item);
                    } else {
                        nav->selected_index = (nav->selected_index + 1) % nav->current_menu->children_count;
                        if (nav->selected_index == 0) {
                            if (nav->current_menu->children_count > MAX_DISPLAY_ITEM) {
                                memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                            }
                            nav->first_visible_item = 0;
                        }
                    }
                    break;
                    
                case MENU_TYPE_TOGGLE:
                    if (!current_item->is_locked) {
                        menu_item_toggle(current_item);
                    } else {
                        nav->selected_index = (nav->selected_index + 1) % nav->current_menu->children_count;
                        if (nav->selected_index == 0) {
                            if (nav->current_menu->children_count > MAX_DISPLAY_ITEM) {
                                memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                            }
                            nav->first_visible_item = 0;
                        }
                    }
                    break;
            }
            break;
            
        case KEY_RIGHT:
            switch (current_item->type) {
                case MENU_TYPE_NORMAL:
                    if (current_item->children_count > 0) {
                        memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                        navigator_mark_all_lines_dirty(nav);  // 标记所有行为脏，确保完全刷新
                        nav->current_menu->saved_selected_index = nav->selected_index;
                        nav->current_menu->saved_first_visible_item = nav->first_visible_item;
                        nav->current_menu = current_item;
                        nav->selected_index = 0;
                        nav->first_visible_item = 0;
                    } else if (current_item->app_func) {
                        memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                        navigator_mark_all_lines_dirty(nav);  // 标记所有行为脏，确保完全刷新
                        nav->in_app_mode = true;
                        nav->app_saved_selected_index = nav->selected_index;
                        current_item->app_func(current_item->app_args);
                    }
                    break;
                    
                case MENU_TYPE_EXHIBITION:
                    if (current_item->is_locked) {
                        current_item->is_locked = false;
                        menu_item_reset_to_first_page(current_item);
                        nav->saved_first_visible_item_before_exhibition = nav->first_visible_item;
                        nav->first_visible_item = nav->selected_index;
                        if (nav->current_menu->children_count > MAX_DISPLAY_ITEM) {
                            memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                            navigator_mark_all_lines_dirty(nav);  // 标记所有行为脏，确保完全刷新
                        }
                    }
                    break;
                    
                case MENU_TYPE_CHANGEABLE:
                case MENU_TYPE_TOGGLE:
                    current_item->is_locked = false;
                    break;
            }
            break;
            
        case KEY_LEFT:
            switch (current_item->type) {
                case MENU_TYPE_NORMAL:
                    if (nav->current_menu->parent_item) {
                        memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                        navigator_mark_all_lines_dirty(nav);  // 标记所有行为脏，确保完全刷新
                        nav->current_menu = nav->current_menu->parent_item;
                        nav->selected_index = nav->current_menu->saved_selected_index;
                        nav->first_visible_item = nav->current_menu->saved_first_visible_item;
                    }
                    break;
                    
                case MENU_TYPE_EXHIBITION:
                    if (!current_item->is_locked) {
                        current_item->is_locked = true;
                        nav->first_visible_item = nav->saved_first_visible_item_before_exhibition;
                        memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                        navigator_mark_all_lines_dirty(nav);  // 标记所有行为脏，确保完全刷新
                    } else {
                        if (nav->current_menu->parent_item) {
                            memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                            navigator_mark_all_lines_dirty(nav);  // 标记所有行为脏，确保完全刷新
                            nav->current_menu = nav->current_menu->parent_item;
                            nav->selected_index = nav->current_menu->saved_selected_index;
                            nav->first_visible_item = nav->current_menu->saved_first_visible_item;
                        }
                    }
                    break;
                    
                case MENU_TYPE_CHANGEABLE:
                case MENU_TYPE_TOGGLE:
                    if (!current_item->is_locked) {
                        current_item->is_locked = true;
                    } else {
                        if (nav->current_menu->parent_item) {
                            memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                            navigator_mark_all_lines_dirty(nav);  // 标记所有行为脏，确保完全刷新
                            nav->current_menu = nav->current_menu->parent_item;
                            nav->selected_index = nav->current_menu->saved_selected_index;
                            nav->first_visible_item = nav->current_menu->saved_first_visible_item;
                        }
                    }
                    break;
            }
            break;
            
        default:
            break;
    }
    
    // 处理可见项范围
    if (nav->current_menu->children_count > MAX_DISPLAY_ITEM) {
        if (nav->selected_index >= nav->first_visible_item + MAX_DISPLAY_ITEM) {
            memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
            navigator_mark_all_lines_dirty(nav);  // 标记优化更新
            nav->first_visible_item += MAX_DISPLAY_ITEM;
        } else if (nav->selected_index < nav->first_visible_item && nav->selected_index != 0) {
            memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
            navigator_mark_all_lines_dirty(nav);  // 标记优化更新
            nav->first_visible_item = nav->selected_index - (nav->selected_index % MAX_DISPLAY_ITEM);
        }
    }
}

/**
 * @brief 刷新显示（使用优化版本）
 */
void navigator_refresh_display(navigator_t* nav) {
    if (!nav || !nav->current_menu) return;
    
    // 执行选中的展示项回调
    menu_item_t* selected_item = nav->current_menu->children_items[nav->selected_index];
    if (selected_item->type == MENU_TYPE_EXHIBITION && !selected_item->is_locked) {
        // 先写标题和页面信息
        uint8_t title_line = nav->selected_index - nav->first_visible_item;
        char title_buffer[MAX_DISPLAY_CHAR];
        
        // 统一使用新的显示逻辑：当页数为1时不显示页码，当页数大于1时显示页码
        if (selected_item->data.exhibition.total_pages > 1) {
            fast_string_build(title_buffer, MAX_DISPLAY_CHAR, MENU_HAS_SUBMENU_INDICATOR, selected_item->item_name, "");
            // 添加分页信息
            char page_info[16];
            snprintf(page_info, sizeof(page_info), "(%d/%d):", 
                    selected_item->data.exhibition.current_page + 1,
                    selected_item->data.exhibition.total_pages);
            strncat(title_buffer, page_info, MAX_DISPLAY_CHAR - strlen(title_buffer) - 1);
        } else {
            fast_string_build(title_buffer, MAX_DISPLAY_CHAR, MENU_HAS_SUBMENU_INDICATOR, selected_item->item_name, ":");
        }
        
        navigator_write_display_line(nav, title_buffer, title_line);
        
        // 在执行回调之前，先清空所有可能的显示行（除了标题行）
        for (uint8_t i = 1; i < MAX_DISPLAY_ITEM; i++) {
            navigator_write_display_line(nav, "", i);
        }
        
        // 统一使用带分页参数的回调函数
        if (selected_item->periodic_callback_with_page) {
            selected_item->periodic_callback_with_page(nav, 
                selected_item->data.exhibition.current_page,
                selected_item->data.exhibition.total_pages);
        }
        return;
    }
    
    static char line_buffer[MAX_DISPLAY_CHAR];
    static char value_str[MAX_DISPLAY_CHAR];
    
    if (!nav->in_app_mode) {
        uint8_t visible_count = (nav->current_menu->children_count - nav->first_visible_item < MAX_DISPLAY_ITEM)
            ? (nav->current_menu->children_count - nav->first_visible_item)
            : MAX_DISPLAY_ITEM;
            
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
                        strncat(line_buffer, value_str, MAX_DISPLAY_CHAR - strlen(line_buffer) - 1);
                    } else {
                        fast_string_build(line_buffer, MAX_DISPLAY_CHAR, MENU_HAS_SUBMENU_INDICATOR, item->item_name, ": ");
                        strncat(line_buffer, value_str, MAX_DISPLAY_CHAR - strlen(line_buffer) - 1);
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
 * @brief 设置应用模式
 */
void navigator_set_app_mode(navigator_t* nav, bool is_app_mode) {
    if (nav) {
        nav->in_app_mode = is_app_mode;
    }
}

/**
 * @brief 获取应用模式
 */
bool navigator_get_app_mode(const navigator_t* nav) {
    return nav ? nav->in_app_mode : false;
}

/**
 * @brief 获取显示缓冲区
 */
char* navigator_get_display_buffer(navigator_t* nav) {
    static char error_str[] = "No Menu Item";
    
    if (!nav || !nav->current_menu || !nav->current_menu->children_items) {
        return error_str;
    }
    
    return nav->display_buffer;
}

/**
 * @brief 写入显示缓冲区
 */
void navigator_write_display_buffer(navigator_t* nav, const char* buffer, size_t size, uint8_t first_line) {
    if (!nav || !buffer) return;
    
    memcpy(&nav->display_buffer[MAX_DISPLAY_CHAR * first_line], buffer, size);
}

/**
 * @brief 优化版本的写入显示行（增量更新）
 */
void navigator_write_display_line(navigator_t* nav, const char* buffer, uint8_t line) {
    if (!nav || !buffer || line >= MAX_DISPLAY_ITEM) return;
    
    // 计算新内容的哈希值
    uint32_t new_hash = fast_hash(buffer, MAX_DISPLAY_CHAR);
    
    // 检查是否需要更新
    if (nav->display_lines[line].state == LINE_STATE_FORCE_UPDATE || 
        nav->display_lines[line].hash != new_hash ||
        string_content_changed(nav->display_lines[line].content, buffer, MAX_DISPLAY_CHAR)) {
        
        // 更新内容
        memset(nav->display_lines[line].content, 0, MAX_DISPLAY_CHAR);
        strncpy(nav->display_lines[line].content, buffer, MAX_DISPLAY_CHAR - 1);
        nav->display_lines[line].hash = new_hash;
        nav->display_lines[line].state = LINE_STATE_UNCHANGED;
        
        // 同步到兼容缓冲区
        memset(&nav->display_buffer[MAX_DISPLAY_CHAR * line], 0, MAX_DISPLAY_CHAR);
        strncpy(&nav->display_buffer[MAX_DISPLAY_CHAR * line], buffer, MAX_DISPLAY_CHAR - 1);
    }
}

/**
 * @brief 强制刷新显示
 */
void navigator_force_refresh_display(navigator_t* nav) {
    if (!nav) return;
    
    memset(nav->display_buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
    navigator_mark_all_lines_dirty(nav);  // 标记所有行为脏，确保完全刷新
    navigator_refresh_display(nav);
}



/**
 * @brief 标记所有行为脏（需要强制更新）
 */
void navigator_mark_all_lines_dirty(navigator_t* nav) {
    if (!nav) return;
    
    for (uint8_t i = 0; i < MAX_DISPLAY_ITEM; i++) {
        nav->display_lines[i].state = LINE_STATE_FORCE_UPDATE;
    }
}



// 展示项分页相关函数
/**
 * @brief 检查展示项是否支持分页
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
 * @brief 展示项下一页
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
 * @brief 展示项上一页
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
 * @brief 展示项重置到第一页
 */
void navigator_exhibition_reset_to_first_page(navigator_t* nav) {
    if (!nav || !nav->current_menu || !nav->current_menu->children_items || 
        nav->selected_index >= nav->current_menu->children_count) {
        return;
    }
    
    menu_item_t* selected_item = nav->current_menu->children_items[nav->selected_index];
    if (selected_item->type == MENU_TYPE_EXHIBITION) {
        menu_item_reset_to_first_page(selected_item);
    }
}

/**
 * @brief 获取展示项当前页
 */
uint8_t navigator_get_exhibition_current_page(const navigator_t* nav) {
    if (!nav || !nav->current_menu || !nav->current_menu->children_items || 
        nav->selected_index >= nav->current_menu->children_count) {
        return 0;
    }
    
    menu_item_t* selected_item = nav->current_menu->children_items[nav->selected_index];
    if (selected_item->type == MENU_TYPE_EXHIBITION) {
        return menu_item_get_current_page(selected_item);
    }
    return 0;
}

/**
 * @brief 获取展示项总页数
 */
uint8_t navigator_get_exhibition_total_pages(const navigator_t* nav) {
    if (!nav || !nav->current_menu || !nav->current_menu->children_items || 
        nav->selected_index >= nav->current_menu->children_count) {
        return 1;
    }
    
    menu_item_t* selected_item = nav->current_menu->children_items[nav->selected_index];
    if (selected_item->type == MENU_TYPE_EXHIBITION) {
        return menu_item_get_total_pages(selected_item);
    }
    return 1;
}

/**
 * @brief 获取当前页面名称
 */
const char* navigator_get_current_page_name(const navigator_t* nav) {
    static char page_name_buffer[MAX_DISPLAY_CHAR * 2] = {0};
    
    if (!nav || !nav->current_menu || !nav->current_menu->children_items || 
        nav->selected_index >= nav->current_menu->children_count) {
        return "Unknown";
    }
    
    menu_item_t* selected_item = nav->current_menu->children_items[nav->selected_index];
    
    if (selected_item->type == MENU_TYPE_EXHIBITION && !selected_item->is_locked) {
        // 在展示模式下，返回带分页信息的项名称
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
        // 返回当前菜单名称
        return nav->current_menu->item_name;
    }
}

/**
 * @brief 获取当前选中的菜单项名称
 */
const char* navigator_get_current_selected_item_name(const navigator_t* nav) {
    if (!nav || !nav->current_menu || !nav->current_menu->children_items || 
        nav->selected_index >= nav->current_menu->children_count) {
        return "Unknown";
    }
    
    return nav->current_menu->children_items[nav->selected_index]->item_name;
}

/**
 * @brief 检查是否在展示模式
 */
bool navigator_is_in_exhibition_mode(const navigator_t* nav) {
    if (!nav || !nav->current_menu || !nav->current_menu->children_items || 
        nav->selected_index >= nav->current_menu->children_count) {
        return false;
    }
    
    menu_item_t* selected_item = nav->current_menu->children_items[nav->selected_index];
    return (selected_item->type == MENU_TYPE_EXHIBITION && !selected_item->is_locked);
}

// 数据类型操作辅助函数实现
/**
 * @brief 按类型递增值
 */
static void increment_value_by_type(void* ref, void* step, data_type_t type) {
    switch (type) {
        case DATA_TYPE_UINT8:
            *(uint8_t*)ref += *(uint8_t*)step;
            break;
        case DATA_TYPE_UINT16:
            *(uint16_t*)ref += *(uint16_t*)step;
            break;
        case DATA_TYPE_UINT32:
            *(uint32_t*)ref += *(uint32_t*)step;
            break;
        case DATA_TYPE_UINT64:
            *(uint64_t*)ref += *(uint64_t*)step;
            break;
        case DATA_TYPE_INT8:
            *(int8_t*)ref += *(int8_t*)step;
            break;
        case DATA_TYPE_INT16:
            *(int16_t*)ref += *(int16_t*)step;
            break;
        case DATA_TYPE_INT32:
            *(int32_t*)ref += *(int32_t*)step;
            break;
        case DATA_TYPE_INT64:
            *(int64_t*)ref += *(int64_t*)step;
            break;
        case DATA_TYPE_FLOAT:
            *(float*)ref += *(float*)step;
            break;
        case DATA_TYPE_DOUBLE:
            *(double*)ref += *(double*)step;
            break;
    }
}

/**
 * @brief 按类型递减值
 */
static void decrement_value_by_type(void* ref, void* step, void* min_val, data_type_t type) {
    switch (type) {
        case DATA_TYPE_UINT8:
            *(uint8_t*)ref -= *(uint8_t*)step;
            break;
        case DATA_TYPE_UINT16:
            *(uint16_t*)ref -= *(uint16_t*)step;
            break;
        case DATA_TYPE_UINT32:
            *(uint32_t*)ref -= *(uint32_t*)step;
            break;
        case DATA_TYPE_UINT64:
            *(uint64_t*)ref -= *(uint64_t*)step;
            break;
        case DATA_TYPE_INT8:
            *(int8_t*)ref -= *(int8_t*)step;
            break;
        case DATA_TYPE_INT16:
            *(int16_t*)ref -= *(int16_t*)step;
            break;
        case DATA_TYPE_INT32:
            *(int32_t*)ref -= *(int32_t*)step;
            break;
        case DATA_TYPE_INT64:
            *(int64_t*)ref -= *(int64_t*)step;
            break;
        case DATA_TYPE_FLOAT:
            *(float*)ref -= *(float*)step;
            break;
        case DATA_TYPE_DOUBLE:
            *(double*)ref -= *(double*)step;
            break;
    }
}

/**
 * @brief 检查值是否在范围内
 */
static bool is_value_in_range(void* ref, void* min_val, void* max_val, data_type_t type, bool is_increment) {
    switch (type) {
        case DATA_TYPE_UINT8:
            if (is_increment) {
                return (*(uint8_t*)ref <= *(uint8_t*)max_val);
            } else {
                return (*(uint8_t*)ref >= *(uint8_t*)min_val);
            }
        case DATA_TYPE_UINT16:
            if (is_increment) {
                return (*(uint16_t*)ref <= *(uint16_t*)max_val);
            } else {
                return (*(uint16_t*)ref >= *(uint16_t*)min_val);
            }
        case DATA_TYPE_UINT32:
            if (is_increment) {
                return (*(uint32_t*)ref <= *(uint32_t*)max_val);
            } else {
                return (*(uint32_t*)ref >= *(uint32_t*)min_val);
            }
        case DATA_TYPE_UINT64:
            if (is_increment) {
                return (*(uint64_t*)ref <= *(uint64_t*)max_val);
            } else {
                return (*(uint64_t*)ref >= *(uint64_t*)min_val);
            }
        case DATA_TYPE_INT8:
            if (is_increment) {
                return (*(int8_t*)ref <= *(int8_t*)max_val);
            } else {
                return (*(int8_t*)ref >= *(int8_t*)min_val);
            }
        case DATA_TYPE_INT16:
            if (is_increment) {
                return (*(int16_t*)ref <= *(int16_t*)max_val);
            } else {
                return (*(int16_t*)ref >= *(int16_t*)min_val);
            }
        case DATA_TYPE_INT32:
            if (is_increment) {
                return (*(int32_t*)ref <= *(int32_t*)max_val);
            } else {
                return (*(int32_t*)ref >= *(int32_t*)min_val);
            }
        case DATA_TYPE_INT64:
            if (is_increment) {
                return (*(int64_t*)ref <= *(int64_t*)max_val);
            } else {
                return (*(int64_t*)ref >= *(int64_t*)min_val);
            }
        case DATA_TYPE_FLOAT:
            if (is_increment) {
                return (*(float*)ref <= *(float*)max_val);
            } else {
                return (*(float*)ref >= *(float*)min_val);
            }
        case DATA_TYPE_DOUBLE:
            if (is_increment) {
                return (*(double*)ref <= *(double*)max_val);
            } else {
                return (*(double*)ref >= *(double*)min_val);
            }
    }
    return false;
}

/**
 * @brief 按类型格式化值
 */
static void format_value_by_type(void* ref, data_type_t type, char* str, size_t size) {
    switch (type) {
        case DATA_TYPE_UINT8:
        case DATA_TYPE_UINT16:
            snprintf(str, size, "%u", *(uint16_t*)ref);
            break;
        case DATA_TYPE_UINT32:
            snprintf(str, size, "%lu", *(uint32_t*)ref);
            break;
        case DATA_TYPE_UINT64:
            snprintf(str, size, "%llu", *(uint64_t*)ref);
            break;
        case DATA_TYPE_INT8:
        case DATA_TYPE_INT16:
            snprintf(str, size, "%d", *(int16_t*)ref);
            break;
        case DATA_TYPE_INT32:
            snprintf(str, size, "%ld", *(int32_t*)ref);
            break;
        case DATA_TYPE_INT64:
            snprintf(str, size, "%lld", *(int64_t*)ref);
            break;
        case DATA_TYPE_FLOAT:
            snprintf(str, size, "%.3f", *(float*)ref);
            break;
        case DATA_TYPE_DOUBLE:
            snprintf(str, size, "%.6f", *(double*)ref);
            break;
        default:
            snprintf(str, size, "<?>");
            break;
    }
}

/**
 * @brief 按类型复制值
 */
static void copy_value_by_type(void* dest, void* src, data_type_t type) {
    switch (type) {
        case DATA_TYPE_UINT8:
            *(uint8_t*)dest = *(uint8_t*)src;
            break;
        case DATA_TYPE_UINT16:
            *(uint16_t*)dest = *(uint16_t*)src;
            break;
        case DATA_TYPE_UINT32:
            *(uint32_t*)dest = *(uint32_t*)src;
            break;
        case DATA_TYPE_UINT64:
            *(uint64_t*)dest = *(uint64_t*)src;
            break;
        case DATA_TYPE_INT8:
            *(int8_t*)dest = *(int8_t*)src;
            break;
        case DATA_TYPE_INT16:
            *(int16_t*)dest = *(int16_t*)src;
            break;
        case DATA_TYPE_INT32:
            *(int32_t*)dest = *(int32_t*)src;
            break;
        case DATA_TYPE_INT64:
            *(int64_t*)dest = *(int64_t*)src;
            break;
        case DATA_TYPE_FLOAT:
            *(float*)dest = *(float*)src;
            break;
        case DATA_TYPE_DOUBLE:
            *(double*)dest = *(double*)src;
            break;
    }
}

