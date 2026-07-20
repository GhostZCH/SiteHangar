#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_index.py - 索引生成模块

职责：为站点生成统一的 index.json 索引文件。
- 读取站点根目录 meta.yaml 合并元数据到索引
- 扫描所有栏目页面生成 columns 数据（含 recent / categories）
- 支持多级分类结构（含 subCategories）

对外接口：
  build_site_index(site_path, site_name, column_pages) -> dict
  extract_page_info(data_json_path, route_path) -> dict
  extract_page_info_from_data(data, route_path) -> dict
"""

import os
from build_utils import read_json, read_meta, format_datetime, log, strip_order_prefix


def extract_page_info(data_json_path: str, route_path: str) -> dict:
    """从 data.json 文件中提取页面信息（用于生成索引）"""
    data = read_json(data_json_path)
    if not data:
        return None
    return extract_page_info_from_data(data, route_path)


def extract_page_info_from_data(data: dict, route_path: str) -> dict:
    """从已编译的 data 字典中提取页面信息"""
    if not data:
        return None

    hero = data.get('hero', {})
    page = data.get('page', {})

    desc = data.get('introduction', '')
    if not desc and data.get('sections'):
        first_section = data['sections'][0]
        content = first_section.get('content', {})
        descriptions = content.get('description', [])
        if descriptions:
            desc = descriptions[0]

    return {
        'title': hero.get('title', page.get('title', '')),
        'subtitle': hero.get('subtitle', ''),
        'desc': desc,
        'link': route_path,
        'lastModified': data.get('lastModified', ''),
    }


def _build_categories_from_meta(categories: list, column_dir: str, site_path: str, sorted_pages: list) -> list:
    """根据 meta.yaml 的 categories 配置，扫描目录结构自动生成 links。
    分类和子分类名称从目录名自动获取，不再依赖 meta.yaml 中的 name 字段。
    强制所有分类都有 subCategories 结构。"""
    result = []
    data_root = os.path.dirname(site_path)

    for cat in categories:
        cat_slug = cat.get('slug', cat.get('id', ''))
        # 如果 meta 中没有 name，使用 slug（目录名）作为名称，并去掉序号前缀
        cat_name = cat.get('name', strip_order_prefix(cat_slug))
        sub_categories = cat.get('subCategories', [])

        if sub_categories:
            # 有 subCategories 的，按原有逻辑处理
            sub_result = []
            for sub in sub_categories:
                sub_slug = sub.get('slug', sub.get('id', ''))
                # 如果 meta 中没有 name，使用 slug（目录名）作为名称，并去掉序号前缀
                sub_name = sub.get('name', strip_order_prefix(sub_slug))
                links = _scan_subcategory_pages(column_dir, cat_slug, sub_slug, data_root)
                sub_result.append({
                    'name': sub_name,
                    'links': links,
                })
            result.append({
                'name': cat_name,
                'subCategories': sub_result,
            })
        else:
            # 没有 subCategories 的，将当前分类本身作为唯一的 subCategory
            # 收集该分类下的页面链接
            if cat_slug == 'all' or cat_slug == '全部':
                # "全部"分类：收集所有页面
                links = []
                for p in sorted_pages:
                    links.append({
                        'title': p['title'],
                        'url': p['link'],
                    })
                result.append({
                    'name': cat_name or '全部',
                    'subCategories': [{
                        'name': '全部',
                        'links': links,
                    }],
                })
            else:
                # 其他分类：扫描该分类目录下的页面
                links = _scan_category_pages(column_dir, cat_slug, data_root)
                result.append({
                    'name': cat_name,
                    'subCategories': [{
                        'name': cat_name,
                        'links': links,
                    }],
                })

    return result


def _build_categories_from_dirs(column_dir: str, data_root: str, sorted_pages: list) -> list:
    """根据目录结构自动生成分类和子分类。
    扫描 column_dir 下的子目录结构：
    - 如果子目录下还有子目录（且包含页面），则作为 category，其子目录作为 subCategory
    - 如果子目录下直接是页面（无更深子目录），则作为 category，自身作为唯一的 subCategory
    - 如果没有子目录，生成默认的 "全部" 分类
    - 跳过空目录（没有子目录也没有页面的目录）
    """
    result = []

    # 扫描 column_dir 下的直接子目录（这些就是分类）
    cat_dirs = []
    try:
        for entry in sorted(os.scandir(column_dir), key=lambda e: e.name):
            if entry.is_dir() and not entry.name.startswith('.'):
                cat_dirs.append(entry)
    except OSError:
        pass

    if not cat_dirs:
        # 没有子目录，生成默认的 "全部" 分类
        links = []
        for p in sorted_pages:
            links.append({
                'title': p['title'],
                'url': p['link'],
            })
        return [{
            'name': '全部',
            'subCategories': [{
                'name': '全部',
                'links': links,
            }],
        }]

    for cat_entry in cat_dirs:
        cat_name = strip_order_prefix(cat_entry.name)
        cat_dir = cat_entry.path

        # 扫描分类目录下的子目录（这些就是子分类）
        sub_dirs = []
        try:
            for sub_entry in sorted(os.scandir(cat_dir), key=lambda e: e.name):
                if sub_entry.is_dir() and not sub_entry.name.startswith('.'):
                    sub_dirs.append(sub_entry)
        except OSError:
            pass

        if not sub_dirs:
            # 分类下没有子目录，检查是否有页面
            links = _scan_category_pages(column_dir, cat_entry.name, data_root)
            if links:
                result.append({
                    'name': cat_name,
                    'subCategories': [{
                        'name': cat_name,
                        'links': links,
                    }],
                })
        else:
            # 检查子目录是否直接包含 data.json（3层结构：column -> category -> page）
            # 如果子目录包含 data.json，说明是页面，不是子分类
            has_direct_pages = any(
                os.path.exists(os.path.join(sub_entry.path, 'data.json'))
                for sub_entry in sub_dirs
            )
            
            if has_direct_pages:
                # 3层结构：子目录是页面，直接扫描
                links = _scan_category_pages(column_dir, cat_entry.name, data_root)
                if links:
                    result.append({
                        'name': cat_name,
                        'subCategories': [{
                            'name': cat_name,
                            'links': links,
                        }],
                    })
            else:
                # 4层结构：子目录是子分类，扫描子分类下的页面
                sub_result = []
                for sub_entry in sub_dirs:
                    sub_name = strip_order_prefix(sub_entry.name)
                    links = _scan_subcategory_pages(column_dir, cat_entry.name, sub_entry.name, data_root)
                    if links:
                        sub_result.append({
                            'name': sub_name,
                            'links': links,
                        })
                if sub_result:
                    result.append({
                        'name': cat_name,
                        'subCategories': sub_result,
                    })

    return result


def _extract_title_and_url(data: dict, url: str, fallback_name: str) -> dict:
    """从 data.json 数据中提取标题并生成链接项"""
    hero = data.get('hero', {})
    page = data.get('page', {})
    title = hero.get('title', page.get('title', fallback_name))
    return {'title': title, 'url': url}


def _calc_url_prefix(column_dir: str, data_root: str) -> str:
    """计算页面链接的 URL 前缀（栏目相对路径，如 /wiki）"""
    rel = os.path.relpath(column_dir, data_root).replace('\\', '/')
    parts = rel.split('/', 1)
    return '/' + parts[1] if len(parts) > 1 else ''


def _collect_page_links(root_dir: str, url_base: str, recursive: bool) -> list:
    """扫描 root_dir 下的页面目录，读取 data.json 生成链接列表。
    url_base: 链接的 URL 前缀（不含末尾目录名）
    recursive: 是否递归扫描更深层级
    """
    if not os.path.isdir(root_dir):
        return []

    links = []

    def _scan(current_dir: str, rel_path: str):
        try:
            for entry in sorted(os.scandir(current_dir), key=lambda e: e.name):
                if not entry.is_dir() or entry.name.startswith('.'):
                    continue
                data_json_path = os.path.join(entry.path, 'data.json')
                if os.path.exists(data_json_path):
                    data = read_json(data_json_path)
                    if data:
                        url = f'{url_base}/{rel_path}{entry.name}'
                        links.append(_extract_title_and_url(data, url, entry.name))
                if recursive:
                    _scan(entry.path, f'{rel_path}{entry.name}/')
        except OSError:
            pass

    _scan(root_dir, '')
    return links


def _scan_subcategory_pages(column_dir: str, cat_slug: str, sub_slug: str, data_root: str) -> list:
    """扫描 column_dir/<cat_slug>/<sub_slug>/ 下的所有页面（递归），生成链接列表"""
    url_prefix = _calc_url_prefix(column_dir, data_root)
    url_base = f'{url_prefix}/{cat_slug}/{sub_slug}'
    sub_dir = os.path.join(column_dir, cat_slug, sub_slug)
    return _collect_page_links(sub_dir, url_base, recursive=True)


def _scan_category_pages(column_dir: str, cat_slug: str, data_root: str) -> list:
    """扫描 column_dir/<cat_slug>/ 下的页面（不递归），生成链接列表"""
    url_prefix = _calc_url_prefix(column_dir, data_root)
    url_base = f'{url_prefix}/{cat_slug}'
    cat_dir = os.path.join(column_dir, cat_slug)
    return _collect_page_links(cat_dir, url_base, recursive=False)


def _build_column_index(column_slug: str, column_meta: dict, column_dir: str,
                        site_path: str, page_infos: list, output_dir: str = None) -> dict:
    """
    为单个栏目生成索引数据。
    从栏目 meta 配置和页面信息生成 recent / categories。
    强制 categories 都有 subCategories 结构。
    """
    # 按 lastModified 倒序排列
    sorted_pages = sorted(page_infos, key=lambda x: x.get('lastModified', ''), reverse=True)

    # 最近更新列表（取前 8 个）
    recent = []
    for p in sorted_pages[:8]:
        recent.append({
            'title': p['title'],
            'subtitle': p.get('subtitle', ''),
            'desc': p.get('desc', ''),
            'link': p['link'],
        })

    # 处理 categories
    # URL 前缀基于 column_dir 的父级目录计算：有编译输出时用 output_dir，否则用站点目录
    data_root = output_dir if output_dir else site_path

    categories = column_meta.get('categories')
    if categories:
        categories = _build_categories_from_meta(categories, column_dir, data_root, sorted_pages)
    else:
        # 没有 categories 配置时，根据目录结构自动生成
        categories = _build_categories_from_dirs(column_dir, data_root, sorted_pages)

    now = format_datetime()

    return {
        'page': column_meta.get('page', {
            'title': column_meta.get('title', strip_order_prefix(column_slug)),
            'description': column_meta.get('description', f'{strip_order_prefix(column_slug)} - SiteHangar'),
        }),
        'hero': column_meta.get('hero', {
            'title': column_meta.get('title', strip_order_prefix(column_slug)),
            'tags': column_meta.get('tags', []),
        }),
        'version': column_meta.get('version', 'v1'),
        'lastModified': now,
        'generatedAt': now,
        'recent': recent,
        'categories': categories,
    }


def build_site_index(site_path: str, site_name: str, column_pages: dict, output_dir: str = None) -> dict:
    """
    构建站点统一的 index.json。
    合并站点根目录 meta.yaml 中的 page、hero、modules 等配置，
    并为每个栏目生成完整的索引数据（recent / categories）。

    column_pages: dict, key 为栏目 slug, value 为该栏目下的页面信息列表
    output_dir: 编译输出目录，categories 扫描时从输出目录读取 data.json
    """
    site_meta = read_meta(site_path)
    now = format_datetime()

    # 1. 构建站点首页基础数据
    page = site_meta.get('page', {})
    root_index = {
        'page': {
            'title': page.get('title', site_name),
            'description': page.get('description', f'{site_name} - SiteHangar'),
        },
        'hero': {
            'title': page.get('title', site_name),
            'brand_name': page.get('brand_name', ''),
            'subtitle': page.get('subtitle', ''),
            'tags': page.get('tags', []),
        },
        'version': site_meta.get('version', 'v1'),
        'lastModified': site_meta.get('lastModified', now),
        'generatedAt': now,
    }

    # 2. 处理 modules 配置
    if site_meta.get('modules'):
        modules = []
        for m in site_meta['modules']:
            module = dict(m)
            code = m.get('id', '')
            if 'link' not in module:
                module['link'] = f'/{code}' if code else ''
            img = m.get('image', '')
            if img and not img.startswith('/'):
                module['image'] = f'/api/image/{site_name}/{img}'
            modules.append(module)
        root_index['modules'] = modules

    # 3. 合并其他顶层字段（兼容旧结构）
    for key in ['subtitle', 'introduction', 'description', 'image', 'banner']:
        if key in site_meta and key not in root_index:
            root_index[key] = site_meta[key]

    # 4. 为每个栏目生成索引数据
    columns_index = {}

    for column_slug, page_infos in column_pages.items():
        # 新结构：从 modules 中查找栏目配置
        column_meta = {}
        for m in site_meta.get('modules', []):
            if m.get('id') == column_slug:
                column_meta = m
                break
        # 优先使用输出目录的栏目路径（供 categories 扫描 data.json）
        if output_dir:
            column_dir = os.path.join(output_dir, site_name, column_slug)
        else:
            column_dir = os.path.join(site_path, column_slug)
        columns_index[column_slug] = _build_column_index(
            column_slug, column_meta, column_dir, site_path, page_infos, output_dir=output_dir
        )

    if columns_index:
        root_index['columns'] = columns_index

    return root_index
