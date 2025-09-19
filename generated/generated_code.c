#include "menu_navigator.h"
#include "menu_wrapper.h"
#include <stdint.h>
#include <stdio.h>

/* ============================ 生成的变量定义 ============================  */
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

/* ============================ 回调函数 ============================  */
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

void Nav_Exhibition_Callback(navigator_t* nav, uint8_t current_page, uint8_t total_pages) {
    char buffer[MAX_DISPLAY_CHAR];
    /* TODO: 实现无分页展示回调函数 */
    snprintf(buffer, sizeof(buffer), "data1");
    navigator_write_display_line(nav, buffer, 1);
    
    snprintf(buffer, sizeof(buffer), "data2");
    navigator_write_display_line(nav, buffer, 2);
    
    snprintf(buffer, sizeof(buffer), "data3");
    navigator_write_display_line(nav, buffer, 3);
}

void Page_Exhibition_Callback(navigator_t* nav, uint8_t current_page, uint8_t total_pages) {
    char buffer[MAX_DISPLAY_CHAR];
    /* TODO: 实现分页展示回调函数 */
    switch(current_page)
    {
    case 0:
        /* TODO: 实现第0页的显示内容 */
        snprintf(buffer, sizeof(buffer), "data1");
        navigator_write_display_line(nav, buffer, 1);

        snprintf(buffer, sizeof(buffer), "data2");
        navigator_write_display_line(nav, buffer, 2);

        snprintf(buffer, sizeof(buffer), "data3");
        navigator_write_display_line(nav, buffer, 3);

        break;
    case 1:
        /* TODO: 实现第1页的显示内容 */
        snprintf(buffer, sizeof(buffer), "data4");
        navigator_write_display_line(nav, buffer, 1);

        snprintf(buffer, sizeof(buffer), "data5");
        navigator_write_display_line(nav, buffer, 2);

        snprintf(buffer, sizeof(buffer), "data6");
        navigator_write_display_line(nav, buffer, 3);

        break;
    case 2:
        /* TODO: 实现第2页的显示内容 */
        snprintf(buffer, sizeof(buffer), "data7");
        navigator_write_display_line(nav, buffer, 1);

        snprintf(buffer, sizeof(buffer), "data8");
        navigator_write_display_line(nav, buffer, 2);

        snprintf(buffer, sizeof(buffer), "data9");
        navigator_write_display_line(nav, buffer, 3);

        break;
    case 3:
        /* TODO: 实现第3页的显示内容 */
        snprintf(buffer, sizeof(buffer), "data10");
        navigator_write_display_line(nav, buffer, 1);

        snprintf(buffer, sizeof(buffer), "data11");
        navigator_write_display_line(nav, buffer, 2);

        snprintf(buffer, sizeof(buffer), "data12");
        navigator_write_display_line(nav, buffer, 3);

        break;
    case 4:
        /* TODO: 实现第4页的显示内容 */
        snprintf(buffer, sizeof(buffer), "data13");
        navigator_write_display_line(nav, buffer, 1);

        snprintf(buffer, sizeof(buffer), "data14");
        navigator_write_display_line(nav, buffer, 2);

        snprintf(buffer, sizeof(buffer), "data15");
        navigator_write_display_line(nav, buffer, 3);

        break;
    case 5:
        /* TODO: 实现第5页的显示内容 */
        snprintf(buffer, sizeof(buffer), "data16");
        navigator_write_display_line(nav, buffer, 1);

        snprintf(buffer, sizeof(buffer), "data17");
        navigator_write_display_line(nav, buffer, 2);

        snprintf(buffer, sizeof(buffer), "data18");
        navigator_write_display_line(nav, buffer, 3);

        break;
    }
}


/* ============================ 静态菜单项定义 ============================  */

