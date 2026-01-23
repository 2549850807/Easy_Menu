#include "Easy_Menu_Page.h"
#include "Easy_Menu_Item.h"

/* ================================================================= 普通页面 ================================================================= */
void Ordinary_Page_Init(Page *prev_page, Page *page, char *text, Item **items, unsigned char item_num)
{
    page->type = ORDINARY_PAGE;
    page->text = text;
    page->prev_page = prev_page;
    
    page->Enter = Ordinary_Page_Enter;
    page->Display = Ordinary_Page_Display;
    page->Input = Ordinary_Page_Input;
    page->Exit = Ordinary_Page_Exit;
    
    Ordinary_Page *ordinary_page = (Ordinary_Page*)page;
    
    ordinary_page->items = items;
    
    ordinary_page->item_num = item_num;
    
    ordinary_page->items_index = 0;
    
#if ORDINARY_PAGE_TITLE_DISPLAY == 0
    ordinary_page->cursor = 0;
#else
    ordinary_page->cursor = 1;
#endif

    ordinary_page->Refresh = Ordinary_Page_Refresh;
}

void Ordinary_Page_Enter(void)
{
    Ordinary_Page *ordinary_page = (Ordinary_Page*)(easy_menu.current_page);
    
    /* 遍历页面中所有需要显示数值的条目，执行一次回调函数 */
    for(unsigned char item_index = 0; item_index < ordinary_page->item_num; item_index++)
    {
        switch(ordinary_page->items[item_index]->type)
        {
            case SWITCH_ITEM:
            {
                Switch_Item *switch_item = (Switch_Item*)ordinary_page->items[item_index];
                if(switch_item->Callback != NULL)
                    switch_item->Callback(*(switch_item->data));
                break;
            }
            case DATA_ITEM:
            {
                Data_Item *data_item = (Data_Item*)ordinary_page->items[item_index];
                if(data_item->Callback != NULL)
                    data_item->Callback(data_item->data);
                break;
            }
//            case ENUM_ITEM:
//            {
//                Enum_Item *enum_item = (Enum_Item*)ordinary_page->items[item_index];
//                if(enum_item->Callback != NULL)
//                    enum_item->Callback(enum_item->enum_str[enum_item->enum_str_index]);
//                break;
//            }
            case SHOW_ITEM:
            {
                Show_Item *show_item = (Show_Item*)ordinary_page->items[item_index];
                if(show_item->Callback != NULL)
                    show_item->Callback();
                break;
            }
            default:
                break;
        }
    }

    /* 更新系统当前行 */
    easy_menu.current_line = ordinary_page->cursor;
    
    /* 清除显示区域 */
    Easy_Menu_All_Clear();
//    Easy_Menu_Area_Clear(1, EASY_MENU_COL_MAX_NUM, 0, EASY_MENU_LINE_MAX_NUM);
    
#if ORDINARY_PAGE_TITLE_DISPLAY == 0
    unsigned char max_visible_items = EASY_MENU_LINE_MAX_NUM;  // 每页最大可见条目数
#else
    unsigned char max_visible_items = EASY_MENU_LINE_MAX_NUM - 1;  // 每页最大可见条目数
    unsigned char line_offset = 1;                 // 行偏移量（跳过标题行）
#endif
    
#if ORDINARY_PAGE_TITLE_DISPLAY == 0
        /* 显示条目 */
        for(unsigned char line = 0; ordinary_page->items_index + line < ordinary_page->item_num && line < max_visible_items && ordinary_page->items[ordinary_page->items_index + line] != NULL; line++)
        {
            /* 显示条目名称 */
            Easy_Menu_Display_String(1, line, ordinary_page->items[ordinary_page->items_index + line]->text);
            
            /* 显示条目数值 */
            switch(ordinary_page->items[ordinary_page->items_index + line]->type)
            {
                case SWITCH_ITEM:
                {
                    Switch_Item *switch_item = (Switch_Item*)ordinary_page->items[ordinary_page->items_index + line];
#if SWITCH_ITEM_MODE == 0
                    if(*(switch_item->data) == 0)
                        Easy_Menu_Display_String(-1, line, "[0]");
                    else
                        Easy_Menu_Display_String(-1, line, "[1]");
#else
                    if(*(switch_item->data) == 0)
                        Easy_Menu_Display_String(-1, line, "[OFF]");
                    else
                        Easy_Menu_Display_String(-1, line, "[ON]");
#endif
                    break;
                }
                case DATA_ITEM:
                {
                    Data_Item *data_item = (Data_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    switch(data_item->data_type)
                    {
                        case UNSIGNED_CHAR:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned char*)(data_item->data)));
                            break;
                        case UNSIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned short int*)(data_item->data)));
                            break;
                        case UNSIGNED_INT:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned int*)(data_item->data)));
                            break;
                        case SIGNED_CHAR:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed char*)(data_item->data)));
                            break;
                        case SIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed short int*)(data_item->data)));
                            break;
                        case SIGNED_INT:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed int*)(data_item->data)));
                            break;
                        case FLOAT:
                            Easy_Menu_Printf(-1, line, "[%.2f]", *((float*)(data_item->data)));
                            break;
                    }
                    break;
                }
                case ENUM_ITEM:
                {
                    Enum_Item *enum_item = (Enum_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    Easy_Menu_Printf(-1, line, "[%s]", enum_item->enum_str[enum_item->enum_str_index]);
                    break;
                }
                case SHOW_ITEM:
                {
                    Show_Item *show_item = (Show_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    switch(show_item->data_type)
                    {
                        case UNSIGNED_CHAR:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned char*)(show_item->data)));
                            break;
                        case UNSIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned short int*)(show_item->data)));
                            break;
                        case UNSIGNED_INT:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned int*)(show_item->data)));
                            break;
                        case SIGNED_CHAR:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed char*)(show_item->data)));
                            break;
                        case SIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed short int*)(show_item->data)));
                            break;
                        case SIGNED_INT:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed int*)(show_item->data)));
                            break;
                        case FLOAT:
                            Easy_Menu_Printf(-1, line, "[%.2f]", *((float*)(show_item->data)));
                            break;
                    }
                    break;
                }
                case GOTO_ITEM:
                    Easy_Menu_Display_Char(EASY_MENU_COL_MAX_NUM - 1, line, EASY_MENU_LIST_ITEM_CHAR);
                    break;
                default:
                    break;
            }
        }
