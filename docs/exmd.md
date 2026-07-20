# EXMD 格式说明

EXMD（Extended Markdown）是 SiteHangar 面向内容创作者的源格式。它在标准 Markdown 基础上扩展了可视化控件、分栏排版、单/多文档模式等能力，由 `build_service.py` 编译为统一的 JSON 数据，供前端渲染。

## 内容层级

```
Article（文章）
  ├── Article Title（文章标题）← 来自 frontmatter，忽略正文 #
  ├── Article Subtitle（文章副标题）
  ├── Article Introduction（文章引言）
  ├── Article Tags（文章标签）
  └── Chapters（多个章节）
        ├── Chapter 01
        │     ├── Chapter Title（章节标题）← 来自章节 frontmatter，忽略正文 ##
        │     ├── Chapter Subtitle（章节副标题）
        │     └── Paragraphs（多个段落）
        │           ├── Text / Images / Charts / Tables
        │           ├── Sub-headings（###）
        │           ├── Sub-sub-headings（####）
        │           └── Columns（可选分栏）
        ├── Chapter 02
        └── ...
```

## 标题规范

| 标题层级 | 来源 | Markdown 写法 | 最终 HTML | 说明 |
|----------|------|---------------|-----------|------|
| 文章标题 | `meta.md` / `page.md` 的 frontmatter `title` | 无 | `<h1>` | 只认 frontmatter，忽略正文 `#` |
| 章节标题 | 多文件章节文件 frontmatter `title` | 无 | `<h2>` | 只认 frontmatter，忽略正文 `##` |
| 章节标题 | 单文件 `page.md` frontmatter `title` | `## 标题` | `<h2>` | 二级标题作为 section 拆分 |
| 子标题 | 正文 | `### 标题` | `<h3>` | 不建议超过三级标题 |
| 二级子标题 | 正文 | `#### 标题` | `<h4>` | 支持但建议少用 |

**关键约束**：
- 文章标题只来自 frontmatter，正文 `# 标题` 被忽略。
- 多文件模式下，章节标题只来自章节文件 frontmatter，正文 `## 标题` 被忽略。
- 单文件模式下，正文 `## 标题` 作为章节标题拆分 section。
- 正文中的 `###` 和 `####` 作为子标题和二级子标题。
- 不推荐使用 `#####` 及以下标题，建议使用多级列表代替。

## 两种文档模式

### 单 Markdown 模式（简单模式）

适用于内容较短、无需分章节的页面，例如关于页、帮助页、快速单页。

**文件结构**：

```
article-slug/
└── page.md              # 单文件：元数据 + 内容
```

或用于关于页：

```
info/
└── page.md
```

**示例 `page.md`**：

```markdown
---
title: 关于本站
description: 关于 SiteHangar 的介绍
tags:
  - 关于
version: v1
---

本站基于 SiteHangar 构建，使用 Markdown 管理内容，编译为 JSON 后动态渲染。

## 特点

- 数据与展示分离
- 多站点支持
- 无需数据库
```

**编译输出**：生成 `data.json`。正文按 `## 标题` 拆分为 `sections`；若全文没有 `## 标题`，则当正文含结构化内容（表格、卡片等）时包装为一个默认 section（标题为"内容"），否则整段正文放入 `introduction`、`sections` 为空。

### 多 Markdown 模式（复杂模式）

适用于内容较长、需要分章节组织的页面，支持导航栏、分栏、图表等高级控件。

**文件结构**：

```
article-slug/
├── meta.md                    # 文章元数据
├── 01-chapter-title.md        # 第一章
├── 02-chapter-title.md
├── 03-chapter-title.md
├── image/                     # 页面级图片（可选）
│   └── photo.jpg
└── data/                      # 图表数据文件（可选）
    └── chart.json
```

**目录名**：用于 URL，英文小写 + 连字符，如 `china-geography`、`tang-dynasty`。

**章节文件命名**：`<两位数字序号>-<章节标题>.md`，例如 `01-overview.md`、`02-landform.md`。

**示例 `meta.md`**：

```markdown
---
title: 中国地理概览
description: 中国地理概览 - SiteHangar 提供中国自然地理、人文地理的系统介绍
tags:
  - 地理
  - 百科
version: v1
introduction: 中国位于亚洲东部、太平洋西岸...
subtitle: 亚洲东部的地理概况
---
```

**示例章节文件 `01-overview.md`**：

```markdown
---
title: 概述
subtitle: 中国地理的总体概况
---

## 地理位置

中国位于亚洲东部、太平洋西岸，陆地面积约960万平方公里...

### 地理特征

中国地理的总体特征可以概括为：**地势西高东低呈三级阶梯分布**。

![stats](data/area-stats.json)
```

### 模式检测优先级

编译工具按以下顺序检测：

1. 如果存在 `meta.md` + `01-xxx.md` 章节文件 → **多 Markdown 模式**
2. 如果存在 `page.md` → **单 Markdown 模式**
3. 无 Markdown 文件 → 不需要编译

## 元数据字段

### 文章元数据（`meta.md` / `page.md`）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 文章标题，显示在浏览器标签页和页面顶部 |
| `description` | string | 是 | SEO 描述 |
| `tags` | string[] | 是 | 标签列表，显示在 hero 区域 |
| `version` | string | 否 | 版本号，默认 `v1` |
| `introduction` | string | 否 | 文章引言，显示在 hero 区域下方 |
| `subtitle` | string | 否 | 文章副标题 |

### 章节元数据（`01-xxx.md`）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 章节标题 |
| `subtitle` | string | 否 | 章节副标题 |

## 内容控件

### 可视化控件

