from collections import namedtuple

PageLabel = namedtuple('PageLabel', ['display', 'type'])

# 罗马数字转换表
_ROMAN_VALUES = [
    (1000, 'M'),
    (900, 'CM'),
    (500, 'D'),
    (400, 'CD'),
    (100, 'C'),
    (90, 'XC'),
    (50, 'L'),
    (40, 'XL'),
    (10, 'X'),
    (9, 'IX'),
    (5, 'V'),
    (4, 'IV'),
    (1, 'I'),
]
_LOWER_ROMAN = [(v, s.lower()) for v, s in _ROMAN_VALUES]


def _to_roman(num, lower=False):
    if num < 1:
        raise ValueError(f'罗马数字起始值必须 >= 1，当前为 {num}')
    table = _LOWER_ROMAN if lower else _ROMAN_VALUES
    result = []
    for value, symbol in table:
        while num >= value:
            result.append(symbol)
            num -= value
    return ''.join(result)


def _to_alpha(num, upper=True):
    if num < 1:
        raise ValueError(f'字母起始值必须 >= 1，当前为 {num}')
    result = []
    n = num
    while n > 0:
        n -= 1
        result.append(chr((n % 26) + (ord('A') if upper else ord('a'))))
        n //= 26
    return ''.join(reversed(result))


# 类型到生成函数的映射
_LABEL_MAKERS = {
    'n': lambda v: PageLabel(str(v), 'n'),
    'r': lambda v: PageLabel(_to_roman(v, lower=True), 'r'),
    'R': lambda v: PageLabel(_to_roman(v, lower=False), 'R'),
    'a': lambda v: PageLabel(_to_alpha(v, upper=False), 'a'),
    'A': lambda v: PageLabel(_to_alpha(v, upper=True), 'A'),
}


def _parse_phys_range(phys_part, total_pages):
    if phys_part == '':
        return 1, total_pages

    if '-' not in phys_part:
        p = int(phys_part)
        return p, p

    left, right = phys_part.split('-', 1)
    start = int(left) if left else 1
    end = int(right) if right else total_pages
    return start, end


def _parse_display_format(fmt_part, last_end_value):
    if fmt_part == '':
        return 'n', 1

    first_char = fmt_part[0]

    # 纯数字简写
    if first_char.isdigit():
        return 'n', int(fmt_part)

    # 类型字母
    fmt_type = first_char.upper() if first_char in 'N' else first_char
    if fmt_type not in _LABEL_MAKERS:
        raise ValueError(f"未定义的类型标识符 '{first_char}'")

    val_str = fmt_part[1:].strip()
    if val_str:
        return fmt_type, int(val_str)
    else:
        start_value = last_end_value + 1 if last_end_value is not None else 1
        return fmt_type, start_value


def parse_page_labels(expr, total_pages):
    if total_pages < 1:
        raise ValueError('总页数必须为正整数')

    expr = expr.strip()
    result = [None] * total_pages

    if not expr:
        for i in range(total_pages):
            result[i] = PageLabel(str(i + 1), 'n')
        return result

    segments = expr.split(',')
    last_end_value = None

    for seg_str in segments:
        seg_str = seg_str.strip()
        if not seg_str:
            continue

        if ':' not in seg_str:
            raise ValueError(f"缺少冒号分隔符: '{seg_str}'")

        phys_part, fmt_part = seg_str.split(':', 1)
        phys_part = phys_part.strip()
        fmt_part = fmt_part.strip()

        start_page, end_page = _parse_phys_range(phys_part, total_pages)

        if start_page < 1 or start_page > total_pages:
            raise ValueError(f'物理起始页超出范围: {start_page}')
        if end_page < 1 or end_page > total_pages:
            raise ValueError(f'物理结束页超出范围: {end_page}')
        if start_page > end_page:
            raise ValueError(f'物理起始页不能大于结束页: {start_page}-{end_page}')

        fmt_type, start_value = _parse_display_format(fmt_part, last_end_value)

        if start_value < 1:
            raise ValueError(f'起始值必须 >= 1: {start_value}')

        make_label = _LABEL_MAKERS[fmt_type]
        current_value = start_value
        for page in range(start_page, end_page + 1):
            result[page - 1] = make_label(current_value)
            current_value += 1

        last_end_value = current_value - 1

    return result


# ========= 测试 =========
if __name__ == '__main__':

    def show(result):
        for i, item in enumerate(result):
            if item is None:
                print(f'  [{i:2d}] None')
            else:
                print(f'  [{i:2d}] {item.display:>4s} ({item.type})')
        print()

    print('示例 A: 1-5:R,10-15:')
    show(parse_page_labels('1-5:R,10-15:', 15))

    print('示例 B: 1-5:R,6-10:r')
    show(parse_page_labels('1-5:R,6-10:r', 15))

    print('示例 C: :n1,1-3:')
    show(parse_page_labels(':n1,1-3:', 10))

    print('示例 D: 1-5:p1')
    try:
        parse_page_labels('1-5:p1', 15)
    except ValueError as e:
        print(f'  错误: {e}')
