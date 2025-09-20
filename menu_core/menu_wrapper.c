#include "menu_wrapper.h"
#include "menu_navigator.h"
#include <string.h>
#include <stdio.h>

/**
 * @brief 创建菜单导航器
 * @param mainMenu 主菜单项指针
 * @return 菜单导航器句柄，失败返回NULL
 * @details 将void*类型的主菜单项转换为menu_item_t*并创建导航器
 */
void* menu_builder(void* mainMenu)
{
    return navigator_create((menu_item_t*)mainMenu);
}

/**
 * @brief 销毁菜单导航器
 * @param navigator 菜单导航器句柄
 * @details 将void*类型的导航器转换为navigator_t*并销毁
 */
void menu_delete(void* navigator)
{
    navigator_destroy((navigator_t*)navigator);
}

/**
 * @brief 处理菜单按键输入
 * @param navigator 菜单导航器句柄
 * @param key_value 按键值（UP/DOWN/LEFT/RIGHT/UP_RepeatPress/DOWN_RepeatPress/NONE）
 * @details 将包装器的按键枚举转换为导航器的按键枚举并处理输入
 */
void menu_handle_input(void* navigator, uint8_t key_value)
{
    key_value_t key;
    switch (key_value)
    {
    case UP: key = KEY_UP; break;
    case DOWN: key = KEY_DOWN; break;
    case LEFT: key = KEY_LEFT; break;
    case RIGHT: key = KEY_RIGHT; break;
    case UP_RepeatPress: key = KEY_UP_RepeatPress; break;
    case DOWN_RepeatPress: key = KEY_DOWN_RepeatPress; break;
    default: key = KEY_NONE; break;
    }
    navigator_handle_input((navigator_t*)navigator, key);
}

/**
 * @brief 刷新菜单显示内容
 * @param navigator 菜单导航器句柄
 * @details 调用底层导航器的显示刷新功能
 */
void menu_refresh_display(void* navigator)
{
    navigator_refresh_display((navigator_t*)navigator);
}

/**
 * @brief 获取菜单显示缓冲区
 * @param navigator 菜单导航器句柄
 * @return 显示缓冲区指针
 * @details 返回包含所有菜单显示内容的缓冲区
 */
char* menu_get_display_buffer(void* navigator)
{
    return navigator_get_display_buffer((navigator_t*)navigator);
}

/**
 * @brief 显示菜单内容
 * @param navigator 菜单导航器句柄
 * @details 刷新显示内容并逐行调用menu_show_string函数输出到屏幕
 * @note 此函数会自动处理字符串填充，确保每行都是MAX_DISPLAY_CHAR长度
 */
void menu_display(void* navigator)
{
    menu_refresh_display(navigator);
    char* display_buffer = menu_get_display_buffer(navigator);
    
    for(unsigned char line = 0; line < MAX_DISPLAY_ITEM; line++)
    {
        static char line_buffer[MAX_DISPLAY_CHAR + 1];
        char* line_start = display_buffer + (MAX_DISPLAY_CHAR * line);
        
        // 复制有效字符
        unsigned char len = 0;
        while (len < MAX_DISPLAY_CHAR && line_start[len] != '\0') {
            line_buffer[len] = line_start[len];
            len++;
        }
        // 用空格填充剩余位置
        while (len < MAX_DISPLAY_CHAR) {
            line_buffer[len++] = ' ';
        }
        line_buffer[MAX_DISPLAY_CHAR] = '\0';
        menu_show_string(line, line_buffer);
    }
}

/**
 * @brief 获取菜单应用模式状态
 * @param navigator 菜单导航器句柄
 * @return 应用模式状态（1：应用模式，0：菜单模式）
 * @details 将底层导航器的布尔值转换为uint8_t返回
 */
uint8_t menu_get_app_mode(void* navigator)
{
    return navigator_get_app_mode((navigator_t*)navigator) ? 1 : 0;
}

/**
 * @brief 设置菜单应用模式
 * @param navigator 菜单导航器句柄
 * @param mode 模式值（非0：应用模式，0：菜单模式）
 * @details 将uint8_t类型的模式值转换为布尔值设置到底层导航器
 */
void menu_set_app_mode(void* navigator, uint8_t mode)
{
    navigator_set_app_mode((navigator_t*)navigator, mode != 0);
}

/**
 * @brief 强制刷新菜单显示
 * @param navigator 菜单导航器句柄
 * @details 清空显示缓冲区并强制更新所有显示内容
 */
void menu_force_refresh_display(void* navigator)
{
    navigator_force_refresh_display((navigator_t*)navigator);
}

/**
 * @brief 展示项下一页
 * @param navigator 菜单导航器句柄
 * @details 切换当前展示项到下一页
 */
void menu_exhibition_next_page(void* navigator)
{
    navigator_exhibition_next_page((navigator_t*)navigator);
}

/**
 * @brief 展示项上一页
 * @param navigator 菜单导航器句柄
 * @details 切换当前展示项到上一页
 */
void menu_exhibition_prev_page(void* navigator)
{
    navigator_exhibition_prev_page((navigator_t*)navigator);
}

/**
 * @brief 重置展示项到第一页
 * @param navigator 菜单导航器句柄
 * @details 将当前展示项重置到第一页
 */
