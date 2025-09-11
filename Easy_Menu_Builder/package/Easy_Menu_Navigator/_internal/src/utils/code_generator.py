from typing import List, Dict, Any, Set
from ..models.menu_config_model import MenuConfigModel
from ..models.menu_item_model import MenuItemModel, MenuItemType, DataType


class CodeGenerator:
    def __init__(self, config: MenuConfigModel):
        self.config = config
        self.includes = ['#include "menu_navigator.h"', '#include <stdint.h>', '#include <stdio.h>']

    def generate_c_code(self) -> str:
        """生成完整的C代码"""
        if not self.config.root_item:
            return "// 未找到根菜单项"
        
        # 生成变量声明
        variables_code = self._generate_variables()
        
        # 生成回调函数（声明和实现都在一起）
        callback_code = self._generate_callbacks()
        
        # 生成菜单创建函数
        menu_creation_code = self._generate_menu_creation()
        
        # 生成主菜单创建函数
        main_menu_code = self._generate_main_menu()
        
        # 组合所有代码
        code_parts = [
            "\n".join(self.includes),
            "",
            "// 生成的变量定义",
            variables_code,
            "",
            "// 回调函数",
            callback_code,
            "",
            "// 创建菜单项",
            menu_creation_code,
            "",
            main_menu_code,
            "",
            "// 获取主菜单项",
            "void* getMainItem(void) {",
            "    return Create_Main_Menu();",
            "}"
        ]
        
        return "\n".join(code_parts)

    def _collect_variables_from_items(self) -> Dict[str, Any]:
        """从菜单项中收集变量"""
        variables = {}
        
        def collect_from_item(item: MenuItemModel):
            # 为需要变量的菜单项类型收集变量
            if item.type in [MenuItemType.TOGGLE, MenuItemType.CHANGEABLE]:
                # 使用变量名称而不是显示名称
                var_name = getattr(item, 'variable_name', item.name)
                if item.type == MenuItemType.TOGGLE:
                    variables[var_name] = item.state
                elif item.type == MenuItemType.CHANGEABLE:
                    # 根据数据类型设置默认值
                    if item.data_type in [DataType.FLOAT, DataType.DOUBLE]:
                        variables[var_name] = 0.0
                    else:
                        variables[var_name] = 0
            
            # 递归处理子项
            for child in item.children:
                collect_from_item(child)
        
        if self.config.root_item:
            collect_from_item(self.config.root_item)
            
        return variables

    def _generate_variables(self) -> str:
        """生成变量声明代码"""
        # 从菜单项中收集变量
        variables = self._collect_variables_from_items()
        
        # 合并配置中已有的变量
        all_variables = {**self.config.variables, **variables}
        
        # 只有在确实有变量时才生成变量定义
        if not all_variables:
            return "// 无变量定义"
        
        lines = ["typedef struct {"]
        for var_name, var_value in all_variables.items():
            if isinstance(var_value, bool):
                lines.append(f"    bool {var_name};")
            elif isinstance(var_value, float):
                lines.append(f"    float {var_name};")
            elif isinstance(var_value, int):
                if -128 <= var_value <= 127:
                    lines.append(f"    int8_t {var_name};")
                elif -32768 <= var_value <= 32767:
                    lines.append(f"    int16_t {var_name};")
                else:
                    lines.append(f"    int32_t {var_name};")
        lines.append("} menu_variables_t;")
        lines.append("")
        
        # 初始化变量
        lines.append("static menu_variables_t g_menu_vars = {")
        for var_name, var_value in all_variables.items():
            if isinstance(var_value, bool):
                lines.append(f"    .{var_name} = {'true' if var_value else 'false'},")
            elif isinstance(var_value, (int, float)):
                if isinstance(var_value, float):
                    lines.append(f"    .{var_name} = {var_value}f,")
                else:
                    lines.append(f"    .{var_name} = {var_value},")
        lines.append("};")
        
        return "\n".join(lines)

    def _generate_callbacks(self) -> str:
        """生成回调函数（声明和实现在一起）"""
        lines = []
        
        # 收集所有需要的回调函数
        callbacks_needed = set()
        callback_types = {}  # 记录回调函数类型
        callback_items = {}  # 记录回调函数对应的菜单项
        if self.config.root_item:
            self._collect_callbacks_with_types(self.config.root_item, callbacks_needed, callback_types, callback_items)
        
        if not callbacks_needed:
            lines.append("// 无回调函数")
        else:
            for callback_name in sorted(callbacks_needed):
                callback_type = callback_types.get(callback_name, "void** args")
                item = callback_items.get(callback_name)
                
                if callback_type == "bool state":
                    lines.append(f"void {callback_name}(bool state) {{")
                    lines.append("    /* TODO: 实现切换回调函数 */")
                    lines.append("}")
                elif callback_type == "void* value":
                    lines.append(f"void {callback_name}(void* value) {{")
                    lines.append("    /* TODO: 实现实时变化回调函数 */")
                    lines.append("}")
                elif callback_type == "void** args":
                    lines.append(f"void {callback_name}(void** args) {{")
                    lines.append("    /* TODO: 实现应用回调函数 */")
                    lines.append("}")
                elif callback_type == "navigator_t* nav":
                    lines.append(f"void {callback_name}(navigator_t* nav) {{")
                    lines.append("    char buffer[MAX_DISPLAY_CHAR];")
                    lines.append("    /* TODO: 实现无分页展示回调函数 */")
                    lines.append("}")
                elif callback_type == "navigator_t* nav, uint8_t current_page, uint8_t total_pages":
                    lines.append(f"void {callback_name}(navigator_t* nav, uint8_t current_page, uint8_t total_pages) {{")
                    lines.append("    char buffer[MAX_DISPLAY_CHAR];")
                    
                    # 根据总页数生成相应的代码模板
                    if item and hasattr(item, 'total_pages'):
                        total_pages = item.total_pages
                    else:
                        total_pages = 1
                    
                    # 当页数为1时，生成无分页的代码模板
                    if total_pages == 1:
                        lines.append("    /* TODO: 实现无分页展示回调函数 */")
                    else:
                        # 当页数大于1时，生成带switch的代码模板
                        lines.append("    /* TODO: 实现分页展示回调函数 */")
                        lines.append("    switch(current_page)")
                        lines.append("    {")
                        
                        for i in range(total_pages):
                            lines.append(f"    case {i}:")
                            lines.append(f"        /* TODO: 实现第{i}页的显示内容 */")
                            lines.append("        break;")
                        lines.append("    }")
                    lines.append("}")
                else:
                    lines.append(f"void {callback_name}(void** args) {{")
                    lines.append("    /* TODO: 实现回调函数 */")
                    lines.append("}")
                lines.append("")
        
        return "\n".join(lines)

    def _collect_callbacks_with_types(self, item: MenuItemModel, callbacks: Set[str], callback_types: Dict[str, str], callback_items: Dict[str, MenuItemModel]):
        """收集所有需要的回调函数及其类型"""
        if item.type == MenuItemType.TOGGLE and item.enable_callback:
            # 使用新的回调函数命名规则
            var_name = getattr(item, 'variable_name', item.name)
            callback_name = f"{self._capitalize_name(var_name)}_Toggle_Callback"
            callbacks.add(callback_name)
            callback_types[callback_name] = "bool state"
            callback_items[callback_name] = item
        elif item.type == MenuItemType.CHANGEABLE and item.enable_callback:
            # 使用新的回调函数命名规则
            var_name = getattr(item, 'variable_name', item.name)
            callback_name = f"{self._capitalize_name(var_name)}_Change_Callback"
            callbacks.add(callback_name)
            callback_types[callback_name] = "void* value"
            callback_items[callback_name] = item
        elif item.type == MenuItemType.APPLICATION and item.enable_callback:
            # 使用新的回调函数命名规则
            callback_name = f"{self._capitalize_name(item.name)}_App_Callback"
            callbacks.add(callback_name)
            callback_types[callback_name] = "void** args"
            callback_items[callback_name] = item
        elif item.type == MenuItemType.EXHIBITION:
            # 展示菜单项默认开启回调函数
            # 使用新的回调函数命名规则，不再区分Page和Nav模式
            callback_name = f"{self._capitalize_name(item.name)}_Exhibition_Callback"
            callbacks.add(callback_name)
            # 根据页数决定回调函数签名
            if item.total_pages == 1:
                # Nav模式使用不带分页参数的回调函数签名
                callback_types[callback_name] = "navigator_t* nav"
            else:
                # Page模式使用带分页参数的回调函数签名
                callback_types[callback_name] = "navigator_t* nav, uint8_t current_page, uint8_t total_pages"
            callback_items[callback_name] = item
            
        # 递归处理子项
        for child in item.children:
            self._collect_callbacks_with_types(child, callbacks, callback_types, callback_items)

    def _generate_menu_creation(self) -> str:
        """生成菜单创建函数代码"""
        if not self.config.root_item:
            return "// 无菜单项"
            
        lines = []
        
        # 收集所有需要生成的菜单项（按依赖顺序）
        menu_items = self._collect_menu_items(self.config.root_item)
        
        # 创建一个字典来跟踪已使用的函数名，以确保唯一性
        used_function_names = {}
        # 创建一个字典来存储每个菜单项对应的函数名
        item_function_names = {}
        
        # 先为所有菜单项生成唯一的函数名
        for item in menu_items:
            func_name = self._get_unique_function_name(item, used_function_names)
            item_function_names[item] = func_name
        
        # 按正确的顺序生成菜单创建函数
        for item in menu_items:
            self._generate_single_menu_function(item, lines, item_function_names)
            
        return "\n".join(lines)

    def _collect_menu_items(self, root_item: MenuItemModel) -> List[MenuItemModel]:
        """收集所有菜单项并按依赖顺序排列"""
        items = []
        self._collect_items_recursive(root_item, items)
        return items

    def _collect_items_recursive(self, item: MenuItemModel, items: List[MenuItemModel]):
        """递归收集菜单项"""
        # 先收集子项
        for child in item.children:
            self._collect_items_recursive(child, items)
        
        # 再添加当前项（确保子项在父项之前）
        # 注意：不添加根菜单项，因为根菜单项由_generate_main_menu单独处理
        if item not in items and item != self.config.root_item:
            items.append(item)

    def _generate_main_menu(self) -> str:
        """生成主菜单创建函数"""
        if not self.config.root_item:
            return "// 无主菜单"
            
        lines = ["static menu_item_t* Create_Main_Menu(void) {"]
        
        if self.config.root_item.children:
            # 使用正确的数组声明和初始化方式
            lines.append(f"    static menu_item_t* main_children[{len(self.config.root_item.children)}];")
            lines.append("")
            
            # 逐个初始化数组元素
            for i, child in enumerate(self.config.root_item.children):
                # 使用函数名而不是简单的名称
                func_name = self._get_unique_function_name(child, {})  # 对于主菜单，我们重新计算
                lines.append(f"    main_children[{i}] = {func_name}();")
            lines.append("")
            
            lines.append(f"    return menu_create_normal_item(\"{self.config.root_item.name}\", main_children, {len(self.config.root_item.children)});")
        else:
            lines.append("    static menu_item_t** no_children = NULL;")
            lines.append(f"    return menu_create_normal_item(\"{self.config.root_item.name}\", no_children, 0);")
            
        lines.append("}")
        return "\n".join(lines)

    def _generate_single_menu_function(self, item: MenuItemModel, lines: List[str], item_function_names: dict):
        """生成单个菜单项的创建函数"""
        function_name = item_function_names[item]
        lines.append(f"static menu_item_t* {function_name}(void) {{")
        
        if item.type == MenuItemType.NORMAL:
            # 普通菜单项
            if item.children:
                # 使用函数名而不是简单的名称
                children_array_name = self._sanitize_name(item.name)
                # 使用正确的数组声明格式
                lines.append(f"    static menu_item_t* {children_array_name}_children[{len(item.children)}];")
                lines.append("")
                # 逐个初始化数组元素
                for i, child in enumerate(item.children):
                    # 使用已生成的函数名
                    child_func_name = item_function_names[child]
                    lines.append(f"    {children_array_name}_children[{i}] = {child_func_name}();")
                lines.append("")
                lines.append(f"    return menu_create_normal_item(\"{item.name}\", {children_array_name}_children, {len(item.children)});")
            else:
                lines.append(f"    static menu_item_t** no_children = NULL;")
                lines.append(f"    return menu_create_normal_item(\"{item.name}\", no_children, 0);")
        elif item.type == MenuItemType.TOGGLE:
            # 切换菜单项
            var_name = getattr(item, 'variable_name', item.name)
            var_ref = f"&g_menu_vars.{self._sanitize_name(var_name)}"
            # 使用新的回调函数命名规则
            callback_name = f"{self._capitalize_name(var_name)}_Toggle_Callback"
            # 检查是否启用了回调函数
            if item.enable_callback:
                lines.append(f"    return menu_create_toggle_item(\"{item.name}\", {var_ref}, {callback_name});")
            else:
                lines.append(f"    return menu_create_toggle_item(\"{item.name}\", {var_ref}, NULL);")
        elif item.type == MenuItemType.CHANGEABLE:
            # 可变菜单项
            var_name = getattr(item, 'variable_name', item.name)
            var_ref = f"&g_menu_vars.{self._sanitize_name(var_name)}"
            data_type = self._map_data_type(item.data_type)
            # 使用新的回调函数命名规则
            callback_name = f"{self._capitalize_name(var_name)}_Change_Callback"
            
            # 初始化最小值、最大值和步长变量
            lines.append(f"    static {self._get_c_type(item.data_type)} {var_name}_min_val = {item.min_val or 0.0}f;")
            lines.append(f"    static {self._get_c_type(item.data_type)} {var_name}_max_val = {item.max_val or 100.0}f;")
            lines.append(f"    static {self._get_c_type(item.data_type)} {var_name}_step_val = {item.step_val or 1.0}f;")
            
            # 添加菜单创建
            if item.enable_callback:
                lines.append(f"    return menu_create_changeable_item(\"{item.name}\", {var_ref}, &{var_name}_min_val, &{var_name}_max_val, &{var_name}_step_val, {data_type}, {callback_name});")
            else:
                lines.append(f"    return menu_create_changeable_item(\"{item.name}\", {var_ref}, &{var_name}_min_val, &{var_name}_max_val, &{var_name}_step_val, {data_type}, NULL);")
        elif item.type == MenuItemType.APPLICATION:
            # 应用菜单项
            # 使用新的回调函数命名规则
            callback_name = f"{self._capitalize_name(item.name)}_App_Callback"
            # 检查是否启用了回调函数
            if item.enable_callback:  # 应用菜单项默认开启回调函数
                lines.append(f"    return menu_create_app_item(\"{item.name}\", NULL, {callback_name});")
            else:
                lines.append(f"    return menu_create_app_item(\"{item.name}\", NULL, NULL);")
        elif item.type == MenuItemType.EXHIBITION:
            # 展示菜单项
            # 使用新的回调函数命名规则，不再区分Page和Nav模式
            callback_name = f"{self._capitalize_name(item.name)}_Exhibition_Callback"
            # 检查是否启用了回调函数
            if item.enable_callback:  # 展示菜单项默认开启回调函数
                # 使用统一的menu_create_exhibition_item函数
                lines.append(f"    return menu_create_exhibition_item(\"{item.name}\", {item.total_pages}, {callback_name});")
            else:
                # 使用统一的menu_create_exhibition_item函数
                lines.append(f"    return menu_create_exhibition_item(\"{item.name}\", {item.total_pages}, NULL);")
        
        lines.append("}")
        lines.append("")

    def _get_capitalized_function_name_base(self, item: MenuItemModel) -> str:
        """获取基础的首字母大写的菜单项函数名（不带唯一性后缀）"""
        # 对于切换和可变菜单项，使用变量名称
        if item.type in [MenuItemType.TOGGLE, MenuItemType.CHANGEABLE]:
            var_name = getattr(item, 'variable_name', item.name)
            capitalized_name = self._capitalize_name(var_name)
        else:
            # 对于其他类型，使用显示名称
            capitalized_name = self._capitalize_name(item.name)
        
        return f"Create_{capitalized_name}_Menu"

    def _get_unique_function_name(self, item: MenuItemModel, used_function_names: dict) -> str:
        """获取唯一的菜单项函数名"""
        base_name = self._get_capitalized_function_name_base(item)
        
        # 如果这个基础名还没有被使用，直接返回
        if base_name not in used_function_names:
            used_function_names[base_name] = 1
            return base_name
        
        # 如果已被使用，添加数字后缀
        counter = used_function_names[base_name]
        unique_name = f"{base_name}_{counter}"
        
        # 更新计数器
        used_function_names[base_name] = counter + 1
        
        return unique_name

    def _get_capitalized_function_name(self, item: MenuItemModel) -> str:
        """获取首字母大写的菜单项函数名（为了向后兼容保留此方法）"""
        # 对于切换和可变菜单项，使用变量名称
        if item.type in [MenuItemType.TOGGLE, MenuItemType.CHANGEABLE]:
            var_name = getattr(item, 'variable_name', item.name)
            capitalized_name = self._capitalize_name(var_name)
        else:
            # 对于其他类型，使用显示名称
            capitalized_name = self._capitalize_name(item.name)
        
        return f"Create_{capitalized_name}_Menu"

    def _sanitize_name(self, name: str) -> str:
        """清理名称，使其符合C语言标识符规范"""
        # 移除特殊字符，替换为下划线
        sanitized = "".join(c if c.isalnum() else "_" for c in name)
        # 确保不以数字开头
        if sanitized and sanitized[0].isdigit():
            sanitized = "_" + sanitized
        return sanitized if sanitized else "item"

    def _get_function_name(self, item: MenuItemModel) -> str:
        """获取菜单项的函数名"""
        # 使用显示名称作为函数名前缀
        name_prefix = self._sanitize_name(item.name)
        return name_prefix

    def _map_data_type(self, data_type: DataType) -> str:
        """映射数据类型到C枚举"""
        mapping = {
            DataType.UINT8: "DATA_TYPE_UINT8",
            DataType.UINT16: "DATA_TYPE_UINT16",
            DataType.UINT32: "DATA_TYPE_UINT32",
            DataType.UINT64: "DATA_TYPE_UINT64",
            DataType.INT8: "DATA_TYPE_INT8",
            DataType.INT16: "DATA_TYPE_INT16",
            DataType.INT32: "DATA_TYPE_INT32",
            DataType.INT64: "DATA_TYPE_INT64",
            DataType.FLOAT: "DATA_TYPE_FLOAT",
            DataType.DOUBLE: "DATA_TYPE_DOUBLE"
        }
        return mapping.get(data_type, "DATA_TYPE_FLOAT")

    def _get_c_type(self, data_type: DataType) -> str:
        """获取数据类型对应的C类型"""
        mapping = {
            DataType.UINT8: "uint8_t",
            DataType.UINT16: "uint16_t",
            DataType.UINT32: "uint32_t",
            DataType.UINT64: "uint64_t",
            DataType.INT8: "int8_t",
            DataType.INT16: "int16_t",
            DataType.INT32: "int32_t",
            DataType.INT64: "int64_t",
            DataType.FLOAT: "float",
            DataType.DOUBLE: "double"
        }
        return mapping.get(data_type, "float")

    def _capitalize_name(self, name: str) -> str:
        """将名称转换为首字母大写的格式"""
        # 清理名称并转换为首字母大写
        sanitized = self._sanitize_name(name)
        # 将下划线分隔的单词首字母大写
        words = sanitized.split('_')
        capitalized_words = [word.capitalize() if word else word for word in words]
        return '_'.join(capitalized_words)
