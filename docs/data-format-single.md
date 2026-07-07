# 数据格式规范 — 单 Markdown 格式（简单模式）

本文档说明 SiteHanger 框架平台**单 Markdown 格式（简单模式）**的数据规范，用于创建简单的单文件知识页面。

## 适用场景

- 内容较短、无需分章节的知识页面
- 关于页、帮助页等简单信息页面
- 快速创建的单页内容

## 文件结构

```
article-slug/                  # 文章目录
└── page.md                    # 单文件（元数据 + 内容）
```

或用于 info 页面：

```
info/
└── page.md                    # 单文件关于页
```

## 文件格式（`page.md`）

```yaml
---
title: 页面标题
description: 页面描述（SEO）
tags:
  - 标签1
  - 标签2
version: v1
---

正文内容，支持标准 Markdown 语法。

可以包含多段文字、列表、引用等。
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 页面标题 |
| `description` | string | 是 | SEO 描述 |
| `tags` | string[] | 否 | 标签列表 |
| `version` | string | 否 | 版本号，默认 `v1` |

## 编译输出

编译后生成 `data.json`，结构如下：

```json
{
  "page": { "title": "...", "description": "..." },
  "hero": { "title": "...", "tags": [...] },
  "version": "v1",
  "lastModified": "2026-06-16 12:00:00",
  "introduction": "正文内容（Markdown body）",
  "sections": []
}
```

## 与多 Markdown 格式的区别

| 特性 | 单 Markdown 格式 | 多 Markdown 格式 |
|------|------------------|------------------|
| 文件数量 | 1 个（`page.md`） | 多个（`meta.md` + 章节文件） |
| 章节支持 | 无（`sections` 为空） | 有（多个章节） |
| 导航栏 | 不显示章节导航 | 显示章节导航 |
| 适用场景 | 简单单页 | 复杂多章节内容 |
| 元数据位置 | 文件头部 Frontmatter | 独立的 `meta.md` |

## 检测优先级

编译工具按以下优先级检测：

1. 如果存在 `meta.md` + `01-xxx.md` 章节文件 → **多 Markdown 格式**
2. 如果存在 `page.md` → **单 Markdown 格式**
3. 无 Markdown 文件 → 不需要编译

## 相关文档

- [data-format-multi.md](data-format-multi.md) — 多 Markdown 格式（复杂模式）
- [data-format.md](data-format.md) — 编译后 JSON 数据格式总览

**文档版本**：1.0
**最后更新**：2026-06-16