static menu_item_t menu_main;
static menu_item_t menu_normal;
static menu_item_t menu_n1;
static menu_item_t menu_n1_1;
static menu_item_t menu_n1_1_1;
static menu_item_t menu_n1_1_1_1;
static menu_item_t menu_n1_1_1_1_1;
static menu_item_t menu_n1_1_1_1_1_1;
static menu_item_t menu_end;
static menu_item_t menu_n1_1_1_1_2;
static menu_item_t menu_n1_1_1_2;
static menu_item_t menu_n1_1_1_3;
static menu_item_t menu_n1_1_2;
static menu_item_t menu_n1_1_3;
static menu_item_t menu_n1_1_4;
static menu_item_t menu_n1_2;
static menu_item_t menu_n1_3;
static menu_item_t menu_n1_4;
static menu_item_t menu_n1_5;
static menu_item_t menu_n2;
static menu_item_t menu_n3;
static menu_item_t menu_n4;
static menu_item_t menu_n5;
static menu_item_t menu_n6;
static menu_item_t menu_toggle;
static menu_item_t menu_led1;
static menu_item_t menu_led2;
static menu_item_t menu_led3;
static menu_item_t menu_led4;
static menu_item_t menu_led5;
static menu_item_t menu_led6;
static menu_item_t menu_changeable;
static menu_item_t menu_kp;
static menu_item_t menu_ki;
static menu_item_t menu_kd;
static menu_item_t menu_application;
static menu_item_t menu_led_on;
static menu_item_t menu_led_off;
static menu_item_t menu_exhibtion;
static menu_item_t menu_nav;
static menu_item_t menu_page;

static menu_item_t* main_children[] = {&menu_normal, &menu_toggle, &menu_changeable, &menu_application, &menu_exhibtion};
static menu_item_t* normal_children[] = {&menu_n1, &menu_n2, &menu_n3, &menu_n4, &menu_n5, &menu_n6};
static menu_item_t* n1_children[] = {&menu_n1_1, &menu_n1_2, &menu_n1_3, &menu_n1_4, &menu_n1_5};
static menu_item_t* n1_1_children[] = {&menu_n1_1_1, &menu_n1_1_2, &menu_n1_1_3, &menu_n1_1_4};
static menu_item_t* n1_1_1_children[] = {&menu_n1_1_1_1, &menu_n1_1_1_2, &menu_n1_1_1_3};
static menu_item_t* n1_1_1_1_children[] = {&menu_n1_1_1_1_1, &menu_n1_1_1_1_2};
static menu_item_t* n1_1_1_1_1_children[] = {&menu_n1_1_1_1_1_1};
static menu_item_t* n1_1_1_1_1_1_children[] = {&menu_end};
static menu_item_t* toggle_children[] = {&menu_led1, &menu_led2, &menu_led3, &menu_led4, &menu_led5, &menu_led6};
static menu_item_t* changeable_children[] = {&menu_kp, &menu_ki, &menu_kd};
static menu_item_t* application_children[] = {&menu_led_on, &menu_led_off};
static menu_item_t* exhibtion_children[] = {&menu_nav, &menu_page};

static float kp_min_val = 0.0f;
static float kp_max_val = 100.0f;
static float kp_step_val = 1.0f;
static float ki_min_val = 0.0f;
static float ki_max_val = 100.0f;
static float ki_step_val = 1.0f;
static float kd_min_val = 0.0f;
static float kd_max_val = 100.0f;
static float kd_step_val = 1.0f;

