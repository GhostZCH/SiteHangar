# EXMD 语法说明书

> 面向 AI 和开发者的扩展 Markdown 标记语言完整语法参考。

---

## 一、术语定义

| 术语 | 英文 | 定义 |
|------|------|------|
| **文章** | Article | 顶层文档，包含所有内容。一篇文章对应一个文件夹。 |
| **文章标题** | Article Title | 文章的主标题，显示在浏览器标签页和页面顶部。 |
| **文章引言** | Article Introduction | 文章开头的介绍性内容，显示在 Hero 区域下方。 |
| **文章副标题** | Article Subtitle | 文章的次要标题，提供额外上下文。 |
| **文章标签** | Article Tags | 与文章关联的分类标签，显示在 Hero 区域。 |
| **章节** | Chapter | 文章内的主要分区，包含相关内容。每个章节对应一个 `.md` 文件。 |
| **子标题** | Sub-heading | 章节内的细分标题，使用 Markdown 三级标题 `###` 实现。 |
| **二级子标题** | Sub-sub-heading | 子标题下的更小层级，使用 Markdown 四级标题 `####` 实现。 |
| **段落** | Paragraph | 子章节内的内容块，包含文本、图片、图表等。 |
| **分栏** | Column | 段落内的布局分割，使用 `===== / -----` 标记实现。 |

---

## 二、内容层级

```
Article（文章）
  ├── Article Title（文章标题）← 来自 frontmatter，忽略正文 #
  ├── Article Subtitle（文章副标题）
  ├── Article Introduction（文章引言）
  ├── Article Tags（文章标签）
  └── Chapters（多个章节）
        ├── Chapter 01
        │     ├── Chapter Title（章节标题）← 来自章节 frontmatter，忽略正文中 ##
        │     ├── Chapter Subtitle（章节副标题）
        │     └── Paragraphs（多个段落）
        │           ├── Text / Images / Charts / Tables
        │           ├── Sub-headings（###）
        │           ├── Sub-sub-headings（####）
        │           └── Columns（可选分栏）
        ├── Chapter 02
        └── ...
```

---

## 三、文件夹结构

```
article-slug/                  # 文章目录名：英文小写，连字符分隔
├── meta.md                    # 单文件模式：文章元信息（简单模式）
│ 或
├── page.md                    # 单文件模式：整篇文章内容（简单模式）
│ 或
├── meta.md                    # 多文件模式：文章元信息
├── 01-chapter-title.md        # 多文件模式：章节文件
├── 02-chapter-title.md
├── img/                       # 可选。图片目录
│   └── *.jpg / *.png / *.gif
└── data/                      # 可选。图表数据目录
    └── *.json
```

**目录名**：用于网站 URL，英文小写 + 连字符，如 `china-geography`、`tang-dynasty`。

**章节文件命名**：
```
<两位数字序号>-<章节标题>.md
```

- **`<两位数字序号>`**：01, 02, 03, ...，用于排序
- **`<章节标题>`**：章节的中文标题，不含序号

**示例**：
```
01-overview.md
02-landform.md
03-climate.md
04-hydrology.md
```

---

## 四、标题规范（重要）

为统一单文件模式和多文件模式，标题来源统一规定如下：

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

---

## 五、元数据文件

### 5.1 `meta.md` / `page.md` — 文章元信息

