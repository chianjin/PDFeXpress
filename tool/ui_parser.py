import xml.etree.ElementTree as ET


def ui_parser(ui_file):
    xml = ET.parse(ui_file)
    root = xml.getroot()
    root_widget = root[0]
    code = f'class {root_widget.attrib.get("id")}({root_widget.attrib.get("class")}):\n' \
           f'    def __init__(self, master=None, **kw):\n'\
           f'        super({root_widget.attrib.get("class")}, self).__init__(master=master, **kw)'
    get_children(root)
    print(code)


def get_children(node):
    code = ''
    master = None
    for child in node:
        print(child.tag, child.attrib, f'"{child.text.strip() if child.text else None }"')
        get_children(child)


if __name__ == '__main__':
    ui_file = '../ui/UiAbout.ui'
    ui_parser(ui_file)
