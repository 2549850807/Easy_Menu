#include "menu_wrapper.h"
#include "menu_navigator.h"

void* menu_builder(void* mainMenu)
{
    return navigator_create((menu_item_t*)mainMenu);
}

void menu_delete(void* navigator)
{
    navigator_destroy((navigator_t*)navigator);
}

void menu_handle_input(void* navigator, uint8_t key_value)
{
    navigator_t* nav = (navigator_t*)navigator;
    key_value_t key;
    
    switch (key_value)
    {
    case UP:
        key = KEY_UP;
        break;
    case DOWN:
        key = KEY_DOWN;
        break;
    case LEFT:
        key = KEY_LEFT;
        break;
    case RIGHT:
        key = KEY_RIGHT;
        break;
    default:
        key = KEY_NONE;
        break;
    }
    
    navigator_handle_input(nav, key);
}

void menu_refresh_display(void* navigator)
{
    navigator_refresh_display((navigator_t*)navigator);
}

char* menu_get_display_buffer(void* navigator)
{
    return navigator_get_display_buffer((navigator_t*)navigator);
}

uint8_t menu_get_app_mode(void* navigator)
{
    return navigator_get_app_mode((navigator_t*)navigator) ? 1 : 0;
}

void menu_set_app_mode(void* navigator, uint8_t mode)
{
    navigator_set_app_mode((navigator_t*)navigator, mode != 0);
}

void menu_force_refresh_display(void* navigator)
{
    navigator_force_refresh_display((navigator_t*)navigator);
}

void menu_exhibition_next_page(void* navigator)
{
    navigator_exhibition_next_page((navigator_t*)navigator);
}

void menu_exhibition_prev_page(void* navigator)
{
    navigator_exhibition_prev_page((navigator_t*)navigator);
}

void menu_exhibition_reset_to_first_page(void* navigator)
{
    navigator_exhibition_reset_to_first_page((navigator_t*)navigator);
}

uint8_t menu_exhibition_get_current_page(void* navigator)
{
    return navigator_get_exhibition_current_page((navigator_t*)navigator);
}

uint8_t menu_exhibition_get_total_pages(void* navigator)
{
    return navigator_get_exhibition_total_pages((navigator_t*)navigator);
}

uint8_t menu_exhibition_is_pageable(void* navigator)
{
    return navigator_is_exhibition_pageable((navigator_t*)navigator) ? 1 : 0;
}

const char* menu_get_current_page_name(void* navigator)
{
    return navigator_get_current_page_name((navigator_t*)navigator);
}

const char* menu_get_current_selected_item_name(void* navigator)
{
    return navigator_get_current_selected_item_name((navigator_t*)navigator);
}

uint8_t menu_is_in_exhibition_mode(void* navigator)
{
    return navigator_is_in_exhibition_mode((navigator_t*)navigator) ? 1 : 0;
}