```markdown
---
title: 中国地理概览                              # 文章标题（浏览器标签页）
description: 中国地理概览 - SiteHanger 提供...      # SEO 描述
tags:                                           # 标签列表（hero 区域显示）
  - 地理
  - 百科
version: v1                                     # 版本号，默认 v1
introduction: 中国位于亚洲东部...                # 文章引言，显示在 hero 下方
subtitle: 亚洲东部的地理概况                    # 文章副标题
---
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | ✓ | 文章标题，显示在浏览器标签页和页面顶部 |
| `description` | string | ✓ | SEO 描述，用于搜索引擎优化 |
| `tags` | string[] | ✓ | 标签列表，显示在 hero 区域 |
| `version` | string | ✗ | 版本号，默认 `v1` |
| `introduction` | string | ✗ | 文章引言，显示在 hero 区域下方 |
| `subtitle` | string | ✗ | 文章副标题，提供额外上下文 |

---

## 六、章节文件

### 6.1 文件格式

每个章节文件以 YAML Frontmatter 开头，定义章节元信息，后跟 Markdown 内容。

```markdown
---
title: 概述
subtitle: 中国地理的总体概况
---

## 地理位置

中国位于亚洲东部、太平洋西岸...

### 地形特点

中国地势西高东低...
```

### 6.2 章节元信息（Frontmatter）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | ✓ | 章节标题 |
| `subtitle` | string | ✗ | 章节副标题 |

### 6.3 章节标题

- 章节标题只来自章节文件 frontmatter 的 `title` 字段。
- 正文中的 `## 标题` 在编译时会被忽略。
- 章节文件内部应只使用一个 `##` 作为章节标题占位（可选），实际以 frontmatter 为准。

---

## 七、分栏（Column）

分栏是一种**排版功能**，用于将内容在水平方向上并行排列。每个栏的内容可以完全不同，例如左边是文字说明，右边是配图或表格。

**分栏与卡片的区别**：
- **分栏**是排版方式，只是位置上并行，每个栏可以内容不统一（如左边文字右边配图）
- **卡片**是可视化控件，用于展示多个相同实体的结构化信息（如多个湖泊的信息卡片）

使用 `=====`` 和 `-----` 标记分栏区域：

```markdown
## 统计数据

=====

左侧文字说明内容...

-----

右侧表格或配图...

=====
```

**分栏规则**：
- `=====`` 开始分栏区域；第二个 `=====`` 结束分栏区域。
- `-----` 分隔两个相邻分栏。
- 严格使用 5 个字符（`=====`` / `-----`），不得增减。
- 分栏标记前后允许空行。
- 最多支持 4 栏。
- 分栏不能嵌套。
- 分栏内支持：文本段落、Markdown 表格、列表、图表、标题等所有内容控件。

**分栏数量示例**：
- 两个 `=====`` 中间无 `-----`：1 栏
- 两个 `=====`` 中间一个 `-----`：2 栏
- 两个 `=====`` 中间两个 `-----`：3 栏
- 两个 `=====`` 中间三个 `-----`：4 栏

---

## 八、内容类型

内容类型分为两大类：**可视化控件**（用于展示特定数据）和 **排版功能**（用于控制布局）。

### 可视化控件

| 控件 | 说明 | 数据特点 |
|------|------|----------|
| `stats` | 统计卡片 | 展示关键数值指标 |
| `cards` | 卡片列表 | **多个相同实体的展示**，如湖泊列表、山峰列表 |
| `tables` | 表格 | 标准 Markdown 表格，展示行列数据 |
| `charts` | 图表 | 柱状图、饼图、折线图、中国地图 |
| `timeline` | 时间线 | 展示历史事件时间轴 |
| `branchVisualizer` | 分支发展可视化 | 展示多分支在不同历史时期的发展变化 |
| `chips` | 标签芯片 | 展示标签集合 |
| `list` | 列表 | 带图标的有序/无序列表 |

### 排版功能

| 功能 | 说明 | 特点 |
|------|------|------|
| `分栏（columns）` | 多栏并行排版 | **只是位置上并行**，每个栏内容可以不统一 |
| `段落文本` | 标准 Markdown 段落 | 连续非空行自动合并 |

### 两种数据提供方式

EXMD 的可视化控件支持两种方式来提供数据：

**方式一：JSON 文件引用（适合大量数据）**
```markdown
![stats](data/area-stats.json)
```

