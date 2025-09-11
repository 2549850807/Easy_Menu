#include "menu_navigator.h"
#include <stdint.h>
#include <stdio.h>

// 生成的变量定义
typedef struct {
    bool led1;
    bool led2;
    bool led3;
    bool led4;
    bool led5;
    bool led6;
    float kp;
    float ki;
    float kd;
} menu_variables_t;

static menu_variables_t g_menu_vars = {
    .led1 = false,
    .led2 = false,
    .led3 = false,
    .led4 = false,
    .led5 = false,
    .led6 = false,
    .kp = 0.0f,
    .ki = 0.0f,
    .kd = 0.0f,
};

// 回调函数
void Kd_Change_Callback(void* value) {
    /* TODO: 实现实时变化回调函数 */
}

void Ki_Change_Callback(void* value) {
    /* TODO: 实现实时变化回调函数 */
}

void Kp_Change_Callback(void* value) {
    /* TODO: 实现实时变化回调函数 */
}

void Led1_Toggle_Callback(bool state) {
    /* TODO: 实现切换回调函数 */
}

void Led2_Toggle_Callback(bool state) {
    /* TODO: 实现切换回调函数 */
}

void Led3_Toggle_Callback(bool state) {
    /* TODO: 实现切换回调函数 */
}

void Led4_Toggle_Callback(bool state) {
    /* TODO: 实现切换回调函数 */
}

void Led5_Toggle_Callback(bool state) {
    /* TODO: 实现切换回调函数 */
}

void Led6_Toggle_Callback(bool state) {
    /* TODO: 实现切换回调函数 */
}

void Led_Off_App_Callback(void** args) {
    /* TODO: 实现应用回调函数 */
}

void Led_On_App_Callback(void** args) {
    /* TODO: 实现应用回调函数 */
}

void Nav_Exhibition_Callback(navigator_t* nav) {
    char buffer[MAX_DISPLAY_CHAR];
    /* TODO: 实现无分页展示回调函数 */
    for(unsigned char i = 1; i < MAX_DISPLAY_ITEM; i++)
    {
      snprintf(buffer, sizeof(buffer), "data%d", i);
      navigator_write_display_line(nav, buffer, i);
    }
}

void Page_Exhibition_Callback(navigator_t* nav, uint8_t current_page, uint8_t total_pages) {
    char buffer[MAX_DISPLAY_CHAR];
    /* TODO: 实现分页展示回调函数 */
    switch(current_page)
    {
    case 0:
        /* TODO: 实现第0页的显示内容 */
        for(unsigned char i = 1, data_num = current_page * (MAX_DISPLAY_ITEM - 1); i < MAX_DISPLAY_ITEM; i++, data_num++)
        {
          snprintf(buffer, sizeof(buffer), "data%d", data_num);
          navigator_write_display_line(nav, buffer, i);
        }
        break;
    case 1:
        /* TODO: 实现第1页的显示内容 */
        for(unsigned char i = 1, data_num = current_page * (MAX_DISPLAY_ITEM - 1); i < MAX_DISPLAY_ITEM; i++, data_num++)
        {
          snprintf(buffer, sizeof(buffer), "data%d", data_num);
          navigator_write_display_line(nav, buffer, i);
        }
        break;
    case 2:
        /* TODO: 实现第2页的显示内容 */
        for(unsigned char i = 1, data_num = current_page * (MAX_DISPLAY_ITEM - 1); i < MAX_DISPLAY_ITEM; i++, data_num++)
        {
          snprintf(buffer, sizeof(buffer), "data%d", data_num);
          navigator_write_display_line(nav, buffer, i);
        }
        break;
    case 3:
        /* TODO: 实现第3页的显示内容 */
        for(unsigned char i = 1, data_num = current_page * (MAX_DISPLAY_ITEM - 1); i < MAX_DISPLAY_ITEM; i++, data_num++)
        {
          snprintf(buffer, sizeof(buffer), "data%d", data_num);
          navigator_write_display_line(nav, buffer, i);
        }
        break;
    case 4:
        /* TODO: 实现第4页的显示内容 */
        for(unsigned char i = 1, data_num = current_page * (MAX_DISPLAY_ITEM - 1); i < MAX_DISPLAY_ITEM; i++, data_num++)
        {
          snprintf(buffer, sizeof(buffer), "data%d", data_num);
          navigator_write_display_line(nav, buffer, i);
        }
        break;
    case 5:
        /* TODO: 实现第5页的显示内容 */
        for(unsigned char i = 1, data_num = current_page * (MAX_DISPLAY_ITEM - 1); i < MAX_DISPLAY_ITEM; i++, data_num++)
        {
          snprintf(buffer, sizeof(buffer), "data%d", data_num);
          navigator_write_display_line(nav, buffer, i);
        }
        break;
    }
}


// 创建菜单项
static menu_item_t* Create_End_Menu(void) {
    static menu_item_t** no_children = NULL;
    return menu_create_normal_item("End", no_children, 0);
}

