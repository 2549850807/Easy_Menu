#include "Easy_Menu_Item.h"

/* ================================================================= 文本条目 ================================================================= */
void Text_Item_Init(Page *parent_page, Item *item, char *text, void (*Callback)(char *str))
{
    item->parent_page = parent_page;
    item->type = TEXT_ITEM;
    item->text = text;
    
    item->Input = Text_Item_Input;
    
    Text_Item *text_item = (Text_Item*)item;
    
    text_item->Callback = Callback;
}

void Text_Item_Input(Item *item, Easy_Menu_Input_TYPE user_input)
{
    Text_Item *text_item = (Text_Item*)item;
    
    if(text_item->Callback != NULL)
        text_item->Callback(item->text);
}

/* ================================================================= 开关条目 ================================================================= */
void Switch_Item_Init(Page *parent_page, Item *item, char *text, unsigned char *data, void (*Callback)(unsigned char data))
{
    item->parent_page = parent_page;
    item->type = SWITCH_ITEM;
    item->text = text;
    
    item->Input = Switch_Item_Input;
    
    Switch_Item *switch_item = (Switch_Item*)item;
    switch_item->data = data;
    switch_item->Callback = Callback;
}

void Switch_Item_Input(Item *item, Easy_Menu_Input_TYPE user_input)
{
    Switch_Item *switch_item = (Switch_Item*)item;
    
    switch(user_input)
    {
        case EASY_MENU_UP:
            *(switch_item->data) ^= 1;
            break;
        case EASY_MENU_DOWN:
            *(switch_item->data) ^= 1;
            break;
        default:
            break;
    }
    
    if(switch_item->Callback != NULL)
        switch_item->Callback(*(switch_item->data));
}
/* ================================================================= 数值条目 ================================================================= */
void Data_Item_Init(Page *parent_page, Item *item, char *text, DATA_TYPE data_type, void *data, Data_Item_Value step, unsigned char use_step, Data_Item_Value min, unsigned char use_min,  Data_Item_Value max, unsigned char use_max, void (*Callback)(void *data))
{
    item->parent_page = parent_page;
    item->type = DATA_ITEM;
    item->text = text;
    
    item->Input = Data_Item_Input;
    
    Data_Item *data_item = (Data_Item*)item;
    data_item->data_type = data_type;
    data_item->data = data;
    data_item->Callback = Callback;
    
    
    data_item->step = step;
    data_item->has_step = use_step ? 1 : 0;
    
    data_item->min = min;
    data_item->has_min = use_min ? 1 : 0;
    
    data_item->max = max;
    data_item->has_max = use_max ? 1 : 0;
    
}

