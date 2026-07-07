#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_page_parser.py - Markdown 特殊语法解析器

职责：解析 Markdown 文本中的各种特殊语法块，返回结构化 content 字典。
支持两种数据提供方式：
1. JSON 文件引用（适合大量数据）：![type](data/xxx.json)
2. Markdown Code 块（适合少量人工编写数据）：```type\n{json}\```

支持的语法块：
  - ![stats](data/xxx.json) 或 ```stats\n[...]\n``` -> content.stats
  - ![cards](data/xxx.json) 或 ```cards\n[...]\n``` -> content.cards
  - ![timeline](data/xxx.json) 或 ```timeline\n{...}\n``` -> content.timeline
  - ![branches](data/xxx.json) 或 ```branches\n{...}\n``` -> content.branchVisualizer
  - ![chips](data/xxx.json) 或 ```chips\n[...]\n``` -> content.chips
  - Markdown 表格  -> content.tables
  - ![bar|pie|line|china-map](data/xxx.json) 或 ```bar|pie|line|china-map\n{...}\n``` -> content.charts
  - 图片 ![desc](img/xxx.jpg) -> content.images (保留在 description 中)
  - 加粗 **text**、斜体 *text* 等 -> 保留在 description 中，前端渲染
  - 列表块 (- item 或 1. item) -> content.list
  - 分栏 ===== / -----  -> content.columns

对外接口：
  parse_markdown_blocks(text: str, dir_path: str = '') -> dict
"""

import os
import re
import json


# 分栏标记，严格 5 个字符
COLUMN_START_MARKER = '====='
COLUMN_SPLIT_MARKER = '-----'


def parse_markdown_blocks(text: str, dir_path: str = '') -> dict:
    """
    解析 Markdown 文本中的特殊语法块，返回结构化 content 字典。
    普通文本段落保留在 description 中。
    支持分栏（===== / -----）的解析。
    """
    content = {
        'description': [],
        'stats': [],
        'tables': [],
        'cards': [],
        'charts': [],
        'list': None,
        'chips': [],
        'branchVisualizer': None,
        'timeline': None,
        'columns': [],
        'blocks': [],
    }

    lines = text.split('\n')
    i = 0
    current_para_lines = []
    current_column = None
    in_column_block = False

    def _flush_para():
        """将当前累积的普通文本段落写入 description 或当前分栏"""
        if not current_para_lines:
            return
        para = '\n'.join(current_para_lines).strip()
        if not para:
            current_para_lines.clear()
            return
        if current_column is not None:
            current_column['items'].append(para)
        else:
            content['description'].append(para)
            content['blocks'].append({'type': 'description', 'data': [para]})
        current_para_lines.clear()

    def _is_column_empty(col: dict) -> bool:
        """检查分栏是否为空（没有文本、表格、列表、卡片）"""
        return not col['items'] and not col['tables'] and col['list'] is None and not col['cards']

    def _clean_column(col: dict) -> dict:
        """清理分栏字典，移除空字段"""
        result = {}
        if col.get('items'):
            result['items'] = col['items']
        if col.get('tables'):
            result['tables'] = col['tables']
        if col.get('list'):
            result['list'] = col['list']
        if col.get('cards'):
            result['cards'] = col['cards']
        return result

    def _flush_column():
        """保存当前分栏"""
        nonlocal current_column
        if current_column is None:
            return
        _flush_para()
        if not _is_column_empty(current_column):
            content['columns'].append(_clean_column(current_column))
        current_column = None

    def _flush_columns():
        """结束分栏区域，保存当前分栏并清空状态"""
        nonlocal in_column_block
        _flush_column()
        in_column_block = False

    def _start_column():
        """开始一个新的分栏"""
        nonlocal current_column, in_column_block
        _flush_para()
        if current_column is not None:
            if not _is_column_empty(current_column):
                content['columns'].append(_clean_column(current_column))
        current_column = {'items': [], 'tables': [], 'list': None, 'cards': []}
        in_column_block = True

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 0. 分栏标记：===== 开始/结束分栏区域，----- 分隔分栏
        if stripped == COLUMN_START_MARKER:
            if in_column_block:
                # 结束分栏区域
                _flush_columns()
            else:
                # 开始分栏区域
                _start_column()
            i += 1
            continue

        if stripped == COLUMN_SPLIT_MARKER:
            if in_column_block:
                # 当前分栏结束，下一个分栏开始
                _flush_column()
                current_column = {'items': [], 'tables': [], 'list': None, 'cards': []}
            else:
                # 不在分栏区域内时，忽略孤立的分隔符
                pass
            i += 1
            continue

        # 1. Markdown Code 块 (```type) - 支持 stats/cards/timeline/branches/chips/bar/pie/line/china-map
        code_block_match = re.match(r'^```(\w+(-\w+)?)\s*$', stripped)
        if code_block_match:
            code_type = code_block_match.group(1)
            supported_types = {'stats', 'cards', 'timeline', 'branches', 'chips', 'bar', 'pie', 'line', 'china-map', 'chinaMap', 'charts'}
            _flush_para()
            code_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() != '```':
                code_lines.append(lines[i])
                i += 1
            code_content = '\n'.join(code_lines)
            if code_type in supported_types:
                # 尝试解析为结构化数据
                code_content_stripped = code_content.strip()
                if code_content_stripped:
                    try:
                        json_data = json.loads(code_content_stripped)
                        if code_type == 'charts':
                            # charts 块内嵌了 type 字段，用其作为实际图表类型
                            inner_type = json_data.get('type', 'bar')
                            _assign_json_data(json_data, inner_type, content, current_column)
                        else:
                            _assign_json_data(json_data, code_type, content, current_column)
                    except json.JSONDecodeError:
                        # JSON 解析失败，作为普通代码块保留在 description 中
                        code_text = f'```{code_type}\n{code_content}\n```'
                        if current_column is not None:
                            current_column['items'].append(code_text)
                        else:
                            content['description'].append(code_text)
                            content['blocks'].append({'type': 'description', 'data': [code_text]})
            else:
                # 普通代码块，直接保留在 description 中
                code_text = f'```{code_type}\n{code_content}\n```'
                if current_column is not None:
                    current_column['items'].append(code_text)
                else:
                    content['description'].append(code_text)
                    content['blocks'].append({'type': 'description', 'data': [code_text]})
            i += 1
            continue

        # 1.5 围栏语法块 (::: type) - 支持 stats/cards/timeline/branches/chips
        fence_block_match = re.match(r'^:::\s*(\w+)\s*$', stripped)
        if fence_block_match:
            fence_type = fence_block_match.group(1)
            supported_fence_types = {'stats', 'cards', 'timeline', 'branches', 'chips'}
            if fence_type in supported_fence_types:
                _flush_para()
                fence_lines = []
                i += 1
                while i < len(lines) and not re.match(r'^:::\s*$', lines[i].strip()):
                    fence_lines.append(lines[i])
                    i += 1
                if fence_type == 'stats':
                    stats_items = _parse_stats_block(fence_lines)
                    for item in stats_items:
                        _append_to_field('stats', item, content, current_column)
                    _append_to_blocks('stats', stats_items, content, current_column)
                elif fence_type == 'cards':
                    card_items = _parse_cards_block(fence_lines)
                    target = _get_target(content, current_column)
                    if 'cards' not in target:
                        target['cards'] = []
                    target['cards'].append(card_items)
                    _append_to_blocks('cards', card_items, content, current_column)
                elif fence_type == 'timeline':
                    timeline_data = _parse_timeline_block(fence_lines)
                    if timeline_data:
                        target = _get_target(content, current_column)
                        if not target.get('timeline'):
                            target['timeline'] = []
                        target['timeline'].append(timeline_data)
                        _append_to_blocks('timeline', timeline_data, content, current_column)
                elif fence_type == 'branches':
                    branches_data = _parse_branches_block(fence_lines)
                    if branches_data:
                        target = _get_target(content, current_column)
                        if not target.get('branchVisualizer'):
                            target['branchVisualizer'] = []
                        target['branchVisualizer'].append(branches_data)
                        _append_to_blocks('branchVisualizer', branches_data, content, current_column)
                elif fence_type == 'chips':
                    chip_items = _parse_chips_block(fence_lines)
                    for item in chip_items:
                        _append_to_field('chips', item, content, current_column)
                    _append_to_blocks('chips', chip_items, content, current_column)
                i += 1
                continue

        # 2. Markdown 表格 (| header | header |)
        if stripped.startswith('|') and stripped.endswith('|') and '|' in stripped[1:-1]:
            _flush_para()
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            table = _parse_markdown_table(table_lines)
            if table:
                if current_column is not None:
                    current_column['tables'].append(table)
                else:
                    content['tables'].append(table)
                    content['blocks'].append({'type': 'tables', 'data': table})
            continue

        # 3. 图表/组件 JSON 引用 ![type](data/xxx.json) 或 ![type](data/xxx) 或 ![type](xxx)
        # 支持的类型：bar, pie, line, china-map, stats, cards, timeline, branches, chips
        # type 必须是纯英文字母（中文 alt 会被图片规则处理）
        # image 类型由专门的图片规则处理
        json_ref_match = re.match(r'^!\[([a-zA-Z-]+)\]\((data/)?([^)]+)\)$', stripped)
        if json_ref_match:
            ref_type = json_ref_match.group(1)
            if ref_type != 'image':
                _flush_para()
                data_file = json_ref_match.group(3)
                # 自动补全 .json 后缀
                if not data_file.endswith('.json'):
                    data_file += '.json'
                json_data = _load_json_data(dir_path, data_file, ref_type)
                if json_data:
                    _assign_json_data(json_data, ref_type, content, current_column)
                i += 1
                continue

        # 3.5 图片引用 ![image](image/xxx.jpg) 或 ![image](xxx.jpg)
        image_match = re.match(r'^!\[image\]\(([^)]+)\)$', stripped)
        if image_match:
            _flush_para()
            image_src = image_match.group(1)
            image_text = f'![image]({image_src})'
            if current_column is not None:
                current_column['items'].append(image_text)
            else:
                content['description'].append(image_text)
                content['blocks'].append({'type': 'description', 'data': [image_text]})
            i += 1
            continue

        # 8. 列表块 (- item 或 1. item) - 只有包含 | 分隔符的才解析为 list 类型
        if re.match(r'^(-\s|\d+\.\s)', stripped):
            _flush_para()
            list_lines = []
            while i < len(lines) and (lines[i].strip().startswith('- ') or re.match(r'^\d+\.\s', lines[i].strip())):
                list_lines.append(lines[i])
                i += 1
            # 检查是否包含 | 分隔符，只有包含 | 的才解析为 list 类型
            has_pipe = any('|' in line for line in list_lines)
            if has_pipe:
                list_block = _parse_list_block(list_lines)
                if list_block:
                    if current_column is not None:
                        if current_column['list'] is None:
                            current_column['list'] = list_block
                        else:
                            current_column['list']['items'].extend(list_block['items'])
                    else:
                        content['list'] = list_block
                        content['blocks'].append({'type': 'list', 'data': list_block})
            else:
                # 普通列表，保留在 description 中（作为一个整体）
                list_text = '\n'.join(list_lines)
                if current_column is not None:
                    current_column['items'].append(list_text)
                else:
                    content['description'].append(list_text)
                    content['blocks'].append({'type': 'description', 'data': [list_text]})
            continue

        # 9. 二级标题 (## heading) -> description 内 h3
        if stripped.startswith('## '):
            _flush_para()
            heading_text = stripped[3:].strip()
            if current_column is not None:
                current_column['items'].append(f'## {heading_text}')
            else:
                content['description'].append(f'## {heading_text}')
                content['blocks'].append({'type': 'description', 'data': [f'## {heading_text}']})
            i += 1
            continue

        # 10. 三级标题 (### heading) -> description 内 h4
        if stripped.startswith('### '):
            _flush_para()
            heading_text = stripped[4:].strip()
            if current_column is not None:
                current_column['items'].append(f'### {heading_text}')
            else:
                content['description'].append(f'### {heading_text}')
                content['blocks'].append({'type': 'description', 'data': [f'### {heading_text}']})
            i += 1
            continue

        # 11. 四级标题 (#### heading) -> description 内 h4（小一级）
        if stripped.startswith('#### '):
            _flush_para()
            heading_text = stripped[5:].strip()
            if current_column is not None:
                current_column['items'].append(f'#### {heading_text}')
            else:
                content['description'].append(f'#### {heading_text}')
                content['blocks'].append({'type': 'description', 'data': [f'#### {heading_text}']})
            i += 1
            continue

        # 12. 投票语法 [vote:xxx] - 直接忽略
        if re.match(r'^\[vote:[^\]]+\]$', stripped):
            i += 1
            continue

        # 13. 普通文本行
        current_para_lines.append(line)
        i += 1

    _flush_para()
    _flush_columns()

    # 移除空字段
    result = {}
    for key, value in content.items():
        if value:
            result[key] = value
    return result


