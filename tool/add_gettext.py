def add_translater(ui_file):
    code_lines = []
    with open(ui_file) as ui:
        for line in ui.readlines():
            if line.startswith('import pathlib') or line.startswith('PROJECT'):
                continue
            if line.startswith('if __name__'):
                break
            if line.find("text='") != -1:
                start = line.find("text='")
                stop = line.find("'", start + 6)
                pre_line = line[:start + 5]
                suf_line = line[stop + 1:]
                text = line[start + 5:stop + 1]
                line = f'{pre_line}_({text}){suf_line}'
            code_lines.append(line)
    code = ''.join(code_lines)
    while code.find('\n\n\n\n') != -1:
        code = code.replace('\n\n\n\n', '\n\n\n')

    with open(ui_file, 'w') as ui:
        ui.write(code)


if __name__ == '__main__':
    import glob

    file_list = glob.glob('../src/ui/*.py')
    for file in file_list:
        add_translater(file)