void Data_Item_Input(Item *item, Easy_Menu_Input_TYPE user_input)
{
    Data_Item *data_item = (Data_Item*)item;
    
    switch(user_input)
    {
        case EASY_MENU_UP:
            switch(data_item->data_type)
            {
                case UNSIGNED_CHAR:
                {
                    unsigned char step = data_item->has_step ? data_item->step.uint8_val : 1;
                    unsigned char max_val = data_item->has_max ? data_item->max.uint8_val : UCHAR_MAX;
                    
                    unsigned char* data_ptr = (unsigned char*)data_item->data;
                    unsigned char new_val = *data_ptr + step;
                    
                    if(new_val > max_val || new_val < *data_ptr)
                        new_val = max_val;
                    
                    *data_ptr = new_val;
                    
                    break;
                }
                case UNSIGNED_SHORT_INT:
                {
                    unsigned short int step = data_item->has_step ? data_item->step.uint16_val : 1;
                    unsigned short int max_val = data_item->has_max ? data_item->max.uint16_val : USHRT_MAX;
                    
                    unsigned short int* data_ptr = (unsigned short int*)data_item->data;
                    unsigned short int new_val = *data_ptr + step;
                    
                    if(new_val > max_val || new_val < *data_ptr)
                        new_val = max_val;
                    
                    *data_ptr = new_val;
                    
                    break;
                }
                case UNSIGNED_INT:
                {
                    unsigned int step = data_item->has_step ? data_item->step.uint32_val : 1;
                    unsigned int max_val = data_item->has_max ? data_item->max.uint32_val : UINT_MAX;
                    
                    unsigned int* data_ptr = (unsigned int*)data_item->data;
                    unsigned int new_val = *data_ptr + step;
                    
                    if(new_val > max_val || new_val < *data_ptr)
                        new_val = max_val;
                    
                    *data_ptr = new_val;
                    
                    break;
                }
                case SIGNED_CHAR:
                {
                    signed char step = data_item->has_step ? data_item->step.int8_val : 1;
                    signed char max_val = data_item->has_max ? data_item->max.int8_val : SCHAR_MAX;
                    
                    signed char* data_ptr = (signed char*)data_item->data;
                    signed char new_val = *data_ptr + step;
                    
                    if(new_val > max_val || new_val < *data_ptr)
                        new_val = max_val;
                    
                    *data_ptr = new_val;
                    
                    break;
                }
                case SIGNED_SHORT_INT:
                {
                    signed short int step = data_item->has_step ? data_item->step.int16_val : 1;
                    signed short int max_val = data_item->has_max ? data_item->max.int16_val : SHRT_MAX;
                    
                    signed short int* data_ptr = (signed short int*)data_item->data;
                    signed short int new_val = *data_ptr + step;
                    
                    if(new_val > max_val || new_val < *data_ptr)
                        new_val = max_val;
                    
                    *data_ptr = new_val;
                    
                    break;
                }
                case SIGNED_INT:
                {
                    signed int step = data_item->has_step ? data_item->step.int32_val : 1;
                    signed int max_val = data_item->has_max ? data_item->max.int32_val : INT_MAX;
                    
                    signed int* data_ptr = (signed int*)data_item->data;
                    signed int new_val = *data_ptr + step;
                    
                    if(new_val > max_val || new_val < *data_ptr)
                        new_val = max_val;
                    
                    *data_ptr = new_val;
                    
                    break;
                }
                case FLOAT:
                {
                    float step = data_item->has_step ? data_item->step.float_val : 1;
                    float max_val = data_item->has_max ? data_item->max.float_val : FLT_MAX;
                    
                    float* data_ptr = (float*)data_item->data;
                    float new_val = *data_ptr + step;
                    
                    if(new_val > max_val || new_val < *data_ptr)
                        new_val = max_val;
                    
                    *data_ptr = new_val;
                    
                    break;
                }
            }
            break;
        case EASY_MENU_DOWN:
            switch(data_item->data_type)
            {
                case UNSIGNED_CHAR:
                {
                    unsigned char step = data_item->has_step ? data_item->step.uint8_val : 1;
                    unsigned char min_val = data_item->has_min ? data_item->min.uint8_val : 0;
                    
                    unsigned char* data_ptr = (unsigned char*)data_item->data;
                    unsigned char new_val = *data_ptr - step;
                    
                    if(new_val < min_val || new_val > *data_ptr)
                        new_val = min_val;
                    
                    *data_ptr = new_val;
                    
                    break;
                }
                case UNSIGNED_SHORT_INT:
                {
                    unsigned short int step = data_item->has_step ? data_item->step.uint16_val : 1;
                    unsigned short int min_val = data_item->has_min ? data_item->min.uint16_val : 0;
                    
                    unsigned short int* data_ptr = (unsigned short int*)data_item->data;
                    unsigned short int new_val = *data_ptr - step;
                    
                    if(new_val < min_val || new_val > *data_ptr)
                        new_val = min_val;
                    
                    *data_ptr = new_val;
                    
                    break;
                }
                case UNSIGNED_INT:
                {
                    unsigned int step = data_item->has_step ? data_item->step.uint16_val : 1;
                    unsigned int min_val = data_item->has_min ? data_item->min.uint16_val : 0;
                    
                    unsigned int* data_ptr = (unsigned int*)data_item->data;
                    unsigned int new_val = *data_ptr - step;
                    
                    if(new_val < min_val || new_val > *data_ptr)
                        new_val = min_val;
                    
                    *data_ptr = new_val;
                    
                    break;
                }
                case SIGNED_CHAR:
                {
                    signed char step = data_item->has_step ? data_item->step.int8_val : 1;
                    signed char min_val = data_item->has_min ? data_item->min.int8_val : SCHAR_MIN;
                    
                    signed char* data_ptr = (signed char*)data_item->data;
                    signed char new_val = *data_ptr - step;
                    
                    if(new_val < min_val || new_val > *data_ptr)
                        new_val = min_val;
                    
                    *data_ptr = new_val;
                    
                    break;
                }
                case SIGNED_SHORT_INT:
                {
                    signed short int step = data_item->has_step ? data_item->step.int16_val : 1;
                    signed short int min_val = data_item->has_min ? data_item->min.int16_val : SHRT_MIN;
                    
                    signed short int* data_ptr = (signed short int*)data_item->data;
                    signed short int new_val = *data_ptr - step;
                    
                    if(new_val < min_val || new_val > *data_ptr)
                        new_val = min_val;
                    
                    *data_ptr = new_val;
                    
                    break;
                }
                case SIGNED_INT:
                {
                    signed int step = data_item->has_step ? data_item->step.int32_val : 1;
                    signed int min_val = data_item->has_min ? data_item->min.int32_val : INT_MIN;
                    
                    signed int* data_ptr = (signed int*)data_item->data;
                    signed int new_val = *data_ptr - step;
                    
                    if(new_val < min_val || new_val > *data_ptr)
                        new_val = min_val;
                    
                    *data_ptr = new_val;
                    
                    break;
                }
                case FLOAT:
                {
                    float step = data_item->has_step ? data_item->step.float_val : 1;
                    float min_val = data_item->has_min ? data_item->min.float_val : -FLT_MAX;
                    
                    float* data_ptr = (float*)data_item->data;
                    float new_val = *data_ptr - step;
                    
                    if(new_val < min_val || new_val > *data_ptr)
                        new_val = min_val;
                    
                    *data_ptr = new_val;
                    
                    break;
                }
            }
            break;
        default:
            break;
    }
    
    if(data_item->Callback != NULL)
        data_item->Callback(data_item->data);
}
/* ================================================================= 枚举条目 ================================================================= */
void Enum_Item_Init(Page *parent_page, Item *item, char *text, char **enum_str, unsigned char enum_num, void (*Callback)(char *str))
{
    item->parent_page = parent_page;
    item->type = ENUM_ITEM;
    item->text = text;
    
    item->Input = Enum_Item_Input;
    
    Enum_Item *enum_item = (Enum_Item*)item;

    enum_item->enum_str = enum_str;
    
    enum_item->enum_num = enum_num;
    enum_item->enum_str_index = 0;
    enum_item->Callback = Callback;
}

