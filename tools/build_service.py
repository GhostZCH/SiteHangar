#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_service.py - 全体编译入口模块

职责：
1. 扫描所有站点目录
2. 并发编译所有页面（调用 build_page.compile_page）
3. 拷贝文章数据文件和图片到 result 目录
4. 生成站点统一的 index.json（调用 build_index.build_site_index）
5. 编译 info 文件夹为 info/data.json（调用 build_service_info.compile_info_page）

用法：
    python tools/build_service.py --data-root e:\code\sitesanddata\my_sites_data\data --output-dir e:\code\sitesanddata\my_sites_data\result
"""

import os
import sys
import re
import json
import time
import shutil
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from build_utils import (
    log, read_file, write_json, read_json, read_meta, format_datetime,
    detect_compile_mode, find_section_files, get_file_mtime, copy_dir_contents,
    parse_frontmatter, slugify, format_section_num
)
from build_page import compile_page
from build_index import (
    build_site_index,
    extract_page_info, extract_page_info_from_data
)
from build_service_info import compile_info_page

# 配置
DATA_ROOT = None
BUILD_OUTPUT_DIR = None
MAX_WORKERS = (os.cpu_count() or 4) * 2


def discover_sites() -> list:
    """动态发现所有站点目录"""
    sites = []
    try:
        for entry in os.scandir(DATA_ROOT):
            if entry.is_dir():
                sites.append(entry.name)
    except OSError:
        pass
    return sorted(sites)


def find_page_dirs(root_path: str) -> list:
    """递归扫描目录，找到所有需要编译的页面目录（叶子目录）"""
    page_dirs = []

    def scan(dir_path: str):
        # 如果当前目录有 md 文件，是页面目录，加入列表
        mode = detect_compile_mode(dir_path)
        if mode != 'none':
            page_dirs.append(dir_path)
            return
        # 否则递归扫描子目录
        try:
            for entry in os.scandir(dir_path):
                if entry.is_dir():
                    scan(entry.path)
        except OSError:
            pass

    scan(root_path)
    return page_dirs


def needs_compile(dir_path: str, mode: str, output_dir: str) -> bool:
    """增量编译判断：检查目录是否需要重新编译"""
    # 计算输出目录对应的 data.json 路径
    rel_path = os.path.relpath(dir_path, DATA_ROOT)
    if output_dir:
        data_json_path = os.path.join(output_dir, rel_path, 'data.json')
    else:
        data_json_path = os.path.join(dir_path, 'data.json')

    if not os.path.exists(data_json_path):
        return True

    existing_data = read_json(data_json_path)
    compiled_at_str = existing_data.get('lastModified') if existing_data else None
    compiled_at = None
    if compiled_at_str:
        try:
            compiled_at = datetime.strptime(compiled_at_str, '%Y-%m-%d %H:%M:%S').timestamp()
        except ValueError:
            compiled_at = None

    # 确定需要扫描的源文件
    if mode == 'simple':
        source_files = ['page.md']
    else:
        source_files = ['meta.md'] + [os.path.basename(f) for f in find_section_files(dir_path)]

    max_mtime = None
    for filename in source_files:
        file_path = os.path.join(dir_path, filename)
        if os.path.exists(file_path):
            mtime = os.path.getmtime(file_path)
            if max_mtime is None or mtime > max_mtime:
                max_mtime = mtime

    if max_mtime is None:
        return False
    if compiled_at is None:
        return True
    return max_mtime > compiled_at


def get_route_path(rel_path: str, site_name: str) -> str:
    """将相对路径转换为前端路由路径（去掉站点名前缀）"""
    parts = rel_path.replace('\\', '/').split('/')
    # 去掉站点名前缀
    if parts and parts[0] == site_name:
        parts = parts[1:]
    return '/' + '/'.join(parts)


def get_column_slug(rel_path: str, site_name: str) -> str:
    """从相对路径中提取栏目 slug"""
    parts = rel_path.replace('\\', '/').split('/')
    # 去掉站点名前缀
    if parts and parts[0] == site_name:
        parts = parts[1:]
    # 第一个部分就是栏目 slug
    column_slug = parts[0] if parts else ''
    # info 是特殊目录，不作为栏目
    return '' if column_slug == 'info' else column_slug


def _copy_page_assets(src_dir: str, dst_dir: str):
    """拷贝页面目录下的数据文件和图片到输出目录"""
    # 拷贝 data/ 目录
    src_data_dir = os.path.join(src_dir, 'data')
    if os.path.isdir(src_data_dir):
        dst_data_dir = os.path.join(dst_dir, 'data')
        copy_dir_contents(src_data_dir, dst_data_dir)

    # 拷贝 images/ 目录
    src_images_dir = os.path.join(src_dir, 'images')
    if os.path.isdir(src_images_dir):
        dst_images_dir = os.path.join(dst_dir, 'images')
        copy_dir_contents(src_images_dir, dst_images_dir)

    # 拷贝 image/ 目录（单数形式兼容）
    src_image_dir = os.path.join(src_dir, 'image')
    if os.path.isdir(src_image_dir):
        dst_image_dir = os.path.join(dst_dir, 'image')
        copy_dir_contents(src_image_dir, dst_image_dir)

    # 拷贝 img/ 目录（页面图片资源）
    src_img_dir = os.path.join(src_dir, 'img')
    if os.path.isdir(src_img_dir):
        dst_img_dir = os.path.join(dst_dir, 'img')
        copy_dir_contents(src_img_dir, dst_img_dir)


def build_site(site_name: str, dry_run: bool = False, output_dir: str = None) -> dict:
    """构建单个站点"""
    site_start_time = time.time()
    site_path = os.path.join(DATA_ROOT, site_name)
    out_site_path = os.path.join(output_dir, site_name) if output_dir else site_path

    log('info', '开始构建站点', {'site': site_name, 'output_dir': output_dir})

    # 1. 找到所有页面目录（叶子目录）
    page_dirs = find_page_dirs(site_path)
    log('info', f'找到 {len(page_dirs)} 个页面目录', {'site': site_name})

    compiled_count = 0
    skipped_count = 0
    error_count = 0
    # 按栏目收集页面信息: {column_slug: [page_info, ...]}
    column_pages = {}

    def compile_task(dir_path: str):
        rel_path = os.path.relpath(dir_path, DATA_ROOT)
        mode = detect_compile_mode(dir_path)

        # 增量编译判断
        if not needs_compile(dir_path, mode, output_dir):
            # 跳过编译但收集页面信息（从输出目录读取 data.json）
            if output_dir:
                out_dir = os.path.join(output_dir, rel_path)
                data_json_path = os.path.join(out_dir, 'data.json')
            else:
                data_json_path = os.path.join(dir_path, 'data.json')
            route_path = get_route_path(rel_path, site_name)
            info = extract_page_info(data_json_path, route_path)
            if info:
                column_slug = get_column_slug(rel_path, site_name)
                if column_slug:
                    column_pages.setdefault(column_slug, []).append(info)
            return {'dir_path': dir_path, 'rel_path': rel_path, 'compiled': False, 'skipped': True}

        # 编译页面
        data = compile_page(dir_path)
        if data is None:
            return {'dir_path': dir_path, 'rel_path': rel_path, 'compiled': False, 'skipped': False, 'error': '编译失败'}

        if not dry_run:
            if output_dir:
                out_dir = os.path.join(output_dir, rel_path)
            else:
                out_dir = dir_path
            data_json_path = os.path.join(out_dir, 'data.json')
            write_json(data_json_path, data)

            # 拷贝数据文件和图片
            _copy_page_assets(dir_path, out_dir)

        # 收集页面信息
        route_path = get_route_path(rel_path, site_name)
        info = extract_page_info_from_data(data, route_path)
        if info:
            column_slug = get_column_slug(rel_path, site_name)
            if column_slug:
                column_pages.setdefault(column_slug, []).append(info)

        log('info', '编译成功', {'path': rel_path, 'mode': mode})
        return {'dir_path': dir_path, 'rel_path': rel_path, 'compiled': True, 'skipped': False}

    # 并发编译所有页面
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(compile_task, dp): dp for dp in page_dirs}
        for future in as_completed(futures):
            result = future.result()
            if result.get('skipped'):
                skipped_count += 1
            elif result.get('compiled'):
                compiled_count += 1
            else:
                error_count += 1

    # 2. 编译 info 文件夹
    info_dir_path = os.path.join(site_path, 'info')
    if os.path.isdir(info_dir_path):
        info_data = compile_info_page(info_dir_path)
        if info_data and not dry_run:
            if output_dir:
                info_json_path = os.path.join(out_site_path, 'info', 'data.json')
            else:
                info_json_path = os.path.join(info_dir_path, 'data.json')
            write_json(info_json_path, info_data)
            log('info', 'info 文件夹编译成功', {'site': site_name})

    # 3. 生成站点统一的 index.json（只生成站点根目录一个）
    if not dry_run:
        if output_dir:
            index_dir = out_site_path
        else:
            index_dir = site_path

        index_data = build_site_index(site_path, site_name, column_pages, output_dir=output_dir)
        index_path = os.path.join(index_dir, 'index.json')
        write_json(index_path, index_data)
        log('info', '生成站点索引', {'site': site_name, 'columns': list(column_pages.keys())})

    # 4. 拷贝站点级资源
    if output_dir and not dry_run:
        # 拷贝站点 meta.yaml（供后端读取栏目配置）
        src_meta_yaml = os.path.join(site_path, 'meta.yaml')
        if os.path.isfile(src_meta_yaml):
            dst_meta_yaml = os.path.join(out_site_path, 'meta.yaml')
            try:
                shutil.copy2(src_meta_yaml, dst_meta_yaml)
                log('info', '拷贝站点 meta.yaml', {'site': site_name, 'from': src_meta_yaml, 'to': dst_meta_yaml})
            except OSError as e:
                log('warning', '拷贝站点 meta.yaml 失败', {'site': site_name, 'error': str(e)})

        # 拷贝站点 image 目录
        src_image_dir = os.path.join(site_path, 'image')
        if os.path.isdir(src_image_dir):
            out_image_dir = os.path.join(out_site_path, 'image')
            try:
                if os.path.exists(out_image_dir):
                    shutil.rmtree(out_image_dir)
                shutil.copytree(src_image_dir, out_image_dir)
                log('info', '拷贝站点图片目录', {'site': site_name, 'from': src_image_dir, 'to': out_image_dir})
            except OSError as e:
                log('warning', '拷贝站点图片目录失败', {'site': site_name, 'error': str(e)})

    site_duration_ms = round((time.time() - site_start_time) * 1000)
    log('info', '站点构建完成', {
        'site': site_name,
        'page_count': len(page_dirs),
        'compiled': compiled_count,
        'skipped': skipped_count,
        'errors': error_count,
        'duration_ms': site_duration_ms
    })

    return {
        'page_count': len(page_dirs),
        'compiled_count': compiled_count,
        'skipped_count': skipped_count,
        'error_count': error_count,
    }


def run_build(dry_run: bool = False, output_dir: str = None, clean: bool = False) -> dict:
    """主构建函数：扫描所有站点并构建"""
    start_time = time.time()
    
    # 清理模式：删除全部已有编译结果
    if clean and output_dir and not dry_run:
        if os.path.exists(output_dir):
            log('info', '清理模式：删除已有编译结果', {'output_dir': output_dir})
            try:
                shutil.rmtree(output_dir)
                log('info', '清理完成', {'output_dir': output_dir})
            except OSError as e:
                log('warning', '清理失败', {'output_dir': output_dir, 'error': str(e)})
    
    log('info', '========== 开始构建 ==========')

    sites = discover_sites()
    log('info', f'发现 {len(sites)} 个站点', {'sites': sites})

    total_pages = 0
    total_compiled = 0
    total_skipped = 0
    total_errors = 0

    with ThreadPoolExecutor(max_workers=min(len(sites), MAX_WORKERS)) as executor:
        futures = {executor.submit(build_site, site, dry_run, output_dir): site for site in sites}
        for future in as_completed(futures):
            result = future.result()
            total_pages += result['page_count']
            total_compiled += result['compiled_count']
            total_skipped += result['skipped_count']
            total_errors += result['error_count']

    duration_ms = round((time.time() - start_time) * 1000)
    log('info', '========== 构建完成 ==========', {
        'total_pages': total_pages,
        'total_compiled': total_compiled,
        'total_skipped': total_skipped,
        'total_errors': total_errors,
        'duration_ms': duration_ms,
    })

    return {
        'total_pages': total_pages,
        'total_compiled': total_compiled,
        'total_skipped': total_skipped,
        'total_errors': total_errors,
        'duration_ms': duration_ms,
    }


if __name__ == '__main__':
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(description='SiteHanger Build Service')
    parser.add_argument('--dry-run', action='store_true', help='仅预览，不实际写入')
    parser.add_argument('--clean', action='store_true', help='清理模式：删除全部已有编译结果后重新构建')
    parser.add_argument('--data-root', type=str, required=True, help='数据根目录路径')
    parser.add_argument('--output-dir', type=str, required=True, help='编译输出目录')
    args = parser.parse_args()

    DATA_ROOT = args.data_root
    BUILD_OUTPUT_DIR = args.output_dir

    # 校验：srcDir 和 outDir 不能相同
    if os.path.abspath(DATA_ROOT) == os.path.abspath(BUILD_OUTPUT_DIR):
        print('错误: --data-root 和 --output-dir 不能指向同一个目录', file=sys.stderr)
        sys.exit(1)

    log('info', '构建配置', {
        'data_root': DATA_ROOT,
        'build_output_dir': BUILD_OUTPUT_DIR,
        'mode': '输出到临时目录'
    })

    result = run_build(dry_run=args.dry_run, output_dir=BUILD_OUTPUT_DIR, clean=args.clean)

    print('\n📊 构建结果汇总:')
    print(f'   页面总数: {result["total_pages"]}')
    print(f'   重新编译: {result["total_compiled"]}')
    print(f'   跳过编译: {result["total_skipped"]}')
    print(f'   编译失败: {result["total_errors"]}')
    print(f'   总耗时: {result["duration_ms"]}ms')
    print(f'   并发线程: {MAX_WORKERS}')