#else
        /* 显示标题 */
        unsigned char title_x = (EASY_MENU_COL_MAX_NUM / 2) - (strlen(ordinary_page->page.text) / 2);
        
        Easy_Menu_Display_Char(title_x - 1, 0, EASY_MENU_TITLE_LEFT_CHAR);
        Easy_Menu_Display_String(title_x, 0, ordinary_page->page.text);
        Easy_Menu_Display_Char(title_x + strlen(ordinary_page->page.text), 0, EASY_MENU_TITLE_RIGHT_CHAR);

        
        /* 显示条目 */
        for(unsigned char line = 0;  ordinary_page->items_index + line < ordinary_page->item_num && line < max_visible_items && ordinary_page->items[ordinary_page->items_index + line] != NULL; line++)
        {
            unsigned char display_line = line + line_offset; // 显示行号（跳过标题行）
            
            /* 显示条目名称 */
            Easy_Menu_Display_String(1, display_line, ordinary_page->items[ordinary_page->items_index + line]->text);
            
            /* 显示条目数值 */
            switch(ordinary_page->items[ordinary_page->items_index + line]->type)
            {
                case SWITCH_ITEM:
                {
                    Switch_Item *switch_item = (Switch_Item*)ordinary_page->items[ordinary_page->items_index + line];
#if SWITCH_ITEM_MODE == 0
                    if(*(switch_item->data) == 0)
                        Easy_Menu_Display_String(-1, display_line, "[0]");
                    else
                        Easy_Menu_Display_String(-1, display_line, "[1]");
#else
                    if(*(switch_item->data) == 0)
                        Easy_Menu_Display_String(-1, display_line, "[OFF]");
                    else
                        Easy_Menu_Display_String(-1, display_line, "[ON]");
#endif
                    break;
                }
                case DATA_ITEM:
                {
                    Data_Item *data_item = (Data_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    switch(data_item->data_type)
                    {
                        case UNSIGNED_CHAR:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned char*)(data_item->data)));
                            break;
                        case UNSIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned short int*)(data_item->data)));
                            break;
                        case UNSIGNED_INT:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned int*)(data_item->data)));
                            break;
                        case SIGNED_CHAR:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed char*)(data_item->data)));
                            break;
                        case SIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed short int*)(data_item->data)));
                            break;
                        case SIGNED_INT:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed int*)(data_item->data)));
                            break;
                        case FLOAT:
                            Easy_Menu_Printf(-1, display_line, "[%.2f]", *((float*)(data_item->data)));
                            break;
                    }
                    break;
                }
                case ENUM_ITEM:
                {
                    Enum_Item *enum_item = (Enum_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    Easy_Menu_Printf(-1, display_line, "[%s]", enum_item->enum_str[enum_item->enum_str_index]);
                    break;
                }
                case SHOW_ITEM:
                {
                    Show_Item *show_item = (Show_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    switch(show_item->data_type)
                    {
                        case UNSIGNED_CHAR:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned char*)(show_item->data)));
                            break;
                        case UNSIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned short int*)(show_item->data)));
                            break;
                        case UNSIGNED_INT:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned int*)(show_item->data)));
                            break;
                        case SIGNED_CHAR:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed char*)(show_item->data)));
                            break;
                        case SIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed short int*)(show_item->data)));
                            break;
                        case SIGNED_INT:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed int*)(show_item->data)));
                            break;
                        case FLOAT:
                            Easy_Menu_Printf(-1, display_line, "[%.2f]", *((float*)(show_item->data)));
                            break;
                    }
                    break;
                }
                case GOTO_ITEM:
                    Easy_Menu_Display_Char(EASY_MENU_COL_MAX_NUM - 1, display_line, EASY_MENU_LIST_ITEM_CHAR);
                    break;
                default:
                    break;
            }
        }
