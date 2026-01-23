#ifndef __EASY_MENU_H__
#define __EASY_MENU_H__

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

#include <limits.h>
#include <float.h>

/* ================================================================ 用户配置项 ================================================================ */
#define SCREEN_WIDTH     128           // 屏幕宽（像素）
#define SCREEN_HEIGHT    32            // 屏幕高（像素）

#define CHAR_WIDTH       8             // 字符宽（像素），统一使用 ASCII 字符的宽度，中文字符必须为 ASCII 字符的两倍
#define CHAR_HEIGHT      16            // 字符高（像素）

#define USER_FREE_CHAR  '>'            // 解锁状态下的 ASCII 指示符
#define USER_FIX_CHAR   '&'            // 锁定状态下的 ASCII 指示符

#define USER_LIST_ITEM_CHAR '+'        // 二级菜单 ASCII 指示符

#define TITLE_DISPLAY   0              // 是否开启居中显示页面标题（普通页面），最大行数（SCREEN_HIGHT / CHAR_HIGHT）> 1 才会生效

#define USER_TITLE_LEFT_CHAR    '<'    // 标题左侧的 ASCII 指示符
#define USER_TITLE_RIGHT_CHAR   '>'    // 标题右侧的 ASCII 指示符

#define SWITCH_ITEM_MODE    1          // 开关条目显示模式：0->显示 0 / 1，1->显示 OFF / ON

#define ENUM_ITEM_MODE  0              // 枚举条目操作模式：0-普通队列，1-循环队列（从第 0 个往上会回到结尾，从结尾往下会回到第 0 个）

//#define EASY_MENU_CHINESE_CODING  1  // 使用的中文编码：0-UTF-8, 1-GB2312          留作拓展使用，目前只支持 GB2312 编码
/* ============================================================= 系统接口函数原型============================================================== */
/*

* @brief  字符显示函数
* @param  x: 起点 X 轴坐标
* @param  y: 起点 Y 轴坐标
* @param  ch: 需要显示的目标字符
* @param  reverse_flag: 反色显示标志位（不需要反色显示，可以忽视），0-正常，1-反色
void (*Display_Char)(unsigned short int x, unsigned short int y, char ch, unsigned char reverse_flag);                  // 核心显示函数（ASCII）

* @brief  字符显示函数（Y 轴以行为单位）
* @param  x: 起点 X 轴坐标
* @param  line: 对应行（对于不等分的行，可以自行用 switch 来设定每行对应的 Y 轴坐标）
* @param  ch: 需要显示的目标字符
* @param  reverse_flag: 反色显示标志位（不需要反色显示，可以忽视）
void (*Display_Char_Line)(unsigned short int x, unsigned char line, char ch, unsigned char reverse_flag);               // 核心显示函数（ASCII）

void (*Display_Chinese_Char)(unsigned short int x, unsigned short int y, char* ch, unsigned char reverse_flag);         // 核心显示函数（中文字符）
void (*Display_Chinese_Char_Line)(unsigned short int x, unsigned char line, char* ch, unsigned char reverse_flag);      // 核心显示函数（中文字符）

*/

/* ================================================================= 操作相关 ================================================================= */
/* 系统输入枚举 */
typedef enum {
    EASY_MENU_NONE,     // 无操作
    EASY_MENU_UP,       // 上
    EASY_MENU_DOWN,     // 下
    EASY_MENU_LEFT,     // 左（返回/解锁）
    EASY_MENU_RIGHT,    // 右（确定/锁定）
} Easy_Menu_Input_TYPE;

/* ================================================================= 页面相关 ================================================================= */
/* 页面类型枚举 */
typedef enum {
    ORDINARY_PAGE,              // 普通页面
    SHOW_PAGE,                  // 展示页面
} PAGE_TYPE;

/* 基类结构体 */
typedef struct Page {
	PAGE_TYPE type;             // 页面类型
	char *text;                 // 页面名称
    struct Page *prev_page;     // 上级页面
    
    void (*Enter)(void);
    void (*Display)(void);
    void (*Input)(Easy_Menu_Input_TYPE user_input);
    void (*Exit)(void);
} Page;

/* ================================================================= 条目相关 ================================================================= */
/* 条目类型枚举 */
typedef enum {
    TEXT_ITEM,          // 文本条目
    SWITCH_ITEM,        // 开关条目                
    DATA_ITEM,          // 数据条目
    ENUM_ITEM,          // 枚举条目
    SHOW_ITEM,          // 展示条目
    GOTO_ITEM,          // 跳转条目
} ITEM_TYPE;

/* 基类结构体 */
typedef struct Item {
	ITEM_TYPE type;     // 条目类型
	char *text;         // 条目名称
	Page *parent_page;  // 父页面
    
    void (*Input)(struct Item *item, Easy_Menu_Input_TYPE user_input);
} Item;
/* ================================================================= 系统相关 ================================================================= */

#define EASY_MENU_LINE_MAX_NUM (SCREEN_HEIGHT / CHAR_HEIGHT)
#define EASY_MENU_COL_MAX_NUM  (SCREEN_WIDTH / CHAR_WIDTH)

#define EASY_MENU_FREE_CHAR ((unsigned char)USER_FREE_CHAR < 128 ? USER_FREE_CHAR : '>')
#define EASY_MENU_FIX_CHAR  ((unsigned char)USER_FIX_CHAR < 128 ? USER_FIX_CHAR : '&')

