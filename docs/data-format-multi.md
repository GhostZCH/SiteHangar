# 数据格式规范 — 多 Markdown 格式（复杂模式）

本文档说明 SiteHanger 框架平台**多 Markdown 格式（复杂模式）**的数据规范，用于创建包含多个章节的知识页面。

## 适用场景

- 内容较长、需要分章节组织的知识页面
- 需要导航栏展示章节列表的页面
- 结构复杂、包含多种内容类型的页面

## 文件结构

```
article-slug/                  # 文章目录
├── meta.md                    # 文章元数据（YAML Frontmatter）
├── 01-chapter-title.md        # 第一章
├── 02-chapter-title.md        # 第二章
├── 03-chapter-title.md
└── ...
```

## 元数据文件（`meta.md`）

```yaml
---
title: 页面标题
description: 页面描述（SEO）
tags:
  - 标签1
  - 标签2
version: v1
introduction: 页面引言，显示在 hero 下方
---
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 页面标题 |
| `description` | string | 是 | SEO 描述 |
| `tags` | string[] | 否 | 标签列表 |
| `version` | string | 否 | 版本号，默认 `v1` |
| `introduction` | string | 否 | 页面引言 |

## 章节文件（`01-xxx.md`）

```markdown
---
title: 章节标题
subtitle: 章节副标题
---

# 子章节标题

正文内容...

## 1

分栏内容...
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 章节标题 |
| `subtitle` | string | 否 | 章节副标题 |

## 编译输出

编译后生成 `data.json`，结构如下：

```json
{
  "page": { "title": "...", "description": "..." },
  "hero": { "title": "...", "tags": [...] },
  "version": "v1",
  "lastModified": "2026-06-16 12:00:00",
  "introduction": "页面引言",
  "sections": [
    {
      "id": "章节ID",
      "title": "01 章节标题",
      "subtitle": "副标题",
      "type": "mixed",
      "content": { "description": ["..."] }
    }
  ]
}
```

## 相关文档

- [data-format-single.md](data-format-single.md) — 单 Markdown 格式（简单模式）
- [data-format.md](data-format.md) — 编译后 JSON 数据格式总览

**文档版本**：1.0
**最后更新**：2026-06-16