#endif
    /* 显示光标 */
    Easy_Menu_Display_Char(0, ordinary_page->cursor, EASY_MENU_FREE_CHAR);
    
    /* 刷新 */
    Easy_Menu_All_Update();
}

void Ordinary_Page_Display(void)
{
#if ORDINARY_PAGE_TITLE_DISPLAY == 0
    unsigned char cursor_start_line = 0;           // 光标起始行
    unsigned char line_offset = 0;                 // 行偏移量
#else
    unsigned char cursor_start_line = 1;           // 光标起始行（第0行显示标题）
    unsigned char line_offset = 1;                 // 行偏移量（跳过标题行）
#endif

    Ordinary_Page *ordinary_page = (Ordinary_Page*)(easy_menu.current_page);
    
    // 修复索引问题：需要考虑行偏移量
    for(unsigned char line = cursor_start_line; line < EASY_MENU_LINE_MAX_NUM; line++)
    {
        // 计算正确的菜单项索引
        unsigned char item_index = ordinary_page->items_index + line - line_offset;
        
        // 检查索引是否有效
        if(item_index >= ordinary_page->item_num) break;
        
        // 检查菜单项是否存在
        if(ordinary_page->items[item_index] == NULL) break;
        
        if(ordinary_page->items[item_index]->type == SHOW_ITEM)
        {
            Show_Item *show_item = (Show_Item*)ordinary_page->items[item_index];
            if(show_item->Callback != NULL && easy_menu.tick - show_item->last_tick >= show_item->period)
            {
                show_item->last_tick = easy_menu.tick;
                show_item->Callback();
                
                Easy_Menu_Area_Clear(1, EASY_MENU_COL_MAX_NUM, line, line);
                Easy_Menu_Display_String(1, line, ordinary_page->items[item_index]->text);
                
                switch(show_item->data_type)
                {
                    case UNSIGNED_CHAR:
                        Easy_Menu_Printf(-1, line, "[%u]", *((unsigned char*)(show_item->data)));
                        break;
                    case UNSIGNED_SHORT_INT:
                        Easy_Menu_Printf(-1, line, "[%u]", *((unsigned short int*)(show_item->data)));
                        break;
                    case UNSIGNED_INT:
                        Easy_Menu_Printf(-1, line, "[%u]", *((unsigned int*)(show_item->data)));
                        break;
                    case SIGNED_CHAR:
                        Easy_Menu_Printf(-1, line, "[%d]", *((signed char*)(show_item->data)));
                        break;
                    case SIGNED_SHORT_INT:
                        Easy_Menu_Printf(-1, line, "[%d]", *((signed short int*)(show_item->data)));
                        break;
                    case SIGNED_INT:
                        Easy_Menu_Printf(-1, line, "[%d]", *((signed int*)(show_item->data)));
                        break;
                    case FLOAT:
                        Easy_Menu_Printf(-1, line, "[%.2f]", *((float*)(show_item->data)));
                        break;
                }
                
                Easy_Menu_All_Update();
            }
        }
    }
}