#define EASY_MENU_LIST_ITEM_CHAR  ((unsigned char)USER_LIST_ITEM_CHAR < 128 ? USER_LIST_ITEM_CHAR : '+')
    
#define EASY_MENU_TITLE_LEFT_CHAR  ((unsigned char)USER_TITLE_LEFT_CHAR < 128 ? USER_TITLE_LEFT_CHAR : '<') 
#define EASY_MENU_TITLE_RIGHT_CHAR  ((unsigned char)USER_TITLE_RIGHT_CHAR < 128 ? USER_TITLE_RIGHT_CHAR : '>')

#define ORDINARY_PAGE_TITLE_DISPLAY (TITLE_DISPLAY == 1 && EASY_MENU_LINE_MAX_NUM > 1)  

#define PAGE(user_page) &(user_page.page)
#define ITEM(user_item) &(user_item.item)

/* 系统结构体 */
typedef struct Easy_Menu {
    char buffer[EASY_MENU_LINE_MAX_NUM][EASY_MENU_COL_MAX_NUM];                                                             // 实际缓冲区
    char compare_buffer[EASY_MENU_LINE_MAX_NUM][EASY_MENU_COL_MAX_NUM];                                                     // 比较缓冲区
    
    void (*Display_Char)(unsigned short int x, unsigned short int y, char ch, unsigned char reverse_flag);                  // 核心显示函数（ASCII）
    void (*Display_Char_Line)(unsigned short int x, unsigned char line, char ch, unsigned char reverse_flag);               // 核心显示函数（ASCII）
    
    void (*Display_Chinese_Char)(unsigned short int x, unsigned short int y, char* ch, unsigned char reverse_flag);         // 核心显示函数（中文字符）
    void (*Display_Chinese_Char_Line)(unsigned short int x, unsigned char line, char* ch, unsigned char reverse_flag);      // 核心显示函数（中文字符）
    
    unsigned int tick;                                                                                                      // 运行 tick
    
    Easy_Menu_Input_TYPE current_input;                                                                                     // 当前的输入
    
    Page *current_page;                                                                                                     // 当前页面    
    unsigned char current_line;                                                                                             // 当前行（普通页面）
    
    unsigned char lock_flag;                                                                                                // 锁定标志位
    
    unsigned char init_flag;                                                                                                // 初始化完成标志位
} Easy_Menu;

extern Easy_Menu easy_menu;

/* =============================================================== 系统绘制函数 =============================================================== */
void Easy_Menu_All_Update(void);
void Easy_Menu_Area_Update(unsigned char col_start, unsigned char col_end, unsigned char line_start, unsigned char line_end);

void Easy_Menu_All_Clear(void);
void Easy_Menu_Area_Clear(unsigned char col_start, unsigned char col_end, unsigned char line_start, unsigned char line_end);

void Easy_Menu_Display_Char(unsigned char col, unsigned char line, char ch);
void Easy_Menu_Display_String(int col, unsigned char line, char* str);

void Easy_Menu_Printf(int col, unsigned char line, const char *format, ...);

/* ================================================================= 用户函数 ================================================================= */
/**
    * @brief  菜单系统初始化
    * @param  Display_Char: ASCII 字符显示函数
    * @param  Display_Char_Line: ASCII 字符显示函数（Y 轴以行为单位）
    * @param  Display_Chinese_Char: 中文 字符显示函数
    * @param  Display_Chinese_Char_Line: 中文字符显示函数（Y 轴以行为单位）
    * @notes  Char 相关的显示函数，至少有一个绑定系统才能显示，Chinese 相关的中文显示函数为可选项
  */
void Easy_Menu_Init(void (*Display_Char)(unsigned short int x, unsigned short int y, char ch, unsigned char reverse_flag), void (*Display_Char_Line)(unsigned short int x, unsigned char line, char ch, unsigned char reverse_flag),
                    void (*Display_Chinese_Char)(unsigned short int x, unsigned short int y, char* ch, unsigned char reverse_flag), void (*Display_Chinese_Char_Line)(unsigned short int x, unsigned char line, char* ch, unsigned char reverse_flag));

/**
* @brief  菜单系统显示
    * @param  Easy_Menu_Tick: 系统运行的 Tick
    * @notes  最好使用 1ms 自增的的变量来作为系统的 Tick 这样可以保证周期页面/条目的周期单位为 ms
  */
void Easy_Menu_Display(unsigned int Easy_Menu_Tick);

/**
    * @brief  刷新当前页面的内容（）
    * @param  Display_Char: ASCII 字符显示函数
    * @notes  仅对普通页面有效，用于在回调函数中修改开关、数据条目的值时，调用这个函数可以立刻刷新
  */
void Easy_Menu_Display_Refresh(void);

/**
    * @brief  菜单系统输入
    * @param  user_input: 操作输入
    * @notes  无操作、上、下、左、右
  */
void Easy_Menu_Input(Easy_Menu_Input_TYPE user_input);

/**
    * @brief  获取当前页面的显示名称
    * @param  str: 用于接收字符串的指针
  */
void Easy_Menu_Get_Current_Page_Text(char* str);

/**
    * @brief  刷新当前页面的内容（）
    * @param  target_page: 目标页面的变量 
    * @notes  使用时需要以这样的形式使用：PAGE(target_page)
  */
void Easy_Menu_Goto_Page(Page *target_page);

#endif 