void menu_exhibition_reset_to_first_page(void* navigator)
{
    navigator_exhibition_reset_to_first_page((navigator_t*)navigator);
}

/**
 * @brief 获取展示项当前页码
 * @param navigator 菜单导航器句柄
 * @return 当前页码（从0开始）
 * @details 返回当前展示项的页码
 */
uint8_t menu_exhibition_get_current_page(void* navigator)
{
    return navigator_get_exhibition_current_page((navigator_t*)navigator);
}

/**
 * @brief 获取展示项总页数
 * @param navigator 菜单导航器句柄
 * @return 总页数
 * @details 返回当前展示项的总页数
 */
uint8_t menu_exhibition_get_total_pages(void* navigator)
{
    return navigator_get_exhibition_total_pages((navigator_t*)navigator);
}

/**
 * @brief 检查展示项是否可分页
 * @param navigator 菜单导航器句柄
 * @return 是否可分页（1：可分页，0：不可分页）
 * @details 将底层导航器的布尔值转换为uint8_t返回
 */
uint8_t menu_exhibition_is_pageable(void* navigator)
{
    return navigator_is_exhibition_pageable((navigator_t*)navigator) ? 1 : 0;
}

/**
 * @brief 获取当前页面名称
 * @param navigator 菜单导航器句柄
 * @return 当前页面名称字符串
 * @details 返回当前菜单页面的名称，展示模式下包含页码信息
 */
const char* menu_get_current_page_name(void* navigator)
{
    return navigator_get_current_page_name((navigator_t*)navigator);
}

/**
 * @brief 获取当前选中项名称
 * @param navigator 菜单导航器句柄
 * @return 当前选中菜单项的名称
 * @details 返回当前选中菜单项的名称字符串
 */
const char* menu_get_current_selected_item_name(void* navigator)
{
    return navigator_get_current_selected_item_name((navigator_t*)navigator);
}

/**
 * @brief 检查是否处于展示模式
 * @param navigator 菜单导航器句柄
 * @return 是否处于展示模式（1：展示模式，0：普通模式）
 * @details 将底层导航器的布尔值转换为uint8_t返回
 */
uint8_t menu_is_in_exhibition_mode(void* navigator)
{
    return navigator_is_in_exhibition_mode((navigator_t*)navigator) ? 1 : 0;
}

/**
 * @brief 递归查找指定名称的菜单项
 * @param item 当前搜索的菜单项
 * @param name 要查找的菜单项名称
 * @return 找到的菜单项指针，未找到返回NULL
 * @details 在菜单树中递归搜索指定名称的菜单项
 * @note 这是一个静态辅助函数，仅在本文件内使用
 */
static menu_item_t* find_item_by_name(menu_item_t* item, const char* name) {
    if (!item || strcmp(item->item_name, name) == 0) return item;
    
    if (item->children_items) {
        for (uint8_t i = 0; i < item->children_count; i++) {
            menu_item_t* found = find_item_by_name(item->children_items[i], name);
            if (found) return found;
        }
    }
    return NULL;
}

/**
 * @brief 跳转到指定菜单项
 * @param navigator 菜单导航器句柄
 * @param menu_name 目标菜单项名称
 * @details 根据菜单项名称直接跳转到指定的菜单项
 * @note 支持跳转到普通菜单项和展示菜单项
 * @warning 如果菜单项名称不存在，函数将不执行任何操作
 */
void menu_goto(void* navigator, const char* menu_name)
{
    navigator_t* nav = (navigator_t*)navigator;
    if (!nav || !menu_name) return;

    // 如果当前处于应用模式，先退出应用模式
    if (navigator_get_app_mode(nav)) {
        navigator_set_app_mode(nav, false);
    }

    // 找到根菜单项
    menu_item_t* root_item = nav->current_menu;
    while (root_item && root_item->parent_item) {
        root_item = root_item->parent_item;
    }

    // 在菜单树中查找目标菜单项
    menu_item_t* target_item = find_item_by_name(root_item, menu_name);
    if (target_item) {
        if (target_item->type == MENU_TYPE_NORMAL && target_item->children_count > 0) {
            // 跳转到普通菜单项
            nav->current_menu = target_item;
            nav->selected_index = 0;
            nav->first_visible_item = 0;
            navigator_force_refresh_display(nav);
        } else if (target_item->type == MENU_TYPE_EXHIBITION && target_item->parent_item) {
            // 跳转到展示菜单项
            nav->current_menu = target_item->parent_item;
            // 找到目标项在父菜单中的索引
            for (uint8_t i = 0; i < target_item->parent_item->children_count; i++) {
                if (target_item->parent_item->children_items[i] == target_item) {
                    nav->selected_index = i;
                    break;
                }
            }
            // 调整可见范围
            if (nav->selected_index < nav->first_visible_item) {
                nav->first_visible_item = nav->selected_index;
            } else if (nav->selected_index >= nav->first_visible_item + MAX_DISPLAY_ITEM) {
                nav->first_visible_item = nav->selected_index - MAX_DISPLAY_ITEM + 1;
            }
            navigator_force_refresh_display(nav);
            // 自动进入展示模式
            menu_handle_input(nav, RIGHT);
        }
    }
}
