#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_service_info.py - Info 页面编译模块

职责：编译站点 info 文件夹为 info/data.json 数据。
复用 build_page.py 的核心逻辑，保持编译行为一致。

对外接口：
  compile_info_page(info_dir_path: str) -> dict
"""

import os
from build_page import compile_simple, compile_complex
from build_utils import format_datetime


def compile_info_page(info_dir_path: str) -> dict:
    """编译 info 文件夹为 info/data.json 数据"""
    has_page_md = os.path.exists(os.path.join(info_dir_path, 'page.md'))
    has_meta_md = os.path.exists(os.path.join(info_dir_path, 'meta.md'))
    from build_utils import find_section_files
    section_files = find_section_files(info_dir_path)
    has_sections = len(section_files) > 0

    # 简单模式：page.md
    if has_page_md and not (has_meta_md and has_sections):
        data = compile_simple(info_dir_path)
        if data:
            data['lastModified'] = format_datetime()
        return data

    # 复杂模式：meta.md + 章节文件
    if has_meta_md and has_sections:
        data = compile_complex(info_dir_path)
        if data:
            data['lastModified'] = format_datetime()
        return data

    return None