**方式二：Markdown Code 块（适合少量人工编写数据）**
```markdown
```stats
[
  { "value": "960万", "label": "陆地面积（平方公里）" },
  { "value": "1.8万", "label": "大陆海岸线（公里）" }
]
```
```

Code 块支持的类型：`stats`、`cards`、`timeline`、`branches`、`chips`、`bar`、`pie`、`line`、`china-map`。

---

## 九、段落文本与内联格式

标准 Markdown 段落，连续非空行自动合并为一个 `<p>`。

```markdown
这是第一段文字。

这是第二段文字，中间用空行分隔。
```

内联格式：

```markdown
**加粗文本**
*斜体文本*
`行内代码`
[链接文字](https://example.com)
$E=mc^2$                # 行内公式
```

---

## 十、列表与引用

```markdown
- 无序列表项 1
- 无序列表项 2

1. 有序列表项 1
2. 有序列表项 2

> 这是一段引用文字。
```

---

## 十一、块级公式（LaTeX）

```markdown
$$
E = mc^2
$$
```

---

## 十二、统计卡片

### 语法

```markdown
![stats](data/<文件>.json)
```

### 数据文件格式

```json
[
  { "value": "960万", "label": "陆地面积（平方公里）" },
  { "value": "1.8万", "label": "大陆海岸线（公里）" },
  { "value": "34", "label": "省级行政区（个）" },
  { "value": "14.08亿", "label": "总人口（2024年）" }
]
```

---

## 十三、表格

使用标准 Markdown 表格语法。

```markdown
| 河流名称 | 长度（公里） | 流域面积（万平方公里） | 注入海洋 |
|---------|------------|---------------------|---------|
| 长江    | 6300       | 180                 | 东海    |
| 黄河    | 5464       | 75                  | 渤海    |
```

---

## 十四、图表

图表复用 Markdown 图片链接语法：`![<类型>](data/<文件>.json)`

### 类型对照

| alt 文本 | 图表类型 | ECharts 类型 |
|----------|----------|-------------|
| `bar` | 柱状图 | bar |
| `pie` | 饼图（donut） | pie |
| `line` | 折线图 | line |
| `china-map` | 中国地图 | map |

---

## 十五、图片

```markdown
![描述文字](img/photo-a.jpg)
```

- 图片放在当前文章目录下的 `img/` 文件夹中
- 使用相对路径 `img/xxx.jpg` 引用
- 支持格式：`.jpg`、`.jpeg`、`.png`、`.gif`、`.webp`、`.svg`

---

## 十六、卡片列表、时间线、分支发展可视化、标签芯片

语法与之前一致，详见数据格式文档。

---

## 十七、完整示例

### 多文件模式示例

#### 目录结构

```
china-geography/
├── meta.md
├── 01-overview.md
├── 02-landform.md
├── 03-climate.md
├── img/
│   └── china-topo.jpg
└── data/
    ├── altitude.json
    └── climate-pie.json
```

#### `meta.md`

```markdown
---
title: 中国地理概览
description: 中国地理概览 - SiteHanger 提供中国自然地理、人文地理、经济地理与区域地理的系统介绍
tags:
  - 地理
  - 百科
version: v1
introduction: 中国位于亚洲东部、太平洋西岸。从青藏高原的巍峨雪峰到东海之滨的辽阔平原，中国大地蕴藏着极其丰富多样的自然景观。
subtitle: 亚洲东部的地理概况
---
```

#### `01-overview.md`

```markdown
---
title: 概述
subtitle: 中国地理的总体概况
---

## 地理位置

中国位于亚洲东部、太平洋西岸，陆地面积约960万平方公里，仅次于俄罗斯和加拿大，居世界第三位。

### 地理特征

中国地理的总体特征可以概括为：**地势西高东低呈三级阶梯分布**。

![stats](data/area-stats.json)
```

#### `02-landform.md`