def _parse_stats_block(lines: list) -> list:
    """解析 ::: stats 块，返回 StatItem 列表"""
    items = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 格式: 数值 | 标签
        parts = line.split('|')
        if len(parts) >= 2:
            value = parts[0].strip()
            label = parts[1].strip()
            items.append({'value': value, 'label': label})
    return items


def _parse_cards_block(lines: list) -> list:
    """解析 ::: cards 块，返回 CardItem 列表"""
    items = []
    for line in lines:
        line = line.strip()
        if not line or not line.startswith('- '):
            continue
        # 格式: - 标题 | 副标题 | 详情1, 详情2, 详情3
        content = line[2:].strip()
        parts = content.split('|')
        if len(parts) >= 2:
            headline = parts[0].strip()
            supporting = parts[1].strip()
            detail = []
            if len(parts) >= 3:
                detail = [d.strip() for d in parts[2].split(',') if d.strip()]
            items.append({
                'headline': headline,
                'supporting': supporting,
                'detail': detail,
            })
    return items


def _parse_timeline_block(lines: list) -> dict:
    """解析 ::: timeline 块，返回 TimelineBlock 字典"""
    items = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 支持两种格式：
        # 1. 带 - 前缀：- 日期 | 标题 | 副标题 | 描述
        # 2. 纯文本行：日期 | 标题 | 副标题 | 描述
        if line.startswith('- '):
            content = line[2:].strip()
        else:
            content = line
        parts = content.split('|')
        if len(parts) >= 2:
            date = parts[0].strip()
            title = parts[1].strip()
            subtitle = parts[2].strip() if len(parts) > 2 else ''
            description = []
            if len(parts) > 3:
                description = [parts[3].strip()]
            items.append({
                'date': date,
                'title': title,
                'subtitle': subtitle,
                'description': description,
            })
    return {'title': '', 'items': items} if items else None


