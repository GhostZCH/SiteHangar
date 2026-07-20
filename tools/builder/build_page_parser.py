#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_page_parser.py - Markdown 特殊语法解析器

职责：解析 Markdown 文本中的各种特殊语法块，返回结构化 content 字典。
支持两种数据提供方式：
1. JSON 文件引用（适合大量数据）：![type](data/xxx.json)
2. Markdown Code 块（适合少量人工编写数据）：```type 包裹的 JSON```

支持的语法块：
  - ![stats](data/xxx.json) 或 ```stats [...] ``` -> content.stats
  - ![cards](data/xxx.json) 或 ```cards [...] ``` -> content.cards
  - ![timeline](data/xxx.json) 或 ```timeline {...} ``` -> content.timeline
  - ![branches](data/xxx.json) 或 ```branches {...} ``` -> content.branchVisualizer
  - ![chips](data/xxx.json) 或 ```chips [...] ``` -> content.chips
  - Markdown 表格  -> content.tables
  - ![bar|pie|line|china-map](data/xxx.json) 或对应 code 块 -> content.charts
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
    parser = _MarkdownParser(text, dir_path)
    return parser.parse()


class _MarkdownParser:
    """Markdown 特殊语法块解析器。

    将解析过程中的共享状态（content、当前段落、当前分栏等）封装为实例属性，
    各语法块的解析逻辑拆分为独立方法，主循环仅负责按行分发。
    """

    def __init__(self, text: str, dir_path: str = ''):
        self.dir_path = dir_path
        self.lines = text.split('\n')
        self.i = 0
        self.content = {
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
        self.current_para_lines = []
        self.current_column = None
        self.in_column_block = False

    # ------------------------------------------------------------------
    # 段落 / 分栏状态管理
    # ------------------------------------------------------------------
    def _flush_para(self):
        """将当前累积的普通文本段落写入 description 或当前分栏"""
        if not self.current_para_lines:
            return
        para = '\n'.join(self.current_para_lines).strip()
        if not para:
            self.current_para_lines.clear()
            return
        if self.current_column is not None:
            self.current_column['items'].append(para)
        else:
            self.content['description'].append(para)
            self.content['blocks'].append({'type': 'description', 'data': [para]})
        self.current_para_lines.clear()

    @staticmethod
    def _is_column_empty(col: dict) -> bool:
        """检查分栏是否为空（没有文本、表格、列表、卡片）"""
        return not col['items'] and not col['tables'] and col['list'] is None and not col['cards']

    @staticmethod
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

    def _new_column(self) -> dict:
        return {'items': [], 'tables': [], 'list': None, 'cards': []}

    def _flush_column(self):
        """保存当前分栏"""
        if self.current_column is None:
            return
        self._flush_para()
        if not self._is_column_empty(self.current_column):
            self.content['columns'].append(self._clean_column(self.current_column))
        self.current_column = None

    def _flush_columns(self):
        """结束分栏区域，保存当前分栏并清空状态"""
        self._flush_column()
        self.in_column_block = False

    def _start_column(self):
        """开始一个新的分栏"""
        self._flush_para()
        if self.current_column is not None and not self._is_column_empty(self.current_column):
            self.content['columns'].append(self._clean_column(self.current_column))
        self.current_column = self._new_column()
        self.in_column_block = True

    def _append_text(self, text: str):
        """将一段文本追加到当前分栏或根 description"""
        if self.current_column is not None:
            self.current_column['items'].append(text)
        else:
            self.content['description'].append(text)
            self.content['blocks'].append({'type': 'description', 'data': [text]})

    # ------------------------------------------------------------------
    # 主循环：逐行分发到各语法块处理器
    # ------------------------------------------------------------------
    def parse(self) -> dict:
        while self.i < len(self.lines):
            stripped = self.lines[self.i].strip()

            if self._try_column_marker(stripped):
                continue
            if self._try_code_block(stripped):
                continue
            if self._try_fence_block(stripped):
                continue
            if self._try_table(stripped):
                continue
            if self._try_json_ref(stripped):
                continue
            if self._try_image(stripped):
                continue
            if self._try_list(stripped):
                continue
            if self._try_heading(stripped):
                continue
            if self._try_vote(stripped):
                continue

            # 普通文本行
            self.current_para_lines.append(self.lines[self.i])
            self.i += 1

        self._flush_para()
        self._flush_columns()

        # 移除空字段
        return {key: value for key, value in self.content.items() if value}

    # ------------------------------------------------------------------
    # 各语法块处理器（命名即语法类型，返回是否命中）
    # ------------------------------------------------------------------
    def _try_column_marker(self, stripped: str) -> bool:
        """分栏标记：===== 开始/结束分栏区域，----- 分隔分栏"""
        if stripped == COLUMN_START_MARKER:
            if self.in_column_block:
                self._flush_columns()
            else:
                self._start_column()
            self.i += 1
            return True

        if stripped == COLUMN_SPLIT_MARKER:
            if self.in_column_block:
                # 当前分栏结束，下一个分栏开始
                self._flush_column()
                self.current_column = self._new_column()
            # 不在分栏区域内时，忽略孤立的分隔符
            self.i += 1
            return True

        return False

    def _try_code_block(self, stripped: str) -> bool:
        """Code 块 (```type) - 支持 stats/cards/timeline/branches/chips/bar/pie/line/china-map"""
        match = re.match(r'^```(\w+(-\w+)?)\s*$', stripped)
        if not match:
            return False

        code_type = match.group(1)
        supported_types = {'stats', 'cards', 'timeline', 'branches', 'chips',
                           'bar', 'pie', 'line', 'china-map', 'chinaMap', 'charts'}
        self._flush_para()

        code_lines = []
        self.i += 1
        while self.i < len(self.lines) and self.lines[self.i].strip() != '```':
            code_lines.append(self.lines[self.i])
            self.i += 1
        code_content = '\n'.join(code_lines)

        handled = False
        if code_type in supported_types and code_content.strip():
            try:
                json_data = json.loads(code_content.strip())
                # charts 块内嵌了 type 字段，用其作为实际图表类型
                actual_type = json_data.get('type', 'bar') if code_type == 'charts' else code_type
                _assign_json_data(json_data, actual_type, self.content, self.current_column)
                handled = True
            except json.JSONDecodeError:
                pass

        if not handled:
            # JSON 解析失败或不支持的类型，作为普通代码块保留
            self._append_text(f'```{code_type}\n{code_content}\n```')

        self.i += 1
        return True

    def _try_fence_block(self, stripped: str) -> bool:
        """围栏语法块 (::: type) - 支持 stats/cards/timeline/branches/chips"""
        match = re.match(r'^:::\s*(\w+)\s*$', stripped)
        if not match:
            return False

        fence_type = match.group(1)
        supported_fence_types = {'stats', 'cards', 'timeline', 'branches', 'chips'}
        if fence_type not in supported_fence_types:
            return False

        self._flush_para()
        fence_lines = []
        self.i += 1
        while self.i < len(self.lines) and not re.match(r'^:::\s*$', self.lines[self.i].strip()):
            fence_lines.append(self.lines[self.i])
            self.i += 1

        self._apply_fence(fence_type, fence_lines)
        self.i += 1
        return True

    def _apply_fence(self, fence_type: str, fence_lines: list):
        """将围栏块内容解析后写入 content / 当前分栏"""
        target = _get_target(self.content, self.current_column)

        if fence_type == 'stats':
            stats_items = _parse_stats_block(fence_lines)
            for item in stats_items:
                _append_to_field('stats', item, self.content, self.current_column)
            _append_to_blocks('stats', stats_items, self.content, self.current_column)
        elif fence_type == 'cards':
            card_items = _parse_cards_block(fence_lines)
            target.setdefault('cards', []).append(card_items)
            _append_to_blocks('cards', card_items, self.content, self.current_column)
        elif fence_type == 'timeline':
            timeline_data = _parse_timeline_block(fence_lines)
            if timeline_data:
                target.setdefault('timeline', []).append(timeline_data)
                _append_to_blocks('timeline', timeline_data, self.content, self.current_column)
        elif fence_type == 'branches':
            branches_data = _parse_branches_block(fence_lines)
            if branches_data:
                target.setdefault('branchVisualizer', []).append(branches_data)
                _append_to_blocks('branchVisualizer', branches_data, self.content, self.current_column)
        elif fence_type == 'chips':
            chip_items = _parse_chips_block(fence_lines)
            for item in chip_items:
                _append_to_field('chips', item, self.content, self.current_column)
            _append_to_blocks('chips', chip_items, self.content, self.current_column)

    def _try_table(self, stripped: str) -> bool:
        """Markdown 表格 (| header | header |)"""
        if not (stripped.startswith('|') and stripped.endswith('|') and '|' in stripped[1:-1]):
            return False

        self._flush_para()
        table_lines = []
        while self.i < len(self.lines) and self.lines[self.i].strip().startswith('|'):
            table_lines.append(self.lines[self.i])
            self.i += 1

        table = _parse_markdown_table(table_lines)
        if table:
            if self.current_column is not None:
                self.current_column['tables'].append(table)
            else:
                self.content['tables'].append(table)
                self.content['blocks'].append({'type': 'tables', 'data': table})
        return True

    def _try_json_ref(self, stripped: str) -> bool:
        """图表/组件 JSON 引用 ![type](data/xxx.json)（image 类型由 _try_image 处理）"""
        match = re.match(r'^!\[([a-zA-Z-]+)\]\((data/)?([^)]+)\)$', stripped)
        if not match:
            return False

        ref_type = match.group(1)
        if ref_type == 'image':
            return False

        self._flush_para()
        data_file = match.group(3)
        if not data_file.endswith('.json'):
            data_file += '.json'
        json_data = _load_json_data(self.dir_path, data_file, ref_type)
        if json_data:
            _assign_json_data(json_data, ref_type, self.content, self.current_column)
        self.i += 1
        return True

    def _try_image(self, stripped: str) -> bool:
        """图片引用 ![image](image/xxx.jpg) - 保留在 description 中由前端渲染"""
        match = re.match(r'^!\[image\]\(([^)]+)\)$', stripped)
        if not match:
            return False

        self._flush_para()
        self._append_text(f'![image]({match.group(1)})')
        self.i += 1
        return True

    def _try_list(self, stripped: str) -> bool:
        """列表块 (- item 或 1. item) - 只有包含 | 分隔符的才解析为 list 类型"""
        if not re.match(r'^(-\s|\d+\.\s)', stripped):
            return False

        self._flush_para()
        list_lines = []
        while self.i < len(self.lines) and (
            self.lines[self.i].strip().startswith('- ')
            or re.match(r'^\d+\.\s', self.lines[self.i].strip())
        ):
            list_lines.append(self.lines[self.i])
            self.i += 1

        has_pipe = any('|' in line for line in list_lines)
        if has_pipe:
            list_block = _parse_list_block(list_lines)
            if list_block:
                if self.current_column is not None:
                    if self.current_column['list'] is None:
                        self.current_column['list'] = list_block
                    else:
                        self.current_column['list']['items'].extend(list_block['items'])
                else:
                    self.content['list'] = list_block
                    self.content['blocks'].append({'type': 'list', 'data': list_block})
        else:
            # 普通列表，保留在 description 中（作为一个整体）
            self._append_text('\n'.join(list_lines))
        return True

    def _try_heading(self, stripped: str) -> bool:
        """标题 (## / ### / ####) - 保留在 description 中由前端渲染"""
        for prefix in ('#### ', '### ', '## '):
            if stripped.startswith(prefix):
                self._flush_para()
                self._append_text(f'{prefix}{stripped[len(prefix):].strip()}')
                self.i += 1
                return True
        return False

    def _try_vote(self, stripped: str) -> bool:
        """投票语法 [vote:xxx] - 直接忽略"""
        if re.match(r'^\[vote:[^\]]+\]$', stripped):
            self.i += 1
            return True
        return False


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


def _get_target(content: dict, current_column) -> dict:
    """获取当前内容目标（分栏 > 根内容）"""
    if current_column is not None:
        return current_column
    return content


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