| 控件 | 说明 | 语法示例 |
|------|------|----------|
| `stats` | 统计卡片 | `![stats](data/area-stats.json)` |
| `cards` | 卡片列表 | `![cards](data/lakes.json)` |
| `tables` | 表格 | 标准 Markdown 表格 |
| `charts` | 图表 | `![bar](data/chart.json)`、`![pie](data/chart.json)`、`![line](data/chart.json)`、`![china-map](data/map.json)` |
| `timeline` | 时间线 | `![timeline](data/history.json)` |
| `branchVisualizer` | 分支发展可视化 | `![branches](data/evolution.json)` |
| `chips` | 标签芯片 | `![chips](data/tags.json)` |
| `list` | 带图标列表 | Markdown 列表配合 `|` 分隔符 |

### 排版功能

| 功能 | 说明 | 语法 |
|------|------|------|
| 段落文本 | 标准 Markdown 段落 | 连续非空行 |
| 分栏 | 多栏并行布局 | `===== ... ----- ... =====` |

### 数据提供方式

可视化控件支持两种数据提供方式：

**方式一：JSON 文件引用（适合大量数据）**

```markdown
![stats](data/area-stats.json)
```

**方式二：Markdown Code 块（适合少量人工数据）**

```markdown
```stats
[
  { "value": "960万", "label": "陆地面积（平方公里）" },
  { "value": "1.8万", "label": "大陆海岸线（公里）" }
]
```
```

Code 块支持的类型：`stats`、`cards`、`timeline`、`branches`、`chips`、`bar`、`pie`、`line`、`china-map`。

## 分栏

分栏用于将内容在水平方向上并行排列，每个栏的内容可以完全不同。

**分栏与卡片的区别**：
- **分栏**是排版方式，只是位置上并行，每个栏可以内容不统一（如左边文字右边配图）。
- **卡片**是可视化控件，用于展示多个相同实体的结构化信息（如多个湖泊的信息卡片）。

**语法**：

```markdown
=====

左侧文字说明内容...

-----

右侧表格或配图...

=====
```

**规则**：
- `=====` 开始分栏区域；第二个 `=====` 结束分栏区域。
- `-----` 分隔两个相邻分栏。
- 严格使用 5 个字符，不得增减。
- 分栏标记前后允许空行。
- 最多支持 4 栏，不能嵌套。
- 分栏内支持：文本段落、Markdown 表格、列表、图表、标题等所有控件。

## 图片

```markdown
![描述文字](image/photo-a.jpg)
```

- 图片放在当前文章目录下的 `image/` 文件夹中。
- 使用相对路径 `image/xxx.jpg` 引用。
- 支持格式：`.jpg`、`.jpeg`、`.png`、`.gif`、`.webp`、`.svg`。

站点级封面图放在 `data/<site>/image/`，在 `meta.yaml` 中引用文件名，构建脚本会自动转换为 `/api/image/<site>/<filename>`。

## 标准 Markdown 支持

- 加粗：`**文本**`
- 斜体：`*文本*`
- 行内代码：`` `code` ``
- 链接：`[文字](https://example.com)`
- 无序列表：`- 项目`
- 有序列表：`1. 项目`
- 引用：`> 引用文字`
- 块级公式：`$$E = mc^2$$`

## 转换映射

`build_service.py` 将 EXMD 转换为 JSON 的对应关系：

| 源 | 目标 JSON 路径 |
|----|---------------|
| `meta.md` / `page.md` → `title`, `description`, `tags` | `page.title`, `page.description`, `hero.tags` |
| `meta.md` / `page.md` → `version`, `introduction`, `subtitle` | `version`, `introduction`, `hero.subtitle` |
| 章节文件 frontmatter `title` | `sections[n].title` |
| 章节文件 frontmatter `subtitle` | `sections[n].subtitle` |
| 单文件 `page.md` → `## 标题` | `sections[n].title` |
| 正文 `### 标题` | `sections[n].content.description[]`（渲染为 h3） |
| 正文 `#### 标题` | `sections[n].content.description[]`（渲染为 h4） |
| 分栏 `===== / -----` | `sections[n].content.columns[]` |
| Markdown 段落 | `content.description[]` |
| `![stats](data/x.json)` | `content.stats[]` |
| Markdown 表格 | `content.tables[]` |
| `![bar](data/x.json)` | `content.charts[{type: "bar"}]` |
| `![pie](data/x.json)` | `content.charts[{type: "pie"}]` |
| `![line](data/x.json)` | `content.charts[{type: "line"}]` |
| `![china-map](data/x.json)` | `content.charts[{type: "chinaMap"}]` |
| `![cards](data/x.json)` | `content.cards[]` |
| `![timeline](data/x.json)` | `content.timeline` |
| `![branches](data/x.json)` | `content.branchVisualizer` |
| `![chips](data/x.json)` | `content.chips[]` |

## 规范约束

| # | 约束 | 说明 |
|---|------|------|
| 1 | 禁止 Emoji | 所有文本内容不得使用 Emoji 表情符号 |
| 2 | 标题来源 | 页面标题、章节标题只来自 frontmatter |
| 3 | 标题层级 | `##` 为章节标题（单文件）或占位（多文件），`###` 为子标题，`####` 为二级子标题 |
| 4 | 禁止五级标题 | 不支持 `#####` 及以下，使用多级列表代替 |
| 5 | 分栏语法 | 使用 `===== / -----`，严格 5 个字符 |
| 6 | 分栏上限 | 最多 4 栏 |
| 7 | 目录名 | 英文小写 + 连字符 |
| 8 | 章节文件名 | `<两位数字>-<标题>.md` |
| 9 | 数据文件路径 | 必须以 `data/` 开头 |
| 10 | 图片路径 | 页面级图片以 `image/` 开头，站点级图片只写文件名 |

**文档版本**：1.0
**最后更新**：2026-07-07
