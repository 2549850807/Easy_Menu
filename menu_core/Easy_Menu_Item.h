#ifndef __EASY_MENU_ITEM_H__
#define __EASY_MENU_ITEM_H__

#include "Easy_Menu.h"

/* ================================================================= 文本条目 ================================================================= */
// ------ 功能介绍
/*
 * 在菜单上显示一行文本
 * 确认（右键）时触发一次回调函数
*/
// ------ 结构体
typedef struct Text_Item {
	Item item;
    void (*Callback)(char *str);
} Text_Item;
// ------ 相关函数
void Text_Item_Init(Page *parent_page, Item *item, char *text, void (*Callback)(char *str));
void Text_Item_Input(Item *item, Easy_Menu_Input_TYPE user_input);
/* ================================================================= 开关条目 ================================================================= */
// ------ 功能介绍
/*
 * 在菜单上显示开关量，结尾显示 [0/1] / [OFF/ON]
 * 修改数据时触发回调函数（进入所在页面时会自动触发一次回调函数）
*/
// ------ 结构体
typedef struct Switch_Item {
	Item item;
    unsigned char *data;
    
    void (*Callback)(unsigned char data);
} Switch_Item;
// ------ 相关函数
void Switch_Item_Init(Page *parent_page, Item *item, char *text, unsigned char *data, void (*Callback)(unsigned char data));
void Switch_Item_Input(Item *item, Easy_Menu_Input_TYPE user_input);
/* ================================================================= 数值条目 ================================================================= */
// ------ 功能介绍
/*
 * 在菜单上显示对应数据，小数只保留后两位
 * 修改数据时触发回调函数（进入所在页面时会自动触发一次回调函数）
*/
/* 数据条目类型枚举 */
typedef enum {
    UNSIGNED_CHAR,          // uint8
    UNSIGNED_SHORT_INT,     // uint16
    UNSIGNED_INT,           // uint32
    SIGNED_CHAR,            // int8
    SIGNED_SHORT_INT,       // int16
    SIGNED_INT,             // int32
    FLOAT,
} DATA_TYPE;
// ------ 联合体
typedef union {
    unsigned char uint8_val;
    unsigned short int uint16_val;
    unsigned int uint32_val;

    signed char int8_val;
    signed short int int16_val;
    signed int int32_val;
    
    float float_val;
} Data_Item_Value;
// ------ 结构体
typedef struct Data_Item {
	Item item;
    DATA_TYPE data_type;
    void *data;
    
    Data_Item_Value step;
    Data_Item_Value min;
    Data_Item_Value max;
    
    unsigned char has_step : 1;
    unsigned char has_min : 1;
    unsigned char has_max : 1;
    
    void (*Callback)(void *data);
} Data_Item;
// ------ 相关函数
void Data_Item_Init(Page *parent_page, Item *item, char *text, DATA_TYPE data_type, void *data, Data_Item_Value step, unsigned char use_step, Data_Item_Value min, unsigned char has_min,  Data_Item_Value max, unsigned char has_max,  void (*Callback)(void *data));
void Data_Item_Input(Item *item, Easy_Menu_Input_TYPE user_input);
// ------ 工具宏
#define UNSIGNED_CHAR_VAL(val) ((Data_Item_Value){.uint8_val = (val)})
#define UNSIGNED_SHORT_INT_VAL(val) ((Data_Item_Value){.uint16_val = (val)})
#define UNSIGNED_INT_VAL(val) ((Data_Item_Value){.uint32_val = (val)})

#define SIGNED_CHAR_VAL(val) ((Data_Item_Value){.int8_val = (val)})
#define SIGNED_SHORT_INT_VAL(val) ((Data_Item_Value){.int16_val = (val)})
#define SIGNED_INT_VAL(val) ((Data_Item_Value){.int32_val = (val)})

#define FLOAT_VAL(val) ((Data_Item_Value){.float_val = (val)})

/* ================================================================= 枚举条目 ================================================================= */
// ------ 功能介绍
/*
 * 在菜单上显示枚举列表中的文本
 * 修改数据时触发回调函数
*/
// ------ 结构体
typedef struct Enum_Item {
	Item item;
    char **enum_str;
    unsigned char enum_num;
    
    unsigned char enum_str_index;
    
    void (*Callback)(char *str);
} Enum_Item;
// ------ 相关函数
void Enum_Item_Init(Page *parent_page, Item *item, char *text, char **enum_str, unsigned char enum_num, void (*Callback)(char *str));
void Enum_Item_Input(Item *item, Easy_Menu_Input_TYPE user_input);
/* ================================================================= 展示条目 ================================================================= */
// ------ 功能介绍
/*
 * 在菜单上显示持续刷新的数据
 * 按周期触发回调函数（进入所在页面时会自动触发一次回调函数）
*/
// ------ 结构体
typedef struct Show_Item {
	Item item;
    DATA_TYPE data_type;
    void *data;

    unsigned short int period;  
    
    unsigned int last_tick;  
    
    void (*Callback)(void);
} Show_Item;
// ------ 相关函数
void Show_Item_Init(Page *parent_page, Item *item, char *text, DATA_TYPE data_type, void *data, unsigned short int period, void (*Callback)(void));

/* ================================================================= 跳转条目 ================================================================= */
// ------ 功能介绍
/*
 * 在菜单上显示一行文本
 * 确认（右键）时跳转到对应页面
*/
// ------ 结构体
typedef struct Goto_Item {
	Item item;
    Page *target_page;
} Goto_Item;
// ------ 相关函数
void Goto_Item_Init(Page *parent_page, Item *item, char *text, Page *target_page);
void Goto_Item_Input(Item *item, Easy_Menu_Input_TYPE user_input);

#endif 
