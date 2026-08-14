# util/file_types/file_types_registry.py

# 使用相对导入，使得 utils 包内部解耦，完全独立
from util.file_types import file_types_data as data_module


class RegistryDict(dict):
    """支持多键索引与批量派生注册的高级字典引擎"""

    def __getitem__(self, keys: str | tuple[str]):
        if isinstance(keys, tuple):
            result = []
            for key in keys:
                result.extend(super().__getitem__(key))
            return result
        return super().__getitem__(keys)

    def register_group(self, group_prefix: str, unified_desc: str, types_dict: dict):
        """统一注册一整组文件类型并自动派生"""
        all_extensions = []
        for key, value in types_dict.items():
            self[key] = [value]
            extension = value[1]
            if isinstance(extension, tuple):
                all_extensions.extend(extension)
            else:
                all_extensions.append(extension)

        unified_item = (unified_desc, tuple(all_extensions))
        self[f'{group_prefix}S'] = [unified_item]
        self[f'{group_prefix}_LIST'] = [
            unified_item,
            *list(types_dict.values()),
        ]


# ==========================================
# 自动化装载流程
# ==========================================

# 1. 加载底层基础类型
FILE_TYPES = RegistryDict(data_module.BASE_FILETYPES)

# 2. 自动装载所有的 _GROUP
for var_name, var_value in vars(data_module).items():
    if (
        var_name.isupper()
        and var_name.endswith('_GROUP')
        and isinstance(var_value, tuple)
        and len(var_value) == 3
    ):
        FILE_TYPES.register_group(*var_value)