def _parse_branches_block(lines: list) -> dict:
    """解析 ::: branches 块，返回 BranchVisualizer 字典"""
    branches = []
    periods = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 第一行可能是时期定义（无 - 前缀）：古代 | 近代 | 现代 | 当代
        # 后续行是分支数据（带 - 前缀）：- 分支名称 | 等级1,等级2 | 描述1;描述2
        if line.startswith('- '):
            content = line[2:].strip()
        else:
            content = line
        parts = content.split('|')
        if len(parts) >= 2:
            # 检查是否是时期定义行（所有部分都是纯文本，没有数字）
            first_part = parts[0].strip()
            second_part = parts[1].strip()
            # 如果第二个部分不是数字（或数字列表），则认为是时期定义
            if not second_part.replace(',', '').replace(' ', '').isdigit():
                # 这是时期定义行
                if not periods:
                    periods = [p.strip() for p in parts]
                continue
            # 否则是分支数据
            name = first_part
            levels = [int(l.strip()) for l in second_part.split(',') if l.strip().isdigit()]
            descriptions = []
            if len(parts) >= 3:
                descriptions = [d.strip() for d in parts[2].split(';') if d.strip()]
            branches.append({
                'name': name,
                'levels': levels,
                'descriptions': descriptions,
            })
    if not branches:
        return None
    # 如果没有定义时期，从第一个分支推断
    if not periods:
        periods_count = len(branches[0]['levels']) if branches else 0
        periods = ['时期 ' + str(i + 1) for i in range(periods_count)]
    return {'periods': periods, 'branches': branches}