static menu_item_t menu_main = {
    .is_locked = true,
    .item_name = "Main",
    .parent_item = NULL,
    .children_items = main_children,
    .children_count = 5,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_normal = {
    .is_locked = true,
    .item_name = "Normal",
    .parent_item = &menu_main,
    .children_items = normal_children,
    .children_count = 6,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n1 = {
    .is_locked = true,
    .item_name = "n1",
    .parent_item = &menu_normal,
    .children_items = n1_children,
    .children_count = 5,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n1_1 = {
    .is_locked = true,
    .item_name = "n1_1",
    .parent_item = &menu_n1,
    .children_items = n1_1_children,
    .children_count = 4,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n1_1_1 = {
    .is_locked = true,
    .item_name = "n1_1_1",
    .parent_item = &menu_n1_1,
    .children_items = n1_1_1_children,
    .children_count = 3,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n1_1_1_1 = {
    .is_locked = true,
    .item_name = "n1_1_1_1",
    .parent_item = &menu_n1_1_1,
    .children_items = n1_1_1_1_children,
    .children_count = 2,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n1_1_1_1_1 = {
    .is_locked = true,
    .item_name = "n1_1_1_1_1",
    .parent_item = &menu_n1_1_1_1,
    .children_items = n1_1_1_1_1_children,
    .children_count = 1,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n1_1_1_1_1_1 = {
    .is_locked = true,
    .item_name = "n1_1_1_1_1_1",
    .parent_item = &menu_n1_1_1_1_1,
    .children_items = n1_1_1_1_1_1_children,
    .children_count = 1,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_end = {
    .is_locked = true,
    .item_name = "End",
    .parent_item = &menu_n1_1_1_1_1_1,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n1_1_1_1_2 = {
    .is_locked = true,
    .item_name = "n1_1_1_1_2",
    .parent_item = &menu_n1_1_1_1,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n1_1_1_2 = {
    .is_locked = true,
    .item_name = "n1_1_1_2",
    .parent_item = &menu_n1_1_1,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n1_1_1_3 = {
    .is_locked = true,
    .item_name = "n1_1_1_3",
    .parent_item = &menu_n1_1_1,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n1_1_2 = {
    .is_locked = true,
    .item_name = "n1_1_2",
    .parent_item = &menu_n1_1,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n1_1_3 = {
    .is_locked = true,
    .item_name = "n1_1_3",
    .parent_item = &menu_n1_1,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n1_1_4 = {
    .is_locked = true,
    .item_name = "n1_1_4",
    .parent_item = &menu_n1_1,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n1_2 = {
    .is_locked = true,
    .item_name = "n1_2",
    .parent_item = &menu_n1,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n1_3 = {
    .is_locked = true,
    .item_name = "n1_3",
    .parent_item = &menu_n1,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n1_4 = {
    .is_locked = true,
    .item_name = "n1_4",
    .parent_item = &menu_n1,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n1_5 = {
    .is_locked = true,
    .item_name = "n1_5",
    .parent_item = &menu_n1,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n2 = {
    .is_locked = true,
    .item_name = "n2",
    .parent_item = &menu_normal,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n3 = {
    .is_locked = true,
    .item_name = "n3",
    .parent_item = &menu_normal,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n4 = {
    .is_locked = true,
    .item_name = "n4",
    .parent_item = &menu_normal,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n5 = {
    .is_locked = true,
    .item_name = "n5",
    .parent_item = &menu_normal,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_n6 = {
    .is_locked = true,
    .item_name = "n6",
    .parent_item = &menu_normal,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_toggle = {
    .is_locked = true,
    .item_name = "Toggle",
    .parent_item = &menu_main,
    .children_items = toggle_children,
    .children_count = 6,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_led1 = {
    .is_locked = true,
    .item_name = "LED1",
    .parent_item = &menu_toggle,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_TOGGLE,
    .data.toggle = {
        .state = false,
        .ref = &g_menu_vars.led1,
        .on_toggle = Led1_Toggle_Callback
    }
};

static menu_item_t menu_led2 = {
    .is_locked = true,
    .item_name = "LED2",
    .parent_item = &menu_toggle,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_TOGGLE,
    .data.toggle = {
        .state = false,
        .ref = &g_menu_vars.led2,
        .on_toggle = Led2_Toggle_Callback
    }
};

static menu_item_t menu_led3 = {
    .is_locked = true,
    .item_name = "LED3",
    .parent_item = &menu_toggle,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_TOGGLE,
    .data.toggle = {
        .state = false,
        .ref = &g_menu_vars.led3,
        .on_toggle = Led3_Toggle_Callback
    }
};

static menu_item_t menu_led4 = {
    .is_locked = true,
    .item_name = "LED4",
    .parent_item = &menu_toggle,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_TOGGLE,
    .data.toggle = {
        .state = false,
        .ref = &g_menu_vars.led4,
        .on_toggle = Led4_Toggle_Callback
    }
};

static menu_item_t menu_led5 = {
    .is_locked = true,
    .item_name = "LED5",
    .parent_item = &menu_toggle,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_TOGGLE,
    .data.toggle = {
        .state = false,
        .ref = &g_menu_vars.led5,
        .on_toggle = Led5_Toggle_Callback
    }
};

static menu_item_t menu_led6 = {
    .is_locked = true,
    .item_name = "LED6",
    .parent_item = &menu_toggle,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_TOGGLE,
    .data.toggle = {
        .state = false,
        .ref = &g_menu_vars.led6,
        .on_toggle = Led6_Toggle_Callback
    }
};

static menu_item_t menu_changeable = {
    .is_locked = true,
    .item_name = "Changeable",
    .parent_item = &menu_main,
    .children_items = changeable_children,
    .children_count = 3,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_kp = {
    .is_locked = true,
    .item_name = "Kp",
    .parent_item = &menu_changeable,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_CHANGEABLE,
    .data.changeable = {
        .ref = &g_menu_vars.kp,
        .min_val = &kp_min_val,
        .max_val = &kp_max_val,
        .step_val = &kp_step_val,
        .data_type = DATA_TYPE_FLOAT,
        .on_change = Kp_Change_Callback
    }
};

static menu_item_t menu_ki = {
    .is_locked = true,
    .item_name = "Ki",
    .parent_item = &menu_changeable,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_CHANGEABLE,
    .data.changeable = {
        .ref = &g_menu_vars.ki,
        .min_val = &ki_min_val,
        .max_val = &ki_max_val,
        .step_val = &ki_step_val,
        .data_type = DATA_TYPE_FLOAT,
        .on_change = Ki_Change_Callback
    }
};

static menu_item_t menu_kd = {
    .is_locked = true,
    .item_name = "Kd",
    .parent_item = &menu_changeable,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_CHANGEABLE,
    .data.changeable = {
        .ref = &g_menu_vars.kd,
        .min_val = &kd_min_val,
        .max_val = &kd_max_val,
        .step_val = &kd_step_val,
        .data_type = DATA_TYPE_FLOAT,
        .on_change = Kd_Change_Callback
    }
};

static menu_item_t menu_application = {
    .is_locked = true,
    .item_name = "Application",
    .parent_item = &menu_main,
    .children_items = application_children,
    .children_count = 2,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_led_on = {
    .is_locked = true,
    .item_name = "LED_ON",
    .parent_item = &menu_application,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL,
    .app_func = Led_On_App_Callback,
    .app_args = NULL
};

static menu_item_t menu_led_off = {
    .is_locked = true,
    .item_name = "LED_OFF",
    .parent_item = &menu_application,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_NORMAL,
    .app_func = Led_Off_App_Callback,
    .app_args = NULL
};

static menu_item_t menu_exhibtion = {
    .is_locked = true,
    .item_name = "Exhibtion",
    .parent_item = &menu_main,
    .children_items = exhibtion_children,
    .children_count = 2,
    .type = MENU_TYPE_NORMAL
};

static menu_item_t menu_nav = {
    .is_locked = true,
    .item_name = "Nav",
    .parent_item = &menu_exhibtion,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_EXHIBITION,
    .periodic_callback_with_page = Nav_Exhibition_Callback,
    .data.exhibition = {
        .current_page = 0,
        .total_pages = 1,
        .lines_per_page = MAX_DISPLAY_ITEM - 1
    }
};

static menu_item_t menu_page = {
    .is_locked = true,
    .item_name = "Page",
    .parent_item = &menu_exhibtion,
    .children_items = NULL,
    .children_count = 0,
    .type = MENU_TYPE_EXHIBITION,
    .periodic_callback_with_page = Page_Exhibition_Callback,
    .data.exhibition = {
        .current_page = 0,
        .total_pages = 6,
        .lines_per_page = MAX_DISPLAY_ITEM - 1
    }
};


/* ============================ 兼容性函数 ============================  */
static menu_item_t* Create_Main_Menu(void) {
    return &menu_main;
}

/* ============================ 获取主菜单项 ============================  */
void* getMainItem(void) {
    return Create_Main_Menu();
}