static menu_item_t* Create_N1_1_1_1_1_1_Menu(void) {
    static menu_item_t* n1_1_1_1_1_1_children[1];

    n1_1_1_1_1_1_children[0] = Create_End_Menu();

    return menu_create_normal_item("n1_1_1_1_1_1", n1_1_1_1_1_1_children, 1);
}

static menu_item_t* Create_N1_1_1_1_1_Menu(void) {
    static menu_item_t* n1_1_1_1_1_children[1];

    n1_1_1_1_1_children[0] = Create_N1_1_1_1_1_1_Menu();

    return menu_create_normal_item("n1_1_1_1_1", n1_1_1_1_1_children, 1);
}

static menu_item_t* Create_N1_1_1_1_2_Menu(void) {
    static menu_item_t** no_children = NULL;
    return menu_create_normal_item("n1_1_1_1_2", no_children, 0);
}

static menu_item_t* Create_N1_1_1_1_Menu(void) {
    static menu_item_t* n1_1_1_1_children[2];

    n1_1_1_1_children[0] = Create_N1_1_1_1_1_Menu();
    n1_1_1_1_children[1] = Create_N1_1_1_1_2_Menu();

    return menu_create_normal_item("n1_1_1_1", n1_1_1_1_children, 2);
}

static menu_item_t* Create_N1_1_1_2_Menu(void) {
    static menu_item_t** no_children = NULL;
    return menu_create_normal_item("n1_1_1_2", no_children, 0);
}

static menu_item_t* Create_N1_1_1_3_Menu(void) {
    static menu_item_t** no_children = NULL;
    return menu_create_normal_item("n1_1_1_3", no_children, 0);
}

static menu_item_t* Create_N1_1_1_Menu(void) {
    static menu_item_t* n1_1_1_children[3];

    n1_1_1_children[0] = Create_N1_1_1_1_Menu();
    n1_1_1_children[1] = Create_N1_1_1_2_Menu();
    n1_1_1_children[2] = Create_N1_1_1_3_Menu();

    return menu_create_normal_item("n1_1_1", n1_1_1_children, 3);
}

static menu_item_t* Create_N1_1_2_Menu(void) {
    static menu_item_t** no_children = NULL;
    return menu_create_normal_item("n1_1_2", no_children, 0);
}

static menu_item_t* Create_N1_1_3_Menu(void) {
    static menu_item_t** no_children = NULL;
    return menu_create_normal_item("n1_1_3", no_children, 0);
}

static menu_item_t* Create_N1_1_4_Menu(void) {
    static menu_item_t** no_children = NULL;
    return menu_create_normal_item("n1_1_4", no_children, 0);
}

static menu_item_t* Create_N1_1_Menu(void) {
    static menu_item_t* n1_1_children[4];

    n1_1_children[0] = Create_N1_1_1_Menu();
    n1_1_children[1] = Create_N1_1_2_Menu();
    n1_1_children[2] = Create_N1_1_3_Menu();
    n1_1_children[3] = Create_N1_1_4_Menu();

    return menu_create_normal_item("n1_1", n1_1_children, 4);
}

static menu_item_t* Create_N1_2_Menu(void) {
    static menu_item_t** no_children = NULL;
    return menu_create_normal_item("n1_2", no_children, 0);
}

static menu_item_t* Create_N1_3_Menu(void) {
    static menu_item_t** no_children = NULL;
    return menu_create_normal_item("n1_3", no_children, 0);
}

static menu_item_t* Create_N1_4_Menu(void) {
    static menu_item_t** no_children = NULL;
    return menu_create_normal_item("n1_4", no_children, 0);
}

static menu_item_t* Create_N1_5_Menu(void) {
    static menu_item_t** no_children = NULL;
    return menu_create_normal_item("n1_5", no_children, 0);
}

static menu_item_t* Create_N1_Menu(void) {
    static menu_item_t* n1_children[5];

    n1_children[0] = Create_N1_1_Menu();
    n1_children[1] = Create_N1_2_Menu();
    n1_children[2] = Create_N1_3_Menu();
    n1_children[3] = Create_N1_4_Menu();
    n1_children[4] = Create_N1_5_Menu();

    return menu_create_normal_item("n1", n1_children, 5);
}

static menu_item_t* Create_N2_Menu(void) {
    static menu_item_t** no_children = NULL;
    return menu_create_normal_item("n2", no_children, 0);
}

static menu_item_t* Create_N3_Menu(void) {
    static menu_item_t** no_children = NULL;
    return menu_create_normal_item("n3", no_children, 0);
}

static menu_item_t* Create_N4_Menu(void) {
    static menu_item_t** no_children = NULL;
    return menu_create_normal_item("n4", no_children, 0);
}

static menu_item_t* Create_N5_Menu(void) {
    static menu_item_t** no_children = NULL;
    return menu_create_normal_item("n5", no_children, 0);
}

static menu_item_t* Create_N6_Menu(void) {
    static menu_item_t** no_children = NULL;
    return menu_create_normal_item("n6", no_children, 0);
}