```markdown
---
title: 地貌格局
subtitle: 中国地形地势特征
---

## 三级阶梯

中国地势西高东低，呈三级阶梯分布：

=====

第一级阶梯是青藏高原，平均海拔4000米以上，面积约250万平方公里，被称为"世界屋脊"。

-----

第二级阶梯平均海拔1000-2000米，分布着内蒙古高原、黄土高原、云贵高原和塔里木盆地、准噶尔盆地、四川盆地。

-----

第三级阶梯海拔多在500米以下，分布着东北平原、华北平原和长江中下游平原。

=====
```

---

## 十八、规范约束汇总

| # | 约束 | 说明 |
|---|------|------|
| 1 | 禁止 Emoji | 所有文本内容不得使用 Emoji 表情符号 |
| 2 | 标题来源 | 页面标题、章节标题只来自 frontmatter |
| 3 | 标题层级 | `##` 为章节标题（单文件）或占位（多文件），`###` 为子标题，`####` 为二级子标题 |
| 4 | 禁止五级标题 | 不支持 `#####` 及以下，使用多级列表代替 |
| 5 | 分栏语法 | 使用 `=====`` 和 `-----`，严格 5 个字符 |
| 6 | 分栏上限 | 最多 4 栏 |
| 7 | 分栏内支持 | 文本、表格、列表、图表、标题等所有控件 |
| 8 | 目录名 | 英文小写 + 连字符 |
| 9 | 章节文件名 | `<两位数字>-<标题>.md` |
| 10 | 数据文件路径 | 必须以 `data/` 开头 |
| 11 | 图片路径 | 必须以 `img/` 开头 |
| 12 | 章节序号 | 两位数字，01-99 |

---

## 十九、build_service.py 转换映射

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
| `![bar](data/x.json)` | `content.charts[{type: "bar", ...}]` |
| `![pie](data/x.json)` | `content.charts[{type: "pie", ...}]` |
| `![line](data/x.json)` | `content.charts[{type: "line", ...}]` |
| `![china-map](data/x.json)` | `content.charts[{type: "chinaMap", ...}]` |
| `![image](image/x.jpg)` | `image` 字段（URL 引用） |
| `![cards](data/x.json)` | `content.cards[]` |
| `![timeline](data/x.json)` | `content.timeline` |
| `![branches](data/x.json)` | `content.branchVisualizer` |
| `![chips](data/x.json)` | `content.chips[]` |
| LaTeX `$$...$$` | 原样保留，渲染时由 KaTeX 处理 |

---

## 二十、版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-06-09 | 初始版本 |
| v2.0 | 2026-06-10 | 重构为章节文件结构，新增分栏、分支可视化 |
| v3.0 | 2026-07-05 | 统一标题来源，分栏语法改为 `===== / -----`，支持 `####` 二级子标题 |

---

## 二十一、与 JSON 数据格式的关系

KMD v3 是面向内容创作者的**源格式**，通过 `build_service.py` 转换为项目统一的 **JSON 数据格式**（详见 `data-format.md`）。

| 特性 | KMD v3（源格式） | JSON（目标格式） |
|------|------------------|------------------|
| 面向对象 | AI / 内容创作者 | 前端渲染引擎 |
| 可读性 | 高（Markdown） | 低（机器格式） |
| 文件组织 | 多文件（章节拆分） | 单文件（`data.json`） |
| 图片处理 | 引用外部文件 | URL 引用 |
| 构建步骤 | 需要 `build_service.py` 转换 | 直接读取 |

**工作流程**：
1. 创作者用 KMD v3 编写内容（`meta.md` / `page.md` + `.md` 章节文件）
2. 运行 `build_service.py` 转换为 `data.json`
3. 后端读取 `data.json` 提供给前端渲染

**相关文档**：
- [data-format.md](data-format.md) — JSON 数据格式详细规范
- [project-structure.md](project-structure.md) — 代码结构和构建工具说明
