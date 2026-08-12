def parse_page_ranges(expr, total_pages):
    if total_pages < 1:
        raise ValueError('总页数必须为正整数')

    expr = expr.strip()
    if not expr:
        return []

    plus_mode = False
    if expr.startswith('+'):
        plus_mode = True
        expr = expr[1:].lstrip()
    elif '+' in expr:
        raise ValueError("增强模式的 '+' 只能出现在表达式最前端")

    groups = expr.split(';')
    result = []

    for group_str in groups:
        group_str = group_str.strip()
        if not group_str:
            continue

        atoms = group_str.split(',')
        pages_1based = []
        for atom_str in atoms:
            atom_str = atom_str.strip()
            if not atom_str:
                continue
            pages_1based.extend(_parse_atom(atom_str, total_pages, plus_mode))

        if not pages_1based:
            continue

        if not plus_mode:
            pages_1based = sorted(set(pages_1based))

        full_range = list(range(1, total_pages + 1))
        if pages_1based == full_range:
            raise ValueError('所选页面与原始文件完全相同，请检查范围表达式')

        pages_0based = [p - 1 for p in pages_1based]
        result.append(pages_0based)

    return result


def _parse_atom(atom_str, total_pages, plus_mode):
    try:
        if ':' in atom_str:
            range_part, step_str = atom_str.split(':', 1)
            try:
                step = int(step_str)
            except ValueError:
                raise ValueError(f"步长必须为整数: '{step_str}'") from None
            if step <= 0:
                raise ValueError(f'步长必须为正整数: {step}') from None
            start, end = _parse_range(range_part.strip(), total_pages, plus_mode)
            return _generate_range(start, end, step, plus_mode)
        else:
            if '-' in atom_str:
                start, end = _parse_range(atom_str.strip(), total_pages, plus_mode)
                return _generate_range(start, end, 1, plus_mode)
            else:
                try:
                    page = int(atom_str)
                except ValueError:
                    raise ValueError(f"无效页码: '{atom_str}'") from None
                if page < 1 or page > total_pages:
                    raise ValueError(f'页码超出范围: {page}') from None
                return [page]
    except ValueError as e:
        raise ValueError(f"原子 '{atom_str}' 解析错误: {e}") from e


def _parse_range(range_str, total_pages, plus_mode):
    if range_str == '-' or range_str == '':
        return 1, total_pages

    try:
        if range_str.startswith('-'):
            try:
                end = int(range_str[1:])
            except ValueError:
                raise ValueError(f"无效结束页码: '{range_str[1:]}'") from None
            if end < 1 or end > total_pages:
                raise ValueError(f'结束页码超出范围: {end}')
            return 1, end

        if range_str.endswith('-'):
            try:
                start = int(range_str[:-1])
            except ValueError:
                raise ValueError(f"无效起始页码: '{range_str[:-1]}'") from None
            if start < 1 or start > total_pages:
                raise ValueError(f'起始页码超出范围: {start}')
            return start, total_pages

        parts = range_str.split('-')
        if len(parts) != 2:
            raise ValueError(f"无效范围格式: '{range_str}'")
        try:
            start = int(parts[0])
        except ValueError:
            raise ValueError(f"无效起始页码: '{parts[0]}'") from None
        try:
            end = int(parts[1])
        except ValueError:
            raise ValueError(f"无效结束页码: '{parts[1]}'") from None
        if start < 1 or start > total_pages:
            raise ValueError(f'起始页码超出范围: {start}')
        if end < 1 or end > total_pages:
            raise ValueError(f'结束页码超出范围: {end}')

        if not plus_mode and start > end:
            raise ValueError(f'默认模式下不允许反向范围: {start}-{end}')

        return start, end
    except ValueError as e:
        raise ValueError(f"范围 '{range_str}' 解析错误: {e}") from e


def _generate_range(start, end, step, plus_mode):
    if start <= end:
        pages = []
        cur = start
        while cur <= end:
            pages.append(cur)
            cur += step
        return pages
    else:
        if not plus_mode:
            raise ValueError('默认模式不支持反向范围')
        pages = []
        cur = start
        while cur >= end:
            pages.append(cur)
            cur -= step
        return pages


if __name__ == '__main__':
    total = 10

    print(parse_page_ranges('1,3,5', total))
    try:
        parse_page_ranges('-', total)
    except ValueError as e:
        print(e)

    try:
        parse_page_ranges('+1-10', total)
    except ValueError as e:
        print(e)

    print(parse_page_ranges('+1-10,5', total))
