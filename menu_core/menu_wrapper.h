#ifndef MENU_C_WRAPPER_H
#define MENU_C_WRAPPER_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief 键值定义
 * @note 用于菜单导航的按键操作定义
 */
enum
{
    UP,     ///< 上键：向上导航或上一页
    DOWN,   ///< 下键：向下导航或下一页  
    LEFT,   ///< 左键：返回上级菜单或退出展示模式
    RIGHT,  ///< 右键：进入下级菜单或激活展示模式
    NONE,   ///< 无按键操作
};


/*==============================================================================
 * 基础菜单导航接口
 *============================================================================*/

/**
 * @brief 创建菜单导航器
 * @param mainMenu 主菜单项指针，由菜单结构定义生成
 * @return 菜单导航器实例指针，失败返回NULL
 * @note 使用完毕后需要调用menu_delete释放资源
 * @code
 * void* main_item = getMainItem();
 * void* navigator = menu_builder(main_item);
 * @endcode
 */


void* menu_builder(void* mainMenu);

/**
 * @brief 销毁菜单导航器
 * @param navigator 菜单导航器指针
 * @note 释放菜单导航器占用的内存资源
 * @warning 销毁后不能再使用该指针
 */
void menu_delete(void* navigator);

/**
 * @brief 处理按键输入
 * @param navigator 菜单导航器指针
 * @param key_value 按键值，参考上面的枚举定义
 * @note 根据当前菜单状态和按键类型执行相应的操作
 * @note 在展示模式下，UP/DOWN键用于翻页，LEFT键退出展示模式
 * @code
 * menu_handle_input(navigator, UP);    // 向上导航
 * menu_handle_input(navigator, RIGHT); // 进入菜单项
 * @endcode
 */
void menu_handle_input(void* navigator, uint8_t key_value);

/**
 * @brief 刷新菜单显示
 * @param navigator 菜单导航器指针
 * @note 更新显示缓冲区内容，应在按键处理后调用
 * @note 会执行展示型菜单项的回调函数更新数据
 */
void menu_refresh_display(void* navigator);

/**
 * @brief 获取显示缓冲区指针
 * @param navigator 菜单导航器指针
 * @return 显示缓冲区数据指针，失败返回错误信息字符串
 * @note 返回的缓冲区大小为MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM
 * @note 每行MAX_DISPLAY_CHAR个字符，共MAX_DISPLAY_ITEM行
 */
char* menu_get_display_buffer(void* navigator);


/*==============================================================================
 * 菜单状态管理接口
 *============================================================================*/

/**
 * @brief 获取应用模式状态
 * @param navigator 菜单导航器指针
 * @return 1表示在应用模式，0表示在菜单模式
 * @note 应用模式下菜单导航被暂停，只响LEFT键退出
 */
uint8_t menu_get_app_mode(void* navigator);

/**
 * @brief 设置应用模式状态
 * @param navigator 菜单导航器指针
 * @param mode 1进入应用模式，0退出应用模式
 * @note 应用模式下只响LEFT键退出，其他按键被忽略
 */

void menu_set_app_mode(void* navigator, uint8_t mode);

/**
 * @brief 强制刷新显示
 * @param navigator 菜单导航器指针
 * @note 清空显示缓冲区并强制重新绘制菜单
 * @note 通常在显示异常或需要强制更新时使用
 */
void menu_force_refresh_display(void* navigator);


/*==============================================================================
 * 展示型菜单项分页控制接口
 *============================================================================*/

/**
 * @brief 展示型菜单项翻至下一页
 * @param navigator 菜单导航器指针
 * @note 仅在展示模式下且支持分页时有效
 * @note 到达最后一页时会循环到第一页
 * @code
 * if (menu_exhibition_is_pageable(navigator)) {
 *     menu_exhibition_next_page(navigator);
 * }
 * @endcode
 */

void menu_exhibition_next_page(void* navigator);

/**
 * @brief 展示型菜单项翻至上一页
 * @param navigator 菜单导航器指针
 * @note 仅在展示模式下且支持分页时有效
 * @note 在第一页时会循环到最后一页
 */
void menu_exhibition_prev_page(void* navigator);

/**
 * @brief 重置展示型菜单项到第一页
 * @param navigator 菜单导航器指针
 * @note 将当前展示型菜单项的页面重置为第一页
 * @note 不管当前是否在展示模式下都可以使用
 */

void menu_exhibition_reset_to_first_page(void* navigator);

/**
 * @brief 获取展示型菜单项当前页码
 * @param navigator 菜单导航器指针
 * @return 当前页码（从0开始），失败返回0
 * @note 仅对展示型菜单项有效，其他类型菜单项返回0
 */
uint8_t menu_exhibition_get_current_page(void* navigator);

/**
 * @brief 获取展示型菜单项总页数
 * @param navigator 菜单导航器指针
 * @return 总页数，失败返回1
 * @note 仅对展示型菜单项有效，其他类型菜单项返回1
 */
uint8_t menu_exhibition_get_total_pages(void* navigator);

/**
 * @brief 检查展示型菜单项是否支持分页
 * @param navigator 菜单导航器指针
 * @return 1表示支持分页，0表示不支持
 * @note 需要同时满足：在展示模式下 + 总页数大于1
 */

uint8_t menu_exhibition_is_pageable(void* navigator);


/*==============================================================================
 * 页面信息查询接口
 *============================================================================*/

/**
 * @brief 获取当前页面名称
 * @param navigator 菜单导航器指针
 * @return 当前页面名称字符串，失败返回"Unknown"
 * @note 返回格式说明：
 *       - 普通菜单：返回菜单名称，如"Main Menu"
 *       - 展示项（单页）：返回菜单项名称，如"RTC"
 *       - 展示项（多页）：返回带分页信息，如"SysInfo(Page 2/3)"
 * @warning 返回的字符串指针指向静态缓冲区，下次调用会被覆盖
 */
const char* menu_get_current_page_name(void* navigator);

/**
 * @brief 获取当前选中的菜单项名称
 * @param navigator 菜单导航器指针
 * @return 当前选中菜单项名称，失败返回"Unknown"
 * @note 始终返回当前选中的菜单项名称，如"SysInfo"、"LED"等
 * @note 不包含分页信息，仅返回菜单项的原始名称
 */
const char* menu_get_current_selected_item_name(void* navigator);

/**
 * @brief 检查是否在展示模式
 * @param navigator 菜单导航器指针
 * @return 1表示在展示型菜单项的激活状态，0表示在普通菜单浏览状态
 * @note 展示模式下UP/DOWN键用于翻页，LEFT键退出展示模式
 * @note 普通菜单模式下UP/DOWN键用于选择菜单项，RIGHT键进入菜单项
 */

uint8_t menu_is_in_exhibition_mode(void* navigator);

#ifdef __cplusplus
}
#endif

#endif //MENU_C_WRAPPER_H