def _parse_chips_block(lines: list) -> list:
    """解析 ::: chips 块，返回 ChipItem 列表"""
    items = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 支持两种格式：
        # 1. 带 - 前缀：- 标签名
        # 2. 纯文本行：标签名
        if line.startswith('- '):
            label = line[2:].strip()
        else:
            label = line
        if label:
            items.append({'label': label, 'accent': False})
    return items


def _parse_markdown_table(lines: list) -> dict:
    """解析 Markdown 表格语法，返回 TableItem 字典"""
    if not lines:
        return None

    # 过滤分隔行 (|---|---|)
    data_lines = []
    for line in lines:
        stripped = line.strip()
        if re.match(r'^\|[-\s|]+\|$', stripped):
            continue
        data_lines.append(stripped)

    if not data_lines:
        return None

    # 解析每一行
    rows = []
    for line in data_lines:
        # 去掉首尾的 |，然后按 | 分割
        cells = [c.strip() for c in line[1:-1].split('|')]
        rows.append(cells)

    if len(rows) < 1:
        return None

    headers = rows[0]
    data_rows = rows[1:]

    return {'headers': headers, 'rows': data_rows}


def _load_json_data(dir_path: str, data_file: str, ref_type: str) -> dict:
    """加载 JSON 数据文件，返回原始数据字典"""
    data_path = os.path.join(dir_path, 'data', data_file)
    if not os.path.exists(data_path):
        return None

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def _assign_json_data(json_data: dict, ref_type: str, content: dict, current_column):
    """将加载的 JSON 数据分配到对应的内容字段，同时追加到 blocks 数组保持顺序"""
    # 图表类型
    chart_types = {'bar', 'pie', 'line', 'china-map', 'chinaMap'}
    if ref_type in chart_types:
        type_map = {
            'bar': 'bar',
            'pie': 'pie',
            'line': 'line',
            'china-map': 'chinaMap',
            'chinaMap': 'chinaMap',
        }
        mapped_type = type_map.get(ref_type, ref_type)
        chart_item = {
            'type': mapped_type,
            'id': json_data.get('id', f'chart-{ref_type}-{json_data.get("title", "")}'),
        }
        for key in ['title', 'xAxis', 'data', 'color', 'subType', 'data2', 'unit']:
            if key in json_data:
                chart_item[key] = json_data[key]
        # 字段别名兼容：labels -> xAxis
        if 'labels' in json_data and 'xAxis' not in chart_item:
            chart_item['xAxis'] = json_data['labels']
        # 饼图：data（对象数组）-> data2
        if mapped_type == 'pie' and 'data' in json_data and 'data2' not in chart_item:
            chart_item['data2'] = json_data['data']
            del chart_item['data']
        _append_to_field('charts', chart_item, content, current_column)
        _append_to_blocks('charts', chart_item, content, current_column)
        return

    # stats 类型
    if ref_type == 'stats':
        stats_items = json_data if isinstance(json_data, list) else json_data.get('items', [])
        for item in stats_items:
            _append_to_field('stats', item, content, current_column)
        _append_to_blocks('stats', stats_items, content, current_column)
        return

    # cards 类型
    if ref_type == 'cards':
        card_items = json_data if isinstance(json_data, list) else json_data.get('items', [])
        target = _get_target(content, current_column)
        if 'cards' not in target:
            target['cards'] = []
        target['cards'].append(card_items)
        _append_to_blocks('cards', card_items, content, current_column)
        return

    # timeline 类型
    if ref_type == 'timeline':
        # 支持同一个子章节中多个 timeline，追加到列表
        target = _get_target(content, current_column)
        if not target.get('timeline'):
            target['timeline'] = []
        target['timeline'].append(json_data)
        _append_to_blocks('timeline', json_data, content, current_column)
        return

    # branches 类型
    if ref_type == 'branches':
        # 支持同一个子章节中多个 branches，追加到列表
        target = _get_target(content, current_column)
        if not target.get('branchVisualizer'):
            target['branchVisualizer'] = []
        target['branchVisualizer'].append(json_data)
        _append_to_blocks('branchVisualizer', json_data, content, current_column)
        return

    # chips 类型
    if ref_type == 'chips':
        chip_items = json_data if isinstance(json_data, list) else json_data.get('items', [])
        for item in chip_items:
            _append_to_field('chips', item, content, current_column)
        _append_to_blocks('chips', chip_items, content, current_column)
        return