void Ordinary_Page_Input(Easy_Menu_Input_TYPE user_input)
{
    unsigned char page_turning_flag = 0; // 翻页标志位
    unsigned char cursor_move_flag = 0; // 光标移动标志位
    
    Ordinary_Page *ordinary_page = (Ordinary_Page*)(easy_menu.current_page);
    
    
#if ORDINARY_PAGE_TITLE_DISPLAY == 0
    unsigned char cursor_start_line = 0;           // 光标起始行
    unsigned char max_visible_items = EASY_MENU_LINE_MAX_NUM;  // 每页最大可见条目数
#else
    unsigned char cursor_start_line = 1;           // 光标起始行（第0行显示标题）
    unsigned char max_visible_items = EASY_MENU_LINE_MAX_NUM - 1;  // 每页最大可见条目数
    unsigned char line_offset = 1;                 // 行偏移量（跳过标题行）
#endif
    
    // 计算当前页面实际显示的条目数
    unsigned char current_page_item_count = max_visible_items;
    unsigned char item_remainder = ordinary_page->item_num - ordinary_page->items_index;
    if (item_remainder < max_visible_items) {
        current_page_item_count = item_remainder;
    }
    
    // 当前光标指向的条目索引
    unsigned char current_item_idx = ordinary_page->items_index + ordinary_page->cursor - cursor_start_line;
    
    switch(user_input)
    {
        case EASY_MENU_UP:
            if(easy_menu.lock_flag == 1)
            {
                ordinary_page->items[current_item_idx]->Input(ordinary_page->items[current_item_idx], user_input);
                page_turning_flag = 1;
            }
            else
            {
                /* 清除当前光标 */
                Easy_Menu_Area_Clear(0, 0, ordinary_page->cursor, ordinary_page->cursor);
                
                /* 光标向上移动 */
                if(ordinary_page->cursor > cursor_start_line)
                {
                    /* 正常上移光标 */
#if SWITCH_ITEM_MODE == 0
                    ordinary_page->cursor--;
#else
                    if(--ordinary_page->cursor == cursor_start_line - 1) 
                        ordinary_page->cursor = cursor_start_line + 255; // 处理无符号溢出
#endif
                }
                else
                {
                    /* 光标已到当前页顶部，需要向上翻页 */
                    if(ordinary_page->items_index == 0)
                    {
                        /* 已经是第一页，翻到最后一页 */
                        // 计算最后一页的起始位置
                        unsigned char last_page_start_idx = 0;
                        if(ordinary_page->item_num > max_visible_items)
                        {
                            last_page_start_idx = (ordinary_page->item_num / max_visible_items) * max_visible_items;
                            if(last_page_start_idx >= ordinary_page->item_num)
                                last_page_start_idx -= max_visible_items;
                        }
                        ordinary_page->items_index = last_page_start_idx;
                        
                        // 设置光标到最后一页的最后一个条目
                        unsigned char items_on_last_page = ordinary_page->item_num - ordinary_page->items_index;
                        if(items_on_last_page > max_visible_items)
                            items_on_last_page = max_visible_items;
                            
                        ordinary_page->cursor = cursor_start_line + items_on_last_page - 1;
                    }
                    else
                    {
                        /* 翻到上一页 */
                        ordinary_page->items_index -= max_visible_items;
                        
                        // 设置光标到上一页的最后一个条目
                        ordinary_page->cursor = cursor_start_line + max_visible_items - 1;
                        
                        // 确保光标不超出实际条目数
                        if(ordinary_page->cursor - cursor_start_line >= max_visible_items ||
                           ordinary_page->cursor - cursor_start_line + ordinary_page->items_index >= ordinary_page->item_num)
                        {
                            ordinary_page->cursor = cursor_start_line + max_visible_items - 1;
                        }
                    }
                    page_turning_flag = 1;
                }
                cursor_move_flag = 1;
            }
            break;
            
        case EASY_MENU_DOWN:
            if(easy_menu.lock_flag == 1)
            {
                ordinary_page->items[current_item_idx]->Input(ordinary_page->items[current_item_idx], user_input);
                page_turning_flag = 1;
            }
            else
            {
                /* 清除当前光标 */
                Easy_Menu_Area_Clear(0, 0, ordinary_page->cursor, ordinary_page->cursor);
                
                /* 光标向下移动 */
                if(ordinary_page->cursor < cursor_start_line + current_page_item_count - 1)
                {
                    /* 正常下移光标 */
                    ordinary_page->cursor++;
                }
                else
                {
                    /* 光标已到当前页底部，需要向下翻页 */
                    if(ordinary_page->items_index + max_visible_items >= ordinary_page->item_num)
                    {
                        /* 已经是最后一页或超过条目总数，翻到第一页 */
                        ordinary_page->items_index = 0;
                        ordinary_page->cursor = cursor_start_line;
                    }
                    else
                    {
                        /* 翻到下一页 */
                        ordinary_page->items_index += max_visible_items;
                        ordinary_page->cursor = cursor_start_line;
                        
                        // 确保光标不超出实际条目数
                        if(ordinary_page->items_index + (ordinary_page->cursor - cursor_start_line) >= ordinary_page->item_num)
                        {
                            ordinary_page->cursor = cursor_start_line;
                        }
                    }
                    page_turning_flag = 1;
                }
                cursor_move_flag = 1;
            }
            break;
            
        case EASY_MENU_LEFT:
            /* 当处于非锁定状态，并且有父页面时，返回父页面 */
            if(easy_menu.current_page->prev_page != NULL && easy_menu.lock_flag == 0)
            {
                if(easy_menu.current_page->Exit != NULL)
                    easy_menu.current_page->Exit();
                
                easy_menu.current_page = easy_menu.current_page->prev_page;
    
                if(easy_menu.current_page->Enter != NULL)
                    easy_menu.current_page->Enter();
            }
        
            if(ordinary_page->items[current_item_idx]->Input != NULL)
            {
                if(easy_menu.lock_flag == 1 && (ordinary_page->items[current_item_idx]->type == SWITCH_ITEM  || \
                                                ordinary_page->items[current_item_idx]->type == DATA_ITEM  || \
                                                ordinary_page->items[current_item_idx]->type == ENUM_ITEM))
                {
                    easy_menu.lock_flag = 0;
                    Easy_Menu_Display_Char(0, ordinary_page->cursor, EASY_MENU_FREE_CHAR);
                }
            }
            break;
            
        case EASY_MENU_RIGHT:
            if(ordinary_page->items[current_item_idx]->Input != NULL)
            {
                if(easy_menu.lock_flag == 0 && (ordinary_page->items[current_item_idx]->type == SWITCH_ITEM  || \
                                                ordinary_page->items[current_item_idx]->type == DATA_ITEM  || \
                                                ordinary_page->items[current_item_idx]->type == ENUM_ITEM))
                {
                    easy_menu.lock_flag = 1;
                    Easy_Menu_Display_Char(0, ordinary_page->cursor, EASY_MENU_FIX_CHAR);
                }
                else
                {
                    ordinary_page->items[current_item_idx]->Input(ordinary_page->items[current_item_idx], user_input);
                    
                    if(ordinary_page->items[current_item_idx]->type == GOTO_ITEM)
                        return;
                }
            }
            break;
            
        default:
            break;
    }
    
    
    /* 菜单翻页 */
    if(page_turning_flag == 1)
    {
        /* 清除显示区域 */
        Easy_Menu_Area_Clear(1, EASY_MENU_COL_MAX_NUM, 0, EASY_MENU_LINE_MAX_NUM);
        
#if ORDINARY_PAGE_TITLE_DISPLAY == 0
        /* 显示条目 */
        for(unsigned char line = 0; ordinary_page->items_index + line < ordinary_page->item_num && line < max_visible_items && ordinary_page->items[ordinary_page->items_index + line] != NULL; line++)
        {
            /* 显示条目名称 */
            Easy_Menu_Display_String(1, line, ordinary_page->items[ordinary_page->items_index + line]->text);
            /* 显示条目数值 */
            switch(ordinary_page->items[ordinary_page->items_index + line]->type)
            {
                case SWITCH_ITEM:
                {
                    Switch_Item *switch_item = (Switch_Item*)ordinary_page->items[ordinary_page->items_index + line];
#if SWITCH_ITEM_MODE == 0
                    if(*(switch_item->data) == 0)
                        Easy_Menu_Display_String(-1, line, "[0]");
                    else
                        Easy_Menu_Display_String(-1, line, "[1]");
#else
                    if(*(switch_item->data) == 0)
                        Easy_Menu_Display_String(-1, line, "[OFF]");
                    else
                        Easy_Menu_Display_String(-1, line, "[ON]");
#endif
                    break;
                }
                case DATA_ITEM:
                {
                    Data_Item *data_item = (Data_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    switch(data_item->data_type)
                    {
                        case UNSIGNED_CHAR:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned char*)(data_item->data)));
                            break;
                        case UNSIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned short int*)(data_item->data)));
                            break;
                        case UNSIGNED_INT:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned int*)(data_item->data)));
                            break;
                        case SIGNED_CHAR:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed char*)(data_item->data)));
                            break;
                        case SIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed short int*)(data_item->data)));
                            break;
                        case SIGNED_INT:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed int*)(data_item->data)));
                            break;
                        case FLOAT:
                            Easy_Menu_Printf(-1, line, "[%.2f]", *((float*)(data_item->data)));
                            break;
                    }
                    break;
                }
                case ENUM_ITEM:
                {
                    Enum_Item *enum_item = (Enum_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    Easy_Menu_Printf(-1, line, "[%s]", enum_item->enum_str[enum_item->enum_str_index]);
                    break;
                }
                case SHOW_ITEM:
                {
                    Show_Item *show_item = (Show_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    switch(show_item->data_type)
                    {
                        case UNSIGNED_CHAR:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned char*)(show_item->data)));
                            break;
                        case UNSIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned short int*)(show_item->data)));
                            break;
                        case UNSIGNED_INT:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned int*)(show_item->data)));
                            break;
                        case SIGNED_CHAR:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed char*)(show_item->data)));
                            break;
                        case SIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed short int*)(show_item->data)));
                            break;
                        case SIGNED_INT:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed int*)(show_item->data)));
                            break;
                        case FLOAT:
                            Easy_Menu_Printf(-1, line, "[%.2f]", *((float*)(show_item->data)));
                            break;
                    }
                    break;
                }
                case GOTO_ITEM:
                    Easy_Menu_Display_String(-1, line, "+");
                    break;
                default:
                    break;
            }
        }