static menu_item_t* Create_Normal_Menu(void) {
    static menu_item_t* Normal_children[6];

    Normal_children[0] = Create_N1_Menu();
    Normal_children[1] = Create_N2_Menu();
    Normal_children[2] = Create_N3_Menu();
    Normal_children[3] = Create_N4_Menu();
    Normal_children[4] = Create_N5_Menu();
    Normal_children[5] = Create_N6_Menu();

    return menu_create_normal_item("Normal", Normal_children, 6);
}

static menu_item_t* Create_Led1_Menu(void) {
    return menu_create_toggle_item("LED1", &g_menu_vars.led1, Led1_Toggle_Callback);
}

static menu_item_t* Create_Led2_Menu(void) {
    return menu_create_toggle_item("LED2", &g_menu_vars.led2, Led2_Toggle_Callback);
}

static menu_item_t* Create_Led3_Menu(void) {
    return menu_create_toggle_item("LED3", &g_menu_vars.led3, Led3_Toggle_Callback);
}

static menu_item_t* Create_Led4_Menu(void) {
    return menu_create_toggle_item("LED4", &g_menu_vars.led4, Led4_Toggle_Callback);
}

static menu_item_t* Create_Led5_Menu(void) {
    return menu_create_toggle_item("LED5", &g_menu_vars.led5, Led5_Toggle_Callback);
}

static menu_item_t* Create_Led6_Menu(void) {
    return menu_create_toggle_item("LED6", &g_menu_vars.led6, Led6_Toggle_Callback);
}

static menu_item_t* Create_Toggle_Menu(void) {
    static menu_item_t* Toggle_children[6];

    Toggle_children[0] = Create_Led1_Menu();
    Toggle_children[1] = Create_Led2_Menu();
    Toggle_children[2] = Create_Led3_Menu();
    Toggle_children[3] = Create_Led4_Menu();
    Toggle_children[4] = Create_Led5_Menu();
    Toggle_children[5] = Create_Led6_Menu();

    return menu_create_normal_item("Toggle", Toggle_children, 6);
}

static menu_item_t* Create_Kp_Menu(void) {
    static float kp_min_val = 0.0f;
    static float kp_max_val = 100.0f;
    static float kp_step_val = 1.0f;
    return menu_create_changeable_item("Kp", &g_menu_vars.kp, &kp_min_val, &kp_max_val, &kp_step_val, DATA_TYPE_FLOAT, Kp_Change_Callback);
}

static menu_item_t* Create_Ki_Menu(void) {
    static float ki_min_val = 0.0f;
    static float ki_max_val = 100.0f;
    static float ki_step_val = 1.0f;
    return menu_create_changeable_item("Ki", &g_menu_vars.ki, &ki_min_val, &ki_max_val, &ki_step_val, DATA_TYPE_FLOAT, Ki_Change_Callback);
}

static menu_item_t* Create_Kd_Menu(void) {
    static float kd_min_val = 0.0f;
    static float kd_max_val = 100.0f;
    static float kd_step_val = 1.0f;
    return menu_create_changeable_item("Kd", &g_menu_vars.kd, &kd_min_val, &kd_max_val, &kd_step_val, DATA_TYPE_FLOAT, Kd_Change_Callback);
}

static menu_item_t* Create_Changeable_Menu(void) {
    static menu_item_t* Changeable_children[3];

    Changeable_children[0] = Create_Kp_Menu();
    Changeable_children[1] = Create_Ki_Menu();
    Changeable_children[2] = Create_Kd_Menu();

    return menu_create_normal_item("Changeable", Changeable_children, 3);
}

static menu_item_t* Create_Led_On_Menu(void) {
    return menu_create_app_item("LED_ON", NULL, Led_On_App_Callback);
}

static menu_item_t* Create_Led_Off_Menu(void) {
    return menu_create_app_item("LED_OFF", NULL, Led_Off_App_Callback);
}

static menu_item_t* Create_Application_Menu(void) {
    static menu_item_t* Application_children[2];

    Application_children[0] = Create_Led_On_Menu();
    Application_children[1] = Create_Led_Off_Menu();

    return menu_create_normal_item("Application", Application_children, 2);
}

static menu_item_t* Create_Nav_Menu(void) {
    return menu_create_exhibition_item("Nav", 1, Nav_Exhibition_Callback);
}

static menu_item_t* Create_Page_Menu(void) {
    return menu_create_exhibition_item("Page", 6, Page_Exhibition_Callback);
}

static menu_item_t* Create_Exhibtion_Menu(void) {
    static menu_item_t* Exhibtion_children[2];

    Exhibtion_children[0] = Create_Nav_Menu();
    Exhibtion_children[1] = Create_Page_Menu();

    return menu_create_normal_item("Exhibtion", Exhibtion_children, 2);
}


static menu_item_t* Create_Main_Menu(void) {
    static menu_item_t* main_children[5];

    main_children[0] = Create_Normal_Menu();
    main_children[1] = Create_Toggle_Menu();
    main_children[2] = Create_Changeable_Menu();
    main_children[3] = Create_Application_Menu();
    main_children[4] = Create_Exhibtion_Menu();

    return menu_create_normal_item("Main", main_children, 5);
}

// 获取主菜单项
void* getMainItem(void) {
    return Create_Main_Menu();
}