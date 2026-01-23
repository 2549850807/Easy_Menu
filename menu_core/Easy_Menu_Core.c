#include "Easy_Menu_Core.h"

/* ================================================================= 用户函数 ================================================================= */
void Easy_Menu_Init(void (*Display_Char)(unsigned short int x, unsigned short int y, char ch, unsigned char reverse_flag), void (*Display_Char_Line)(unsigned short int x, unsigned char line, char ch, unsigned char reverse_flag),
                    void (*Display_Chinese_Char)(unsigned short int x, unsigned short int y, char* ch, unsigned char reverse_flag), void (*Display_Chinese_Char_Line)(unsigned short int x, unsigned char line, char* ch, unsigned char reverse_flag))
{
    /* 绑定显示函数 */
    easy_menu.Display_Char = Display_Char;
    easy_menu.Display_Char_Line = Display_Char_Line;
    
    easy_menu.Display_Chinese_Char = Display_Chinese_Char;
    easy_menu.Display_Chinese_Char_Line = Display_Chinese_Char_Line;
    
    /* 重置系统输入 */
    easy_menu.current_input = EASY_MENU_NONE;
    
    /* 清屏 */
    Easy_Menu_All_Clear();
    
    /* UI 初始化 */
    Easy_Menu_Ui_Init();
}

void Easy_Menu_Display(unsigned int Easy_Menu_Tick)
{
    /* 标识系统状态，执行进入函数 */
    if(easy_menu.init_flag == 0)
    {
        easy_menu.init_flag = 1;
        if(easy_menu.current_page->Enter != NULL)
            easy_menu.current_page->Enter();
    }
    
    /* 更新运行 tick */
    easy_menu.tick = Easy_Menu_Tick;
    
    /* 页面输入 */
    if(easy_menu.current_input != EASY_MENU_NONE)
    {
        easy_menu.current_page->Input(easy_menu.current_input);
        easy_menu.current_input = EASY_MENU_NONE;
    }
    
    /* 页面更新 */
    easy_menu.current_page->Display();
    
}

void Easy_Menu_Display_Refresh(void)
{
    if(easy_menu.current_page->type != ORDINARY_PAGE) return;

    Ordinary_Page *ordinary_page = (Ordinary_Page*)(easy_menu.current_page);
    
    ordinary_page->Refresh();
}

void Easy_Menu_Input(Easy_Menu_Input_TYPE user_input)
{
    if(easy_menu.current_input != EASY_MENU_NONE) return;
    
    easy_menu.current_input = user_input;
}

void Easy_Menu_Get_Current_Page_Text(char* str)
{
    strcpy(str, easy_menu.current_page->text);
}

void Easy_Menu_Goto_Page(Page *target_page)
{
    if(easy_menu.init_flag == 1 && easy_menu.current_page != NULL && easy_menu.current_page->Exit != NULL)
        easy_menu.current_page->Exit();
  
    easy_menu.current_page = target_page;
    
    /* 重置目标页面光标 */
    if(easy_menu.current_page->type == ORDINARY_PAGE)
    {
        Ordinary_Page *ordinary_page = (Ordinary_Page*)(easy_menu.current_page);
        ordinary_page->items_index = 0;
#if ORDINARY_PAGE_TITLE_DISPLAY == 0
        ordinary_page->cursor = 0;
#else
        ordinary_page->cursor = 1;
#endif
    }
    
    if(easy_menu.init_flag == 1 && easy_menu.current_page->Enter != NULL)
        easy_menu.current_page->Enter();
}

