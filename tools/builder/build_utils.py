#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_utils.py - 编译工具公共模块

提供编译流程中各模块共享的基础工具函数：
- 文件读写（JSON/YAML/Markdown）
- 日志输出（线程安全）
- 日期格式化与字符串处理
- Frontmatter 解析
- 目录扫描与文件查找

被 build_page.py、build_index.py、build_service.py 共同引用。
"""

import os
import re
import json
import shutil
import time
import tempfile
from datetime import datetime
from threading import Lock

try:
    import yaml
except ImportError:
    yaml = None

# 日志锁（保证多线程日志不混乱）
LOG_LOCK = Lock()


def log(level: str, message: str, meta: dict = None):
    """线程安全的日志输出"""
    timestamp = datetime.now().isoformat()
    meta_str = f' {json.dumps(meta, ensure_ascii=False)}' if meta else ''
    with LOG_LOCK:
        try:
            print(f'{timestamp} [build-service] [{level.upper()}] {message}{meta_str}', flush=True)
        except UnicodeEncodeError:
            safe_msg = f'{timestamp} [build-service] [{level.upper()}] {message}{meta_str}'
            safe_msg = safe_msg.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            print(safe_msg, flush=True)


def read_file(path: str) -> str:
    """读取文本文件，自动检测 UTF-8 / GBK 编码"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(path, 'r', encoding='gbk') as f:
            return f.read()


def write_json(path: str, data: dict):
    """原子写入 JSON 文件，带重试和权限错误处理。临时文件写入系统临时目录，避免污染 data root。"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # 使用系统临时目录存放临时文件，避免在 data root 下产生临时文件
    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.tmp', prefix='kc_build_', dir=tempfile.gettempdir())
    try:
        with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        shutil.move(tmp_path, path)
    except PermissionError:
        log('warn', f'原子写入失败，回退直接写入: {path}')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    finally:
        # 确保临时文件被清理
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def read_json(path: str) -> dict:
    """读取 JSON 文件，失败返回 None"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def read_meta(dir_path: str) -> dict:
    """读取目录下的 meta.yaml（优先）或 meta.json，失败返回空字典"""
    meta_yaml_path = os.path.join(dir_path, 'meta.yaml')
    meta_json_path = os.path.join(dir_path, 'meta.json')

    if os.path.exists(meta_yaml_path) and yaml:
        try:
            with open(meta_yaml_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            log('warn', f'读取 meta.yaml 失败: {e}', {'path': meta_yaml_path})
            return {}

    if os.path.exists(meta_json_path):
        data = read_json(meta_json_path)
        return data if data else {}

    return {}


def format_datetime(dt: datetime = None) -> str:
    """格式化日期时间为 YYYY-MM-DD HH:MM:SS"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def slugify(text: str) -> str:
    """简单 slugify：保留中文、字母、数字和连字符"""
    text = text.strip()
    result = []
    for ch in text:
        if ch.isalnum() or ch == '-' or '\u4e00' <= ch <= '\u9fff' or '\u3400' <= ch <= '\u4dbf':
            result.append(ch)
        else:
            result.append('-')
    return ''.join(result).strip('-')


def parse_frontmatter(text: str) -> tuple:
    """解析 Markdown 文件的 YAML Frontmatter，返回 (frontmatter_dict, body)"""
    if not text.startswith('---'):
        return {}, text

    match = re.match(r'^---\s*\n(.*?)\n---\s*(?:\n|$)', text, re.DOTALL)
    if not match:
        return {}, text

    fm_text = match.group(1)
    body = text[match.end():]

    frontmatter = {}
    lines = fm_text.split('\n')
    current_key = None

    for line in lines:
        key_match = re.match(r'^(\w+):\s*(.*)$', line)
        if key_match:
            current_key = key_match.group(1)
            value = key_match.group(2).strip()
            if value.startswith('[') and value.endswith(']'):
                frontmatter[current_key] = [s.strip() for s in value[1:-1].split(',') if s.strip()]
            else:
                frontmatter[current_key] = value
        elif current_key and line.strip().startswith('- '):
            if not isinstance(frontmatter.get(current_key), list):
                existing = frontmatter.get(current_key, '')
                frontmatter[current_key] = [existing] if existing else []
            frontmatter[current_key].append(line.strip()[2:])

    return frontmatter, body


def find_section_files(dir_path: str) -> list:
    """查找目录下的章节文件（01-xxx.md, 02-xxx.md 等），返回排序后的完整路径列表"""
    files = []
    try:
        for entry in os.scandir(dir_path):
            if entry.is_file() and re.match(r'^\d{2}-.*\.md$', entry.name):
                files.append(entry.path)
    except OSError:
        pass
    return sorted(files)


def detect_compile_mode(dir_path: str) -> str:
    """
    判断页面目录的编译模式
    - 'complex': 有 meta.md + 01-xxx.md 章节文件
    - 'simple':  有 page.md
    - 'none':    无 md 文件
    """
    has_meta_md = os.path.exists(os.path.join(dir_path, 'meta.md'))
    has_page_md = os.path.exists(os.path.join(dir_path, 'page.md'))
    has_sections = len(find_section_files(dir_path)) > 0

    if has_meta_md and has_sections:
        return 'complex'
    if has_page_md:
        return 'simple'
    return 'none'


def strip_order_prefix(name: str) -> str:
    """去掉文件夹名前的序号前缀，如 '01 文学' -> '文学', '02 自然科学' -> '自然科学'"""
    match = re.match(r'^\d{2,3}\s+(.+)$', name)
    if match:
        return match.group(1)
    return name


def copy_dir_contents(src_dir: str, dst_dir: str):
    """递归拷贝目录内容，保留文件结构，跳过 .md 和 .yaml 文件"""
    if not os.path.isdir(src_dir):
        return
    # 如果源目录和目标目录相同，跳过复制
    if os.path.abspath(src_dir) == os.path.abspath(dst_dir):
        return
    os.makedirs(dst_dir, exist_ok=True)
    for entry in os.scandir(src_dir):
        # 跳过 markdown 和 yaml 源文件（这些由编译器处理）
        if entry.name.endswith('.md') or entry.name.endswith('.yaml') or entry.name.endswith('.yml'):
            continue
        src_path = entry.path
        dst_path = os.path.join(dst_dir, entry.name)
        if entry.is_dir():
            copy_dir_contents(src_path, dst_path)
        elif entry.is_file():
            shutil.copy2(src_path, dst_path)