def _append_to_field(field: str, item: dict, content: dict, current_column):
    """将 item 追加到指定字段（支持分栏）"""
    target = _get_target(content, current_column)
    if field not in target:
        target[field] = []
    target[field].append(item)


def _append_to_blocks(block_type: str, data: any, content: dict, current_column):
    """将内容块追加到 blocks 数组以保持渲染顺序"""
    target = _get_target(content, current_column)
    if 'blocks' not in target:
        target['blocks'] = []
    target['blocks'].append({'type': block_type, 'data': data})


def _set_field(field: str, value: dict, content: dict, current_column):
    """设置指定字段的值（支持分栏）"""
    target = _get_target(content, current_column)
    target[field] = value


def _get_target(content: dict, current_column) -> dict:
    """获取当前内容目标（分栏 > 根内容）"""
    if current_column is not None:
        return current_column
    return content


def _load_chart_data(dir_path: str, data_file: str, chart_type: str) -> dict:
    """加载图表数据文件，返回 ChartItem 字典（兼容旧接口）"""
    json_data = _load_json_data(dir_path, data_file, chart_type)
    if not json_data:
        return None

    type_map = {
        'bar': 'bar',
        'pie': 'pie',
        'line': 'line',
        'china-map': 'chinaMap',
        'chinaMap': 'chinaMap',
    }
    mapped_type = type_map.get(chart_type, chart_type)

    result = {
        'type': mapped_type,
        'id': json_data.get('id', f'chart-{chart_type}-{data_file}'),
    }
    if 'title' in json_data:
        result['title'] = json_data['title']
    if 'xAxis' in json_data:
        result['xAxis'] = json_data['xAxis']
    if 'data' in json_data:
        result['data'] = json_data['data']
    if 'color' in json_data:
        result['color'] = json_data['color']
    if 'subType' in json_data:
        result['subType'] = json_data['subType']
    if 'data2' in json_data:
        result['data2'] = json_data['data2']
    if 'unit' in json_data:
        result['unit'] = json_data['unit']

    return result


def _parse_list_block(lines: list) -> dict:
    """解析 Markdown 列表块，返回 ListBlock 字典"""
    items = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 去掉列表标记
        if line.startswith('- '):
            content = line[2:].strip()
        elif re.match(r'^\d+\.\s', line):
            content = re.sub(r'^\d+\.\s', '', line).strip()
        else:
            continue

        if not content:
            continue

        # 尝试解析：图标 | 标题 | 副标题
        parts = content.split('|')
        if len(parts) >= 2:
            icon = parts[0].strip()
            title = parts[1].strip()
            subtitle = parts[2].strip() if len(parts) > 2 else ''
            items.append({'icon': icon, 'title': title, 'subtitle': subtitle})
        else:
            items.append({'icon': str(len(items) + 1), 'title': content, 'subtitle': ''})

    if not items:
        return None

    return {'title': '', 'items': items}
