#ifndef __EASY_MENU_PAGE_H__
#define __EASY_MENU_PAGE_H__

#include "Easy_Menu.h"

/* ================================================================= 普通页面 ================================================================= */
// ------ 结构体
typedef struct Ordinary_Page {
    Page page;
    Item **items;                              // 条目数组
    unsigned char item_num;                    // 条目数量
    unsigned char items_index;                 // 条目数组索引（每页的第一行）
    
    unsigned char cursor;                      // 光标（行）
    
    void (*Refresh)(void);
} Ordinary_Page;
// ------ 相关函数
void Ordinary_Page_Init(Page *prev_page, Page *page, char *text, Item **items, unsigned char item_num);
void Ordinary_Page_Enter(void);
void Ordinary_Page_Display(void);
void Ordinary_Page_Input(Easy_Menu_Input_TYPE user_input);
void Ordinary_Page_Exit(void);
void Ordinary_Page_Refresh(void);
/* ================================================================= 展示页面 ================================================================= */
typedef struct Show_Page {
    Page page;
    unsigned short int period;  // 每 period 个 tick 刷新一次
    
    unsigned int last_tick;     // 上一次的刷新的时间

    void (*Enter_Callback)(void);
    void (*Period_Callback)(void* temp, Easy_Menu_Input_TYPE user_input);
    void (*Exit_Callback)(void);
} Show_Page;
// ------ 相关函数
void Show_Page_Init(Page *prev_page, Page *page, char *text, unsigned short int period, void (*Enter_Callback)(void), void (*Period_Callback)(void* temp, Easy_Menu_Input_TYPE user_input), void (*Exit_Callback)(void));
void Show_Page_Enter(void);
void Show_Page_Diaplsy(void);
void Show_Page_Input(Easy_Menu_Input_TYPE user_input);
void Show_Page_Exit(void);

#endif 