#else
        /* 显示标题 */
        unsigned char title_x = (EASY_MENU_COL_MAX_NUM / 2) - (strlen(ordinary_page->page.text) / 2);
        
        Easy_Menu_Display_Char(title_x - 1, 0, EASY_MENU_TITLE_LEFT_CHAR);
        Easy_Menu_Display_String(title_x, 0, ordinary_page->page.text);
        Easy_Menu_Display_Char(title_x + strlen(ordinary_page->page.text), 0, EASY_MENU_TITLE_RIGHT_CHAR);
        
        /* 显示条目 */
        for(unsigned char line = 0; ordinary_page->items_index + line < ordinary_page->item_num && line < max_visible_items && ordinary_page->items[ordinary_page->items_index + line] != NULL; line++)
        {
            unsigned char display_line = line + line_offset; // 显示行号（跳过标题行）
            
            /* 显示条目名称 */
            Easy_Menu_Display_String(1, display_line, ordinary_page->items[ordinary_page->items_index + line]->text);
            
            /* 显示条目数值 */
            switch(ordinary_page->items[ordinary_page->items_index + line]->type)
            {
                case SWITCH_ITEM:
                {
                    Switch_Item *switch_item = (Switch_Item*)ordinary_page->items[ordinary_page->items_index + line];
#if SWITCH_ITEM_MODE == 0
                    if(*(switch_item->data) == 0)
                        Easy_Menu_Display_String(-1, display_line, "[0]");
                    else
                        Easy_Menu_Display_String(-1, display_line, "[1]");
#else
                    if(*(switch_item->data) == 0)
                        Easy_Menu_Display_String(-1, display_line, "[OFF]");
                    else
                        Easy_Menu_Display_String(-1, display_line, "[ON]");
#endif
                    break;
                }
                case DATA_ITEM:
                {
                    Data_Item *data_item = (Data_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    switch(data_item->data_type)
                    {
                        case UNSIGNED_CHAR:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned char*)(data_item->data)));
                            break;
                        case UNSIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned short int*)(data_item->data)));
                            break;
                        case UNSIGNED_INT:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned int*)(data_item->data)));
                            break;
                        case SIGNED_CHAR:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed char*)(data_item->data)));
                            break;
                        case SIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed short int*)(data_item->data)));
                            break;
                        case SIGNED_INT:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed int*)(data_item->data)));
                            break;
                        case FLOAT:
                            Easy_Menu_Printf(-1, display_line, "[%.2f]", *((float*)(data_item->data)));
                            break;
                    }
                    break;
                }
                case ENUM_ITEM:
                {
                    Enum_Item *enum_item = (Enum_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    Easy_Menu_Printf(-1, display_line, "[%s]", enum_item->enum_str[enum_item->enum_str_index]);
                    break;
                }
                case SHOW_ITEM:
                {
                    Show_Item *show_item = (Show_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    switch(show_item->data_type)
                    {
                        case UNSIGNED_CHAR:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned char*)(show_item->data)));
                            break;
                        case UNSIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned short int*)(show_item->data)));
                            break;
                        case UNSIGNED_INT:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned int*)(show_item->data)));
                            break;
                        case SIGNED_CHAR:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed char*)(show_item->data)));
                            break;
                        case SIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed short int*)(show_item->data)));
                            break;
                        case SIGNED_INT:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed int*)(show_item->data)));
                            break;
                        case FLOAT:
                            Easy_Menu_Printf(-1, display_line, "[%.2f]", *((float*)(show_item->data)));
                            break;
                    }
                    break;
                }
                case GOTO_ITEM:
                    Easy_Menu_Display_Char(EASY_MENU_COL_MAX_NUM - 1, display_line, EASY_MENU_LIST_ITEM_CHAR);
                    break;
                default:
                    break;
            }
        }
