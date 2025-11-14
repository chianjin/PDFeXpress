from pathlib import Path


def generate_extension_set(*file_types_args, with_star=False):
    extensions = []
    for file_types in file_types_args:
        for type_name, extension in file_types:
            if isinstance(extension, str):
                extensions.append(extension)
            else:
                extensions.extend(extension)
        if not with_star:
            extensions = [ext.replace("*", "") for ext in extensions]
    return set(extensions)


def get_files_with_extensions(file_list, *file_types_args):
    extensions = generate_extension_set(*file_types_args)
    return [file for file in file_list if Path(file).suffix.lower() in extensions]


def get_folder_files_with_extensions(folder_path, *file_types_args):
    folder_path = Path(folder_path)
    file_list = []
    for extension in generate_extension_set(*file_types_args, with_star=True):
        file_list.extend(folder_path.glob(extension))
    return file_list
