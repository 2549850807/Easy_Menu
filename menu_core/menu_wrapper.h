#ifndef MENU_C_WRAPPER_H
#define MENU_C_WRAPPER_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief 显示字符串函数指针
 * @param line 显示行号
 * @param str 要显示的字符串
 * @details 用户需要实现此函数来处理实际的显示输出
 * @note 此函数需要用户在外部实现
 */
void menu_show_string(unsigned char line, char* str);

/**
 * @defgroup MenuKeys 菜单按键枚举
 * @brief 菜单系统支持的按键定义
 * @{
 */
enum
{
    UP,     /**< 上键 */
    DOWN,   /**< 下键 */
    LEFT,   /**< 左键 */
    RIGHT,  /**< 右键 */
    UP_RepeatPress,   /**<  上键长按 */
    DOWN_RepeatPress,  /**< 下键长按*/
    NONE,   /**< 无按键 */
};
/** @} */

/**
 * @defgroup MenuCore 菜单核心功能
 * @brief 菜单系统的基本创建、销毁和操作功能
 * @{
 */

/**
 * @brief 创建菜单导航器
 * @param mainMenu 主菜单项指针
 * @return 菜单导航器句柄，失败返回NULL
 * @details 根据主菜单项创建菜单导航器实例
 */
void* menu_builder(void* mainMenu);

/**
 * @brief 销毁菜单导航器
 * @param navigator 菜单导航器句柄
 * @details 释放菜单导航器占用的资源
 */
void menu_delete(void* navigator);

/**
 * @brief 处理菜单按键输入
 * @param navigator 菜单导航器句柄
 * @param key_value 按键值（UP/DOWN/LEFT/RIGHT/NONE）
 * @details 根据按键值执行相应的菜单操作
 */
void menu_handle_input(void* navigator, uint8_t key_value);

/** @} */

/**
 * @defgroup MenuDisplay 菜单显示功能
 * @brief 菜单显示相关的功能函数
 * @{
 */

/**
 * @brief 刷新菜单显示内容
 * @param navigator 菜单导航器句柄
 * @details 更新菜单显示缓冲区的内容
 */
void menu_refresh_display(void* navigator);

/**
 * @brief 获取菜单显示缓冲区
 * @param navigator 菜单导航器句柄
 * @return 显示缓冲区指针
 * @details 返回包含所有菜单显示内容的缓冲区
 */
char* menu_get_display_buffer(void* navigator);

/**
 * @brief 显示菜单内容
 * @param navigator 菜单导航器句柄
 * @details 刷新显示内容并调用menu_show_string函数输出到屏幕
 * @note 此函数会自动调用用户实现的menu_show_string函数
 */
void menu_display(void* navigator);

/**
 * @brief 强制刷新菜单显示
 * @param navigator 菜单导航器句柄
 * @details 清空显示缓冲区并强制更新所有显示内容
 */
void menu_force_refresh_display(void* navigator);

/** @} */

/**
 * @defgroup MenuMode 菜单模式管理
 * @brief 菜单应用模式的设置和获取
 * @{
 */

/**
 * @brief 获取菜单应用模式状态
 * @param navigator 菜单导航器句柄
 * @return 应用模式状态（1：应用模式，0：菜单模式）
 * @details 检查菜单是否处于应用程序模式
 */
uint8_t menu_get_app_mode(void* navigator);

/**
 * @brief 设置菜单应用模式
 * @param navigator 菜单导航器句柄
 * @param mode 模式值（非0：应用模式，0：菜单模式）
 * @details 设置菜单是否进入应用程序模式
 */
void menu_set_app_mode(void* navigator, uint8_t mode);

/** @} */

/**
 * @defgroup MenuExhibition 菜单展示功能
 * @brief 展示类型菜单项的分页管理功能
 * @{
 */

/**
 * @brief 展示项下一页
 * @param navigator 菜单导航器句柄
 * @details 切换当前展示项到下一页
 */
void menu_exhibition_next_page(void* navigator);

/**
 * @brief 展示项上一页
 * @param navigator 菜单导航器句柄
 * @details 切换当前展示项到上一页
 */
void menu_exhibition_prev_page(void* navigator);

/**
 * @brief 重置展示项到第一页
 * @param navigator 菜单导航器句柄
 * @details 将当前展示项重置到第一页
 */
void menu_exhibition_reset_to_first_page(void* navigator);

/**
 * @brief 获取展示项当前页码
 * @param navigator 菜单导航器句柄
 * @return 当前页码（从0开始）
 */
uint8_t menu_exhibition_get_current_page(void* navigator);

/**
 * @brief 获取展示项总页数
 * @param navigator 菜单导航器句柄
 * @return 总页数
 */
uint8_t menu_exhibition_get_total_pages(void* navigator);

/**
 * @brief 检查展示项是否可分页
 * @param navigator 菜单导航器句柄
 * @return 是否可分页（1：可分页，0：不可分页）
 * @details 检查当前选中的展示项是否支持分页操作
 */
uint8_t menu_exhibition_is_pageable(void* navigator);

/** @} */

/**
 * @defgroup MenuInfo 菜单信息获取
 * @brief 获取菜单当前状态信息的功能
 * @{
 */

/**
 * @brief 获取当前页面名称
 * @param navigator 菜单导航器句柄
 * @return 当前页面名称字符串
 * @details 返回当前菜单页面的名称，展示模式下包含页码信息
 */
const char* menu_get_current_page_name(void* navigator);

/**
 * @brief 获取当前选中项名称
 * @param navigator 菜单导航器句柄
 * @return 当前选中菜单项的名称
 */
const char* menu_get_current_selected_item_name(void* navigator);

/**
 * @brief 检查是否处于展示模式
 * @param navigator 菜单导航器句柄
 * @return 是否处于展示模式（1：展示模式，0：普通模式）
 * @details 判断当前是否处于展示类型菜单项的展示模式
 */
uint8_t menu_is_in_exhibition_mode(void* navigator);

/** @} */

/**
 * @defgroup MenuNavigation 菜单导航功能
 * @brief 菜单跳转和导航相关功能
 * @{
 */

/**
 * @brief 跳转到指定菜单项
 * @param navigator 菜单导航器句柄
 * @param menu_name 目标菜单项名称
 * @details 根据菜单项名称直接跳转到指定的菜单项
 * @note 此函数会在整个菜单树中搜索指定名称的菜单项
 */
void menu_goto(void* navigator, const char* menu_name);

/** @} */

#ifdef __cplusplus
}
#endif

#endif