#endif
    }
    
    /* 光标移动 */
    if(cursor_move_flag == 1)
        Easy_Menu_Display_Char(0, ordinary_page->cursor, EASY_MENU_FREE_CHAR);
    
    /* 更新系统当前行 */
    easy_menu.current_line = ordinary_page->cursor;
    
    /* 刷新 */
    Easy_Menu_All_Update();
}

void Ordinary_Page_Exit(void)
{
    /* 重置系统当前行 */
#if ORDINARY_PAGE_TITLE_DISPLAY == 0
        easy_menu.current_line = 0;
#else
        easy_menu.current_line = 1;
#endif
    
    /* 清屏 */
    Easy_Menu_All_Clear();
}

void Ordinary_Page_Refresh(void)
{
    Ordinary_Page *ordinary_page = (Ordinary_Page*)(easy_menu.current_page);

    /* 清除显示区域 */
    Easy_Menu_All_Clear();
    
#if ORDINARY_PAGE_TITLE_DISPLAY == 0
    unsigned char max_visible_items = EASY_MENU_LINE_MAX_NUM;  // 每页最大可见条目数
#else
    unsigned char max_visible_items = EASY_MENU_LINE_MAX_NUM - 1;  // 每页最大可见条目数
    unsigned char line_offset = 1;                 // 行偏移量（跳过标题行）
#endif
    
#if ORDINARY_PAGE_TITLE_DISPLAY == 0
        /* 显示条目 */
        for(unsigned char line = 0; ordinary_page->items_index + line < ordinary_page->item_num && line < max_visible_items && ordinary_page->items[ordinary_page->items_index + line] != NULL; line++)
        {
            /* 显示条目名称 */
            Easy_Menu_Display_String(1, line, ordinary_page->items[ordinary_page->items_index + line]->text);
            /* 显示条目数值 */
            switch(ordinary_page->items[ordinary_page->items_index + line]->type)
            {
                case SWITCH_ITEM:
                {
                    Switch_Item *switch_item = (Switch_Item*)ordinary_page->items[ordinary_page->items_index + line];
#if SWITCH_ITEM_MODE == 0
                    if(*(switch_item->data) == 0)
                        Easy_Menu_Display_String(-1, line, "[0]");
                    else
                        Easy_Menu_Display_String(-1, line, "[1]");
#else
                    if(*(switch_item->data) == 0)
                        Easy_Menu_Display_String(-1, line, "[OFF]");
                    else
                        Easy_Menu_Display_String(-1, line, "[ON]");
#endif
                    break;
                }
                case DATA_ITEM:
                {
                    Data_Item *data_item = (Data_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    switch(data_item->data_type)
                    {
                        case UNSIGNED_CHAR:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned char*)(data_item->data)));
                            break;
                        case UNSIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned short int*)(data_item->data)));
                            break;
                        case UNSIGNED_INT:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned int*)(data_item->data)));
                            break;
                        case SIGNED_CHAR:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed char*)(data_item->data)));
                            break;
                        case SIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed short int*)(data_item->data)));
                            break;
                        case SIGNED_INT:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed int*)(data_item->data)));
                            break;
                        case FLOAT:
                            Easy_Menu_Printf(-1, line, "[%.2f]", *((float*)(data_item->data)));
                            break;
                    }
                    break;
                }
                case ENUM_ITEM:
                {
                    Enum_Item *enum_item = (Enum_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    Easy_Menu_Printf(-1, line, "[%s]", enum_item->enum_str[enum_item->enum_str_index]);
                    break;
                }
                case SHOW_ITEM:
                {
                    Show_Item *show_item = (Show_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    switch(show_item->data_type)
                    {
                        case UNSIGNED_CHAR:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned char*)(show_item->data)));
                            break;
                        case UNSIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned short int*)(show_item->data)));
                            break;
                        case UNSIGNED_INT:
                            Easy_Menu_Printf(-1, line, "[%u]", *((unsigned int*)(show_item->data)));
                            break;
                        case SIGNED_CHAR:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed char*)(show_item->data)));
                            break;
                        case SIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed short int*)(show_item->data)));
                            break;
                        case SIGNED_INT:
                            Easy_Menu_Printf(-1, line, "[%d]", *((signed int*)(show_item->data)));
                            break;
                        case FLOAT:
                            Easy_Menu_Printf(-1, line, "[%.2f]", *((float*)(show_item->data)));
                            break;
                    }
                    break;
                }
                case GOTO_ITEM:
                    Easy_Menu_Display_Char(EASY_MENU_COL_MAX_NUM - 1, line, EASY_MENU_LIST_ITEM_CHAR);
                    break;
                default:
                    break;
            }
        }
