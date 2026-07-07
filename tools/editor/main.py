#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py - Markdown 编辑器 Flask 后端

提供文件管理 API 和页面编译功能，数据根目录为 E:\\code\\sitesanddata\\my_sites_data\\data
"""

import os
import sys
import json
import base64
import re
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory

# 将父目录（tools）加入 sys.path，以便导入 build_page
TOOLS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from build_page import compile_page
from build_utils import write_json

app = Flask(__name__, static_folder='static')

# 数据根目录（默认路径，可通过环境变量或前端设置覆盖）
DEFAULT_DATA_ROOT = Path(r'E:\code\sitesanddata\my_sites_data\data').resolve()
DATA_ROOT = DEFAULT_DATA_ROOT


def _get_data_root():
    """获取当前数据根目录，优先使用环境变量 DATA_ROOT"""
    env_root = os.environ.get('DATA_ROOT', '')
    if env_root:
        return Path(env_root).resolve()
    return DATA_ROOT


def _safe_path(relative_path: str) -> Path:
    """将相对路径解析为 DATA_ROOT 下的安全绝对路径，防止路径遍历"""
    root = _get_data_root()
    if not relative_path:
        return root
    # 规范化路径，去除 .. 等
    relative_path = relative_path.replace('\\', '/')
    parts = relative_path.split('/')
    safe_parts = [p for p in parts if p and p != '.' and p != '..']
    target = root.joinpath(*safe_parts).resolve()
    # 确保目标在 DATA_ROOT 下
    try:
        target.relative_to(root)
    except ValueError:
        raise ValueError('Path traversal detected')
    return target


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


@app.route('/api/config', methods=['GET'])
def get_config():
    """GET /api/config - 获取当前数据根目录配置"""
    root = _get_data_root()
    return jsonify({
        'data_root': str(root),
        'default_data_root': str(DEFAULT_DATA_ROOT),
        'exists': root.exists() and root.is_dir()
    })


@app.route('/api/config', methods=['POST'])
def set_config():
    """POST /api/config - 设置数据根目录 (body: {data_root})"""
    global DATA_ROOT
    data = request.get_json(force=True, silent=True) or {}
    new_root = data.get('data_root', '')
    if not new_root:
        return jsonify({'error': 'data_root is required'}), 400
    
    path = Path(new_root).resolve()
    if not path.exists():
        return jsonify({'error': 'Directory does not exist'}), 400
    if not path.is_dir():
        return jsonify({'error': 'Path is not a directory'}), 400
    
    DATA_ROOT = path
    return jsonify({'success': True, 'data_root': str(path)})


@app.route('/api/files', methods=['GET'])
def list_files():
    """GET /api/files?path=<relative_path> - 列出目录内容"""
    rel_path = request.args.get('path', '')
    try:
        target = _safe_path(rel_path)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    if not target.exists():
        return jsonify({'error': 'Not found'}), 404
    if not target.is_dir():
        return jsonify({'error': 'Not a directory'}), 400

    items = []
    try:
        for entry in sorted(target.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())):
            items.append({
                'name': entry.name,
                'path': str(entry.relative_to(DATA_ROOT)).replace('\\', '/'),
                'type': 'directory' if entry.is_dir() else 'file',
                'size': entry.stat().st_size if entry.is_file() else 0,
            })
    except OSError as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'items': items, 'path': rel_path})


@app.route('/api/file', methods=['GET'])
def read_file():
    """GET /api/file?path=<relative_path> - 读取文件内容"""
    rel_path = request.args.get('path', '')
    try:
        target = _safe_path(rel_path)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    if not target.exists():
        return jsonify({'error': 'Not found'}), 404
    if not target.is_file():
        return jsonify({'error': 'Not a file'}), 400

    try:
        with open(target, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(target, 'r', encoding='gbk') as f:
            content = f.read()
    except OSError as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'content': content, 'path': rel_path})


@app.route('/api/file', methods=['POST'])
def save_file():
    """POST /api/file - 保存文件内容 (body: {path, content})"""
    data = request.get_json(force=True, silent=True) or {}
    rel_path = data.get('path', '')
    content = data.get('content', '')

    if not rel_path:
        return jsonify({'error': 'path is required'}), 400

    try:
        target = _safe_path(rel_path)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)
    except OSError as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'success': True, 'path': rel_path})


@app.route('/api/file', methods=['DELETE'])
def delete_file():
    """DELETE /api/file?path=<relative_path> - 删除文件或目录"""
    rel_path = request.args.get('path', '')
    if not rel_path:
        return jsonify({'error': 'path is required'}), 400

    try:
        target = _safe_path(rel_path)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    if not target.exists():
        return jsonify({'error': 'Not found'}), 404

    try:
        if target.is_dir():
            import shutil
            shutil.rmtree(target)
        else:
            target.unlink()
    except OSError as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'success': True})


@app.route('/api/file/upload', methods=['POST'])
def upload_image():
    """POST /api/file/upload - 上传图片 (body: {path, data: base64})"""
    data = request.get_json(force=True, silent=True) or {}
    rel_path = data.get('path', '')
    b64_data = data.get('data', '')

    if not rel_path or not b64_data:
        return jsonify({'error': 'path and data are required'}), 400

    try:
        target = _safe_path(rel_path)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    # 解析 base64
    if ',' in b64_data:
        b64_data = b64_data.split(',', 1)[1]

    try:
        img_bytes = base64.b64decode(b64_data)
    except Exception as e:
        return jsonify({'error': f'Invalid base64: {e}'}), 400

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, 'wb') as f:
            f.write(img_bytes)
    except OSError as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'success': True, 'path': rel_path})


@app.route('/api/file/exists', methods=['GET'])
def file_exists():
    """GET /api/file/exists?path=<relative_path> - 检查文件是否存在"""
    rel_path = request.args.get('path', '')
    try:
        target = _safe_path(rel_path)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'exists': target.exists(), 'is_file': target.is_file() if target.exists() else False})


@app.route('/api/build', methods=['POST'])
def build_page():
    """POST /api/build - 编译单个页面目录 (body: {path})"""
    data = request.get_json(force=True, silent=True) or {}
    rel_path = data.get('path', '')

    if not rel_path:
        return jsonify({'error': 'path is required'}), 400

    try:
        target = _safe_path(rel_path)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    if not target.exists() or not target.is_dir():
        return jsonify({'error': 'Not a valid directory'}), 400

    try:
        result = compile_page(str(target))
    except Exception as e:
        return jsonify({'error': f'Compile failed: {e}'}), 500

    if result is None:
        return jsonify({'error': 'No markdown files found to compile'}), 400

    # 写入 data.json 到同一目录
    output_path = target / 'data.json'
    try:
        write_json(str(output_path), result)
    except Exception as e:
        return jsonify({'error': f'Write data.json failed: {e}'}), 500

    return jsonify({'success': True, 'path': str(output_path.relative_to(DATA_ROOT)).replace('\\', '/')})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
