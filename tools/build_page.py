#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_page.py - 单页面编译模块

职责：编译单个页面目录（单MD文件或多MD文件模式），生成 data.json。
- 单文件模式（page.md）：元信息只来自 frontmatter，正文一级标题忽略，
  二级标题作为 section 内容块
- 多文件模式（meta.md + 01-xxx.md 章节）：meta.md 提供元数据，
  章节文件提供各 section 内容，章节标题只来自章节文件 frontmatter

对外接口：
  compile_page(dir_path: str) -> dict   编译页面目录，返回 data.json 字典
  detect_compile_mode(dir_path: str) -> str   检测编译模式
"""

import os
import re
from build_utils import (
    read_file, parse_frontmatter, slugify, format_section_num,
    format_datetime, find_section_files, log
)
from build_page_parser import parse_markdown_blocks


def _parse_single_md_sections(body: str, dir_path: str = '') -> list:
    """
    解析单 MD 文件 body，按二级标题 (## ) 拆分为 sections。
    一级标题 (# ) 以及 Setext 风格标题均忽略，只从 frontmatter 获取页面标题。
    每个 section 的内容会解析 Markdown 特殊语法块。
    """
    sections = []
    lines = body.split('\n')
    current_title = None
    current_lines = []

    for line in lines:
        if line.startswith('## '):
            # 保存上一个 section
            if current_title is not None:
                section_body = '\n'.join(current_lines).strip()
                content = parse_markdown_blocks(section_body, dir_path)
                sections.append({
                    'id': slugify(current_title),
                    'title': current_title,
                    'subtitle': '',
                    'type': 'mixed',
                    'content': content,
                })
            current_title = line[3:].strip()
            current_lines = []
        elif current_title is not None:
            current_lines.append(line)

    # 保存最后一个 section
    if current_title is not None:
        section_body = '\n'.join(current_lines).strip()
        content = parse_markdown_blocks(section_body, dir_path)
        sections.append({
                'id': slugify(current_title),
                'title': current_title,
                'subtitle': '',
                'type': 'mixed',
                'content': content,
            })

    return sections


def _strip_ignored_headings(body: str) -> str:
    """
    移除正文中被忽略的一级标题 (# ) 和 Setext 风格标题（=== / ---）。
    这些标题不用于结构拆分，仅保留 frontmatter 中的元信息。
    """
    lines = body.split('\n')
    result = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        # ATX 一级标题 # 标题
        if re.match(r'^#\s+', stripped):
            i += 1
            continue
        # Setext 风格一级标题 === 和二级标题 ---
        if i + 1 < len(lines) and re.match(r'^={3,}\s*$', lines[i + 1].strip()):
            i += 2
            continue
        if i + 1 < len(lines) and re.match(r'^-{3,}\s*$', lines[i + 1].strip()):
            i += 2
            continue
        result.append(lines[i])
        i += 1
    return '\n'.join(result)


def compile_simple(dir_path: str) -> dict:
    """
    编译单文件模式（page.md）。
    解析规则：元信息只来自 frontmatter；正文一级标题忽略；
    每个二级标题对应一个 section 内容块。
    """
    page_md_path = os.path.join(dir_path, 'page.md')
    content = read_file(page_md_path)
    frontmatter, body = parse_frontmatter(content)

    # 标题只从 frontmatter 获取，回退到目录名
    title = frontmatter.get('title', '') or os.path.basename(dir_path)
    description = frontmatter.get('description', '')

    # 忽略正文中一级标题和 Setext 标题
    body = _strip_ignored_headings(body)

    # 解析 sections（按二级标题拆分，并解析 Markdown 语法块）
    sections = _parse_single_md_sections(body, dir_path)

    # 如果没有二级标题，body 内容作为 introduction
    introduction = ''
    if not sections:
        # 解析整个 body 作为 introduction 内容
        content = parse_markdown_blocks(body, dir_path)
        # 如果有结构化内容，创建一个默认 section
        if content and len(content) > 1:
            sections.append({
                'id': 'content',
                'title': '内容',
                'subtitle': '',
                'type': 'mixed',
                'content': content,
            })
        else:
            introduction = body.strip()

    return {
        'page': {
            'title': title,
            'description': description,
        },
        'hero': {
            'title': title,
            'tags': frontmatter.get('tags', []),
        },
        'introduction': introduction,
        'sections': sections,
        'version': frontmatter.get('version', 'v1'),
        'lastModified': format_datetime(),
    }


def compile_complex(dir_path: str) -> dict:
    """
    编译多文件模式（meta.md 元数据 + 01-xxx.md 章节）。
    meta.md 提供 page/hero/version 等元数据，章节文件提供各 section 内容。
    每个章节文件的标题只来自其 frontmatter 的 title 字段。
    """
    meta_md_path = os.path.join(dir_path, 'meta.md')
    meta_content = read_file(meta_md_path)
    meta_fm, _ = parse_frontmatter(meta_content)

    title = meta_fm.get('title', os.path.basename(dir_path))
    description = meta_fm.get('description', '')

    # meta.md 的 introduction 作为文章引言，缺省时回退到 description
    introduction = meta_fm.get('introduction', description)

    section_files = find_section_files(dir_path)
    sections = []

    for i, section_path in enumerate(section_files):
        section_content = read_file(section_path)
        section_fm, section_body = parse_frontmatter(section_content)

        # 章节标题只来自 frontmatter 的 title，缺省时使用文件名
        section_title = section_fm.get('title', '')
        if not section_title:
            base_name = os.path.splitext(os.path.basename(section_path))[0]
            # 去掉序号前缀，如 01-overview -> overview
            section_title = re.sub(r'^\d{2}-', '', base_name)
            section_title = section_title.replace('-', ' ').strip()
            if not section_title:
                section_title = '未命名'

        section_id = slugify(section_title)

        # 忽略章节正文中一级标题和 Setext 标题
        section_body = _strip_ignored_headings(section_body)

        # 解析章节 body 中的 Markdown 特殊语法块
        content = parse_markdown_blocks(section_body, dir_path)

        sections.append({
            'id': section_id,
            'title': section_title,
            'subtitle': section_fm.get('subtitle', ''),
            'type': 'mixed',
            'content': content,
        })

    return {
        'page': {
            'title': title,
            'description': description,
        },
        'hero': {
            'title': title,
            'tags': meta_fm.get('tags', []),
        },
        'introduction': introduction,
        'sections': sections,
        'version': meta_fm.get('version', 'v1'),
        'lastModified': format_datetime(),
    }


def compile_page(dir_path: str) -> dict:
    """
    编译单个页面目录，返回 data.json 字典。
    根据目录内容自动判断使用单文件模式还是多文件模式。
    """
    from build_utils import detect_compile_mode

    mode = detect_compile_mode(dir_path)

    if mode == 'none':
        log('warn', '无 Markdown 文件，跳过编译', {'dir': dir_path})
        return None

    if mode == 'simple':
        return compile_simple(dir_path)
    else:
        return compile_complex(dir_path)
