#include "menu_wrapper.h"
#include "menu_navigator.h"
#include <string.h>
#include <stdio.h>

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

void menu_display(void* navigator)
{
  menu_refresh_display(navigator);
  
  char* display_buffer = menu_get_display_buffer(navigator);
  
  for(unsigned char line = 0; line < MAX_DISPLAY_ITEM; line++)
  {
        static char line_buffer[MAX_DISPLAY_CHAR + 1];
        char* line_start = display_buffer + (MAX_DISPLAY_CHAR * line);
        
        unsigned char len = 0;
        while (len < MAX_DISPLAY_CHAR && line_start[len] != '\0') {
            line_buffer[len] = line_start[len];
            len++;
        }
        
        while (len < MAX_DISPLAY_CHAR) {
            line_buffer[len++] = ' ';
        }
        line_buffer[MAX_DISPLAY_CHAR] = '\0';
      
        menu_show_string(line, line_buffer);
  }
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

static menu_item_t* find_item_by_name(menu_item_t* item, const char* name) {
    if (item == NULL) {
        return NULL;
    }

    if (strcmp(item->item_name, name) == 0) {
        return item;
    }

    if (item->children_items != NULL) {
        for (uint8_t i = 0; i < item->children_count; i++) {
            menu_item_t* found = find_item_by_name(item->children_items[i], name);
            if (found != NULL) {
                return found;
            }
        }
    }

    return NULL;
}

void menu_goto(void* navigator, const char* menu_name)
{
    navigator_t* nav = (navigator_t*)navigator;
    if (!nav || !menu_name) {
        return;
    }

    if (navigator_get_app_mode(nav)) {
        navigator_set_app_mode(nav, false);
    }

    menu_item_t* root_item = nav->current_menu;
    while (root_item && root_item->parent_item) {
        root_item = root_item->parent_item;
    }

    if (!root_item) {
        return;
    }

    menu_item_t* target_item = find_item_by_name(root_item, menu_name);

    if (target_item) {
        if (target_item->type == MENU_TYPE_NORMAL && target_item->children_count > 0) {
            nav->current_menu = target_item;
            nav->selected_index = 0;
            nav->first_visible_item = 0;
            navigator_force_refresh_display(nav);
        } else if (target_item->type == MENU_TYPE_EXHIBITION) {
            if (target_item->parent_item) {
                nav->current_menu = target_item->parent_item;
                
                for (uint8_t i = 0; i < target_item->parent_item->children_count; i++) {
                    if (target_item->parent_item->children_items[i] == target_item) {
                        nav->selected_index = i;
                        break;
                    }
                }
                
                if (nav->selected_index < nav->first_visible_item) {
                    nav->first_visible_item = nav->selected_index;
                } else if (nav->selected_index >= nav->first_visible_item + MAX_DISPLAY_ITEM) {
                    nav->first_visible_item = nav->selected_index - MAX_DISPLAY_ITEM + 1;
                }
                
                navigator_force_refresh_display(nav);
                menu_handle_input(nav, RIGHT);
            }
        } else {
            char* buffer = navigator_get_display_buffer(nav);
            if (buffer) {
                memset(buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
                snprintf(buffer, MAX_DISPLAY_CHAR, "Cannot goto %s", menu_name);
            }
            navigator_set_app_mode(nav, true);
        }
    } else {
        char* buffer = navigator_get_display_buffer(nav);
        if (buffer) {
            memset(buffer, 0, MAX_DISPLAY_CHAR * MAX_DISPLAY_ITEM);
            snprintf(buffer, MAX_DISPLAY_CHAR, "No Have %s", menu_name);
        }
        navigator_set_app_mode(nav, true);
    }
}