void Enum_Item_Input(Item *item, Easy_Menu_Input_TYPE user_input)
{
    Enum_Item *enum_item = (Enum_Item*)item;
    
    switch(user_input)
    {
        case EASY_MENU_UP:
            #if ENUM_ITEM_MODE == 0
                if(--enum_item->enum_str_index == 255)
                    enum_item->enum_str_index = 0;
            #else
                if(--enum_item->enum_str_index == 255)
                    enum_item->enum_str_index = enum_item->enum_num - 1;
            #endif
            break;
        case EASY_MENU_DOWN:
            #if ENUM_ITEM_MODE == 0
                if(++enum_item->enum_str_index == enum_item->enum_num)
                    enum_item->enum_str_index = enum_item->enum_num - 1;
            #else
                if(++enum_item->enum_str_index == enum_item->enum_num)
                    enum_item->enum_str_index = 0;
            #endif
            break;
        default:
            break;
    }
    
    if(enum_item->Callback != NULL)
        enum_item->Callback(enum_item->enum_str[enum_item->enum_str_index]);
}
/* ================================================================= 展示条目 ================================================================= */
void Show_Item_Init(Page *parent_page, Item *item, char *text, DATA_TYPE data_type, void *data, unsigned short int period, void (*Callback)(void))
{
    item->parent_page = parent_page;
    item->type = SHOW_ITEM;
    item->text = text;
    
    Show_Item *show_item = (Show_Item*)item;

    show_item->data_type = data_type;
    show_item->data = data;
    show_item->period = period;
    
    show_item->last_tick = 0;

    show_item->Callback = Callback;
}
/* ================================================================= 跳转条目 ================================================================= */
void Goto_Item_Init(Page *parent_page, Item *item, char *text, Page *target_page)
{
    item->parent_page = parent_page;
    item->type = GOTO_ITEM;
    item->text = text;
    
    item->Input = Goto_Item_Input;

    Goto_Item *goto_item = (Goto_Item*)item;
    goto_item->target_page = target_page;
}

void Goto_Item_Input(Item *item, Easy_Menu_Input_TYPE user_input)
{
    Goto_Item *goto_item = (Goto_Item*)item;
    
    if(user_input == EASY_MENU_RIGHT && goto_item->target_page != NULL)
    {
        Easy_Menu_Goto_Page(goto_item->target_page);
    }
}