#else
        /* 显示标题 */
        unsigned char title_x = (EASY_MENU_COL_MAX_NUM / 2) - (strlen(ordinary_page->page.text) / 2);
        
        Easy_Menu_Display_Char(title_x - 1, 0, EASY_MENU_TITLE_LEFT_CHAR);
        Easy_Menu_Display_String(title_x, 0, ordinary_page->page.text);
        Easy_Menu_Display_Char(title_x + strlen(ordinary_page->page.text), 0, EASY_MENU_TITLE_RIGHT_CHAR);

        
        /* 显示条目 */
        for(unsigned char line = 0;  ordinary_page->items_index + line < ordinary_page->item_num && line < max_visible_items && ordinary_page->items[ordinary_page->items_index + line] != NULL; line++)
        {
            unsigned char display_line = line + line_offset; // 显示行号（跳过标题行）
            
            /* 显示条目名称 */
            Easy_Menu_Display_String(1, display_line, ordinary_page->items[ordinary_page->items_index + line]->text);
            
            /* 显示条目数值 */
            switch(ordinary_page->items[ordinary_page->items_index + line]->type)
            {
                case SWITCH_ITEM:
                {
                    Switch_Item *switch_item = (Switch_Item*)ordinary_page->items[ordinary_page->items_index + line];
#if SWITCH_ITEM_MODE == 0
                    if(*(switch_item->data) == 0)
                        Easy_Menu_Display_String(-1, display_line, "[0]");
                    else
                        Easy_Menu_Display_String(-1, display_line, "[1]");
#else
                    if(*(switch_item->data) == 0)
                        Easy_Menu_Display_String(-1, display_line, "[OFF]");
                    else
                        Easy_Menu_Display_String(-1, display_line, "[ON]");
#endif
                    break;
                }
                case DATA_ITEM:
                {
                    Data_Item *data_item = (Data_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    switch(data_item->data_type)
                    {
                        case UNSIGNED_CHAR:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned char*)(data_item->data)));
                            break;
                        case UNSIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned short int*)(data_item->data)));
                            break;
                        case UNSIGNED_INT:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned int*)(data_item->data)));
                            break;
                        case SIGNED_CHAR:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed char*)(data_item->data)));
                            break;
                        case SIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed short int*)(data_item->data)));
                            break;
                        case SIGNED_INT:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed int*)(data_item->data)));
                            break;
                        case FLOAT:
                            Easy_Menu_Printf(-1, display_line, "[%.2f]", *((float*)(data_item->data)));
                            break;
                    }
                    break;
                }
                case ENUM_ITEM:
                {
                    Enum_Item *enum_item = (Enum_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    Easy_Menu_Printf(-1, display_line, "[%s]", enum_item->enum_str[enum_item->enum_str_index]);
                    break;
                }
                case SHOW_ITEM:
                {
                    Show_Item *show_item = (Show_Item*)ordinary_page->items[ordinary_page->items_index + line];
                    switch(show_item->data_type)
                    {
                        case UNSIGNED_CHAR:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned char*)(show_item->data)));
                            break;
                        case UNSIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned short int*)(show_item->data)));
                            break;
                        case UNSIGNED_INT:
                            Easy_Menu_Printf(-1, display_line, "[%u]", *((unsigned int*)(show_item->data)));
                            break;
                        case SIGNED_CHAR:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed char*)(show_item->data)));
                            break;
                        case SIGNED_SHORT_INT:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed short int*)(show_item->data)));
                            break;
                        case SIGNED_INT:
                            Easy_Menu_Printf(-1, display_line, "[%d]", *((signed int*)(show_item->data)));
                            break;
                        case FLOAT:
                            Easy_Menu_Printf(-1, display_line, "[%.2f]", *((float*)(show_item->data)));
                            break;
                    }
                    break;
                }
                case GOTO_ITEM:
                    Easy_Menu_Display_Char(EASY_MENU_COL_MAX_NUM - 1, display_line, EASY_MENU_LIST_ITEM_CHAR);
                    break;
                default:
                    break;
            }
        }
#endif
    /* 显示光标 */
    Easy_Menu_Display_Char(0, ordinary_page->cursor, EASY_MENU_FREE_CHAR);
    
    /* 刷新 */
    Easy_Menu_All_Update();
}

/* ================================================================= 展示页面 ================================================================= */
void Show_Page_Init(Page *prev_page, Page *page, char *text, unsigned short int period, void (*Enter_Callback)(void), void (*Period_Callback)(void* temp, Easy_Menu_Input_TYPE user_input), void (*Exit_Callback)(void))
{
    page->type = SHOW_PAGE;
    page->text = text;
    page->prev_page = prev_page;
    
    page->Enter = Show_Page_Enter;
    page->Display = Show_Page_Diaplsy;
    page->Input = Show_Page_Input;
    page->Exit = Show_Page_Exit;

    Show_Page *show_page = (Show_Page*)page;
    
    show_page->period = period;
    
    show_page->last_tick = 0;
    
    show_page->Enter_Callback = Enter_Callback;
    show_page->Period_Callback = Period_Callback;
    show_page->Exit_Callback = Exit_Callback;
}
void Show_Page_Enter(void)
{
    Easy_Menu_All_Clear();
    Easy_Menu_All_Update();
    
    Show_Page *show_page = (Show_Page*)(easy_menu.current_page);
    
    if(show_page->Enter_Callback != NULL)
        show_page->Enter_Callback();
    
    show_page->last_tick = easy_menu.tick;
}
void Show_Page_Diaplsy(void)
{
    Show_Page *show_page = (Show_Page*)(easy_menu.current_page);
    
    if(show_page->Period_Callback != NULL && easy_menu.tick - show_page->last_tick > show_page->period)
    {
        show_page->last_tick = easy_menu.tick;
        show_page->Period_Callback(NULL, EASY_MENU_NONE);
    }
}
void Show_Page_Input(Easy_Menu_Input_TYPE user_input)
{
    Show_Page *show_page = (Show_Page*)(easy_menu.current_page);
    
    if(show_page->Period_Callback != NULL)
    {
        show_page->last_tick = easy_menu.tick;
        show_page->Period_Callback(NULL, user_input);
    }
    
    if(user_input == EASY_MENU_LEFT && easy_menu.current_page->prev_page != NULL)
    {
        if(easy_menu.current_page->Exit != NULL)
            easy_menu.current_page->Exit();

        easy_menu.current_page = easy_menu.current_page->prev_page;

        if(easy_menu.current_page->Enter != NULL)
            easy_menu.current_page->Enter();
    }         
}
void Show_Page_Exit(void)
{
    Show_Page *show_page = (Show_Page*)(easy_menu.current_page);
    
    /* 重置系统当前行 */
#if ORDINARY_PAGE_TITLE_DISPLAY == 0
        easy_menu.current_line = 0;
#else
        easy_menu.current_line = 1;
#endif
    
    /* 清屏 */
    Easy_Menu_All_Clear();
    
    if(show_page->Exit_Callback != NULL)
        show_page->Exit_Callback();
}
