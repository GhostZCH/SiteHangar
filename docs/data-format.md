# 数据格式规范

本文档详细说明 SiteHanger 平台的数据格式规范，用于创建和维护知识页面。

## 数据文件类型

### 知识详情页 (`data.json`)

**用途**：用于展示具体知识内容的页面（如 `/wiki/xxx`）

**文件位置**：`my_sites_data/<site>/<path>/data.json`

**支持的内容类型**：文本段落、统计卡片、表格、卡片列表、图表（柱状图、饼图、地图）、时间线、分支发展可视化、列表、标签芯片

**数据来源**：
- **方式一（推荐）**：使用 EXMD 格式编写内容，通过 `build.py` 转换生成 `data.json`（详见 [exmd-spec.md](exmd-spec.md)）
- **方式二（兼容）**：直接手工维护 `data.json`

### 二级分类页 (`index.json`)

**用途**：展示某一模块下的最近更新和全部分类列表（如 `/wiki`）

**文件位置**：`my_sites_data/<site>/<module>/index.json`

**支持的内容**：最近更新列表、分类索引（多级分类）

**生成方式**：
- **方式一（推荐）**：在模块目录下创建 `meta.yaml` 配置文件，运行构建脚本自动生成 `index.json`
  - `meta.yaml` 包含 `page`、`hero`、`categories` 等配置
  - `recent` 列表由构建脚本通过扫描子目录的 `data.json` 自动生成
- **方式二（兼容）**：直接手工维护 `index.json`

### 关于页 (`info.json`)

**用途**：展示站点关于/帮助信息（如 `/info`）

**文件位置**：`my_sites_data/<site>/info.json`

**生成方式**：
- **方式一（推荐）**：在 `my_sites_data/<site>/info/` 文件夹中放置 Markdown 文件，运行构建脚本自动生成 `info.json`
  - 复杂模式：`data.md`（元数据）+ `01-xxx.md`、`02-xxx.md`（章节文件）
  - 简单模式：`single.md`（单文件）
- **方式二（兼容）**：直接在站点根目录手工维护 `info.json`

**优先级**：构建脚本优先检测 `info/` 文件夹，如果存在则编译生成 `info.json`；后端读取时优先使用 `info/` 文件夹编译结果，回退到根目录 `info.json`。

**数据格式**：与知识详情页结构一致，支持 `page`、`hero`、`introduction`、`sections` 等字段。

### 元数据配置文件 (`meta.yaml`)

**用途**：定义站点的页面标题、栏目结构等元数据，构建脚本据此生成站点首页和栏目首页的 `index.json`。

**文件位置**：`my_sites_data/<site>/meta.yaml`（**统一放在站点根目录**）

**基本结构**：

```yaml
page:
  title: "站点标题"
  description: "站点描述"
  brand_name: "BRAND_NAME"   # 英文品牌名（首页装饰标签）
  subtitle: "站点副标题"      # 首页副标题/介绍语
  tags:
    - "标签 1"
modules:
  - id: "wiki"           # 文件夹名，用于生成 link
    title: "常识概览"
    description: "描述"
    image: "wiki.jpg"      # 图片文件名，编译时自动转为 /api/image/<site>/<filename>
    tags:
      - "生活常识"
      - "科学原理"
  - id: "tools"
    title: "工具&游戏"
    description: "学习工具、可视化组件、演示案例等实用工具"
    image: "tools.jpg"
    tags:
      - "学习工具"
      - "可视化"
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `page.title` | string | 是 | 页面标题（浏览器标签页显示） |
| `page.description` | string | 是 | 页面描述（SEO 优化） |
| `page.brand_name` | string | 否 | 英文品牌名（首页装饰标签，如 `KNOWLEDGE_CUBE`） |
| `page.subtitle` | string | 否 | 站点副标题/介绍语（首页副标题） |
| `page.tags` | string[] | 否 | 标签列表（显示在标题右侧） |
| `modules` | array | 否 | 定义首页栏目卡片和栏目配置 |

**`modules` 下的栏目配置字段**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 栏目标识，对应文件夹名，用于生成 link |
| `title` | string | 是 | 栏目标题（同时用于栏目页面标题） |
| `description` | string | 否 | 栏目描述（同时用于栏目页面 SEO） |
| `image` | string | 否 | 栏目封面图文件名 |
| `tags` | string[] | 否 | 栏目标签列表 |

**分类的来源**：

分类和子分类**不是**在 `meta.yaml` 中配置的，而是由构建脚本根据目录结构自动扫描生成。目录结构如下：

```
my_sites_data/<site>/
  └── wiki/                    # 栏目（对应 modules 中的 id）
      ├── 01 文学/             # 一级分类（目录名即为分类名）
      │   ├── 01 中国古代文学/  # 二级分类
      │   │   └── tang-poetry/  # 页面目录
      │   │       └── data.json
      │   └── 02 外国文学/      # 二级分类
      │       └── shakespeare/
      │           └── data.json
      └── 02 自然科学/         # 一级分类
          ├── 01 天文学/
          │   └── solar-system/
          │       └── data.json
          └── 02 物理学/
              └── relativity/
                  └── data.json
```

构建脚本扫描上述目录后，会在 `wiki/index.json` 中生成如下 `categories` 结构：

```json
{
  "categories": [
    {
      "name": "文学",
      "subCategories": [
        {
          "name": "中国古代文学",
          "links": [
            { "title": "唐诗", "url": "/wiki/tang-poetry" }
          ]
        },
        {
          "name": "外国文学",
          "links": [
            { "title": "莎士比亚", "url": "/wiki/shakespeare" }
          ]
        }
      ]
    },
    {
      "name": "自然科学",
      "subCategories": [
        {
          "name": "天文学",
          "links": [
            { "title": "太阳系", "url": "/wiki/solar-system" }
          ]
        },
        {
          "name": "物理学",
          "links": [
            { "title": "相对论", "url": "/wiki/relativity" }
          ]
        }
      ]
    }
  ]
}
```

**关于序号前缀**：

分类和子分类的目录名可以添加 `01 `、`02 ` 等序号前缀（如 `01 文学`、`02 自然科学`），用于在文件系统中控制排序顺序。构建脚本会自动去掉序号前缀，仅展示纯名称（如 `文学`、`自然科学`）。

**注意事项**：

- **所有 meta 配置统一放在站点根目录的 `meta.yaml` 中**
- `image` 字段只写文件名（如 `wiki.jpg`），构建脚本会自动补全为 `/api/image/<site>/<filename>`
- `modules` 中的 `id` 是文件夹名，用于生成 `link`（如 `/wiki`）
- 如果栏目目录下无子目录，构建脚本会自动生成 `全部` 分类列出所有子页面
- `recent` 列表始终由构建脚本自动生成（取最近更新的 8 个页面）
- 站点根目录 `meta.yaml` 的 `modules` 定义首页展示的栏目卡片；未在 `modules` 中定义但存在的栏目目录也会被构建脚本扫描并生成索引

## 图片资源

### 图片目录结构

```
my_sites_data/<site>/image/
  ├── wiki.jpg        # 栏目封面图
  ├── tools.jpg
  └── topic.jpg
```

### 图片使用规则

1. **封面图**：`meta.yaml` 中 `image` 字段只写文件名（如 `wiki.jpg`）
2. **构建时自动转换**：`build_service.py` 会将文件名补全为 `/api/image/<site>/<filename>`
3. **图片服务**：后端通过 `GET /api/image/:site/:filename` 从 `DATA_ROOT/<site>/image/` 读取图片
4. **支持的格式**：jpg、jpeg、png、gif、webp、svg

### 图片生成示例

```python
from PIL import Image, ImageDraw, ImageFont

# 创建渐变封面图
img = Image.new('RGB', (800, 400), (60, 40, 180))
draw = ImageDraw.Draw(img)
for y in range(400):
    ratio = y / 400
    r = int(60 + (120 - 60) * ratio)
    g = int(40 + (80 - 40) * ratio)
    b = int(180 + (240 - 180) * ratio)
    draw.line([(0, y), (800, y)], fill=(r, g, b))
img.save('wiki.jpg', 'JPEG', quality=85)
```

## 知识详情页数据格式

### 基本结构

```json
{
  "page": {
    "title": "页面标题",
    "description": "页面描述（用于 SEO）"
  },
  "hero": {
    "title": "主标题（大标题）",
    "tags": ["标签 1", "标签 2"]
  },
  "version": "v1",
  "lastModified": "2026-05-11 12:00:00",
  "introduction": "页面引言/导语（显示在 hero 下方）",
  "sections": [...]
}
```

### `page` - 页面元信息

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 页面标题（浏览器标签页显示） |
| `description` | string | 是 | 页面描述（SEO 优化） |

### `hero` - 页面头部信息

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 页面主标题（页面顶部大标题） |
| `brand_name` | string | 否 | 英文品牌名（首页装饰标签） |
| `subtitle` | string | 否 | 站点副标题/介绍语 |
| `tags` | string[] | 否 | 标签列表（显示在标题右侧） |

### `version` 与 `lastModified` - 页面版本信息

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `version` | string | 否 | 页面版本号（默认 `v1`） |
| `lastModified` | string | 否 | 最后编辑时间（格式：`YYYY-MM-DD HH:MM:SS`） |
| `generatedAt` | string | 否 | 索引生成时间（由构建脚本自动生成） |

### `sections` - 章节内容

每个章节包含以下字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 章节 ID（用于导航和锚点） |
| `title` | string | 是 | 章节完整标题 |
| `subtitle` | string | 否 | 副标题（章节标题下方的小字） |
| `type` | string | 否 | 内容类型（默认 `mixed`） |
| `content` | object | 否 | 章节内容对象 |

### `content` - 内容对象

`content` 中的字段分为两类：**可视化控件**（展示特定数据）和 **排版功能**（控制布局）。

**可视化控件**：
- `stats` — 统计卡片
- `cards` — 卡片列表（**多个相同实体的展示**，如湖泊列表、山峰列表）
- `tables` — 表格
- `charts` — 图表（柱状图、饼图、折线图、中国地图）
- `timeline` — 时间线
- `branchVisualizer` — 分支发展可视化
- `chips` — 标签芯片
- `list` — 带图标列表

**排版功能**：
- `columns` — 分栏布局（**只是位置上并行**，每个栏内容可以不统一，如左边文字右边配图）
- `description` — 文本段落
- `blocks` — 顺序内容块数组（按原始文档顺序渲染各内容块）

**分栏与卡片的区别**：
- **分栏**是排版方式，只是位置上并行，每个栏可以内容不统一（如左边文字、右边配图）
- **卡片**是可视化控件，用于展示多个相同实体的结构化信息（如多个湖泊的信息卡片）

#### `blocks` - 顺序内容块（v2.0 新增）

`blocks` 数组按原始文档顺序记录内容块，前端优先按此顺序渲染，确保文字与控件交替显示。

```json
{
  "blocks": [
    { "type": "description", "data": ["段落内容..."] },
    { "type": "cards", "data": [[{ "headline": "卡片标题", "supporting": "描述" }]] },
    { "type": "tables", "data": [{ "headers": ["列1"], "rows": [["值1"]] } ] },
    { "type": "timeline", "data": { "title": "", "items": [...] } }
  ]
}
```

支持的 `type` 值：`description`、`stats`、`tables`、`cards`、`charts`、`list`、`chips`、`branchVisualizer`、`timeline`。

> **兼容性**：旧数据若无 `blocks` 字段，前端会回退到按独立字段（`description` → `stats` → `tables` → ...）顺序渲染。

#### `description` - 文本段落

```json
{
  "description": [
    "第一段内容...",
    "第二段内容..."
  ]
}
```

#### `stats` - 统计卡片

```json
{
  "stats": [
    {
      "value": "4457.9",
      "label": "万平方公里"
    }
  ]
}
```

#### `tables` - 表格

支持多组表格，每组表格独立渲染。

```json
{
  "tables": [
    {
      "headers": ["列 1", "列 2"],
      "rows": [
        ["值 1", "值 2"]
      ]
    }
  ]
}
```

#### `cards` - 卡片列表

支持多组卡片，每组卡片独立渲染（组间有间隔）。

```json
{
  "cards": [
    [
      {
        "headline": "卡片标题",
        "supporting": "卡片描述文字",
        "detail": ["详细信息 1"],
        "image": "图片 URL"
      }
    ]
  ]
}
```

#### `charts` - 图表

**柱状图**：
```json
{
  "charts": [
    {
      "type": "bar",
      "id": "chart-1",
      "title": "图表标题",
      "xAxis": ["类别 1", "类别 2"],
      "data": [10, 20],
      "color": "#546e7a"
    }
  ]
}
```

**饼图**：
```json
{
  "charts": [
    {
      "type": "pie",
      "id": "chart-2",
      "title": "饼图标题",
      "subType": "donut",
      "data": [
        { "value": 30, "name": "类别 A", "color": "#5c6bc0" }
      ]
    }
  ]
}
```

**中国地图**：
```json
{
  "charts": [
    {
      "type": "chinaMap",
      "id": "china-map-1",
      "title": "中国地图标题"
    }
  ]
}
```

#### `list` - 列表

```json
{
  "list": {
    "title": "列表标题",
    "items": [
      {
        "icon": "A",
        "title": "列表项标题",
        "subtitle": "列表项副标题"
      }
    ]
  }
}
```

#### `chips` - 标签芯片

```json
{
  "chips": [
    { "label": "标签 1", "accent": true }
  ]
}
```

#### `branchVisualizer` - 分支发展可视化

```json
{
  "branchVisualizer": {
    "periods": ["时期 1", "时期 2"],
    "branches": [
      {
        "name": "分支名称",
        "levels": [5, 4],
        "descriptions": ["描述 1", "描述 2"]
      }
    ]
  }
}
```

#### `timeline` - 时间线

`description` 支持嵌套数组表示层级结构：字符串为主条目，数组内第一个元素为主条目，后续为子条目。

```json
{
  "timeline": {
    "title": "时间线标题",
    "items": [
      {
        "date": "2024-01-01",
        "title": "事件标题",
        "subtitle": "事件副标题",
        "description": [
          "主条目描述",
          ["主条目标题", "子条目 1", "子条目 2"]
        ],
        "image": "图片 URL"
      }
    ]
  }
}
```

#### `columns` - 分栏布局

分栏是一种**排版功能**，用于将内容在水平方向上并行排列。每个栏的内容可以完全不同。

**分栏与卡片的区别**：
- **分栏**是排版方式，只是位置上并行，每个栏可以内容不统一（如左边文字、右边配图）
- **卡片**是可视化控件，用于展示多个相同实体的结构化信息（如多个湖泊的信息卡片）

```json
{
  "columns": [
    {
      "items": ["左侧文字内容..."],
      "tables": [...],
      "list": {...}
    },
    {
      "items": ["右侧文字内容..."]
    }
  ]
}
```

每个分栏对象包含以下可选字段：
- `items` — 文本段落数组（支持 Markdown 语法，可包含 `##` / `###` / `####` 标题）
- `tables` — 表格数组
- `list` — 列表对象
- `cards` — 卡片数组
- `stats` — 统计卡片数组
- `charts` — 图表数组

### 标题字段

`description` 数组中的文本项如果以特定 Markdown 标题前缀开头，前端会渲染为对应层级的 HTML 标题：

| 前缀 | 渲染标签 | 说明 |
|------|----------|------|
| `## 标题` | `<h3>` | 章节内的二级子标题（视觉样式为 h2） |
| `### 标题` | `<h4>` | 章节内的三级子标题 |
| `#### 标题` | `<h5>` | 章节内的四级子标题 |

> 注意：页面标题（`<h1>`）和章节标题（`<h2>`）分别由 `hero.title` 和 `section.title` 渲染，不通过 `description` 中的标题前缀实现。

## 二级分类页数据格式

### 基本结构

```json
{
  "page": {
    "title": "页面标题",
    "description": "页面描述"
  },
  "hero": {
    "title": "主标题",
    "tags": ["标签 1"]
  },
  "version": "v1",
  "lastModified": "2026-05-11 12:00:00",
  "generatedAt": "2026-05-11 12:00:00",
  "recent": [...],
  "categories": [...]
}
```

### `recent` - 最近更新

```json
{
  "recent": [
    {
      "title": "文章标题",
      "subtitle": "",
      "desc": "",
      "link": "/页面链接"
    }
  ]
}
```

### `categories` - 分类索引

```json
{
  "categories": [
    {
      "name": "分类名称",
      "subCategories": [
        {
          "name": "子分类名称",
          "links": [
            {
              "title": "页面标题",
              "url": "/页面链接"
            }
          ]
        }
      ]
    }
  ]
}
```

## 字段说明

### 必填字段

| 字段路径 | 说明 |
|----------|------|
| `page.title` | 页面标题 |
| `page.description` | 页面描述 |
| `hero.title` | 主标题 |
| `sections[].id` | 章节 ID |
| `sections[].title` | 章节标题 |

### 可选字段

| 字段路径 | 说明 | 默认值 |
|----------|------|--------|
| `introduction` | 页面引言/导语 | `null` |
| `version` | 页面版本号 | `v1` |
| `lastModified` | 最后编辑时间 | 文件修改时间 |
| `generatedAt` | 索引生成时间 | 构建时自动生成 |
| `hero.brand_name` | 英文品牌名 | `""` |
| `hero.subtitle` | 站点副标题/介绍语 | `""` |
| `hero.tags` | 标签列表 | `[]` |
| `sections[].subtitle` | 副标题 | `""` |
| `sections[].type` | 内容类型 | `"mixed"` |

### 内容类型 (`type`)

| 类型 | 说明 |
|------|------|
| `mixed` | 混合内容（默认，支持所有元素） |
| `text` | 纯文本 |

## 注意事项

- **严禁使用 Emoji 表情**：所有文本内容禁止使用 Emoji
- **图片使用**：鼓励使用图片增强视觉效果，封面图放在 `image/` 目录下，文件名引用即可
- **图表使用**：鼓励使用 ECharts 图表展示数据
- **目录名支持中文**：分类和子分类目录可以直接使用中文名称（如 `自然科学`、`天文学`）
- **目录名支持序号前缀**：分类和子分类目录名可以添加 `01 `、`02 ` 等序号前缀用于排序，构建脚本会自动去掉前缀，仅展示纯名称
- **数据文件统一命名为 `data.json`**
- **元数据配置文件统一命名为 `meta.yaml`**（优先）或 `meta.json`（兼容）
- **测试页面**必须放在 `my_sites_data/<site>/tools/` 目录下
- **image 文件名**：只写文件名，不要写完整路径，构建脚本会自动处理
- **Markdown 内联格式**：`description` 中的加粗 `**text**`、斜体 `*text*`、行内代码 `` `code` `` 等 Markdown 语法由前端渲染时解析，编译器保留原始语法
- **标题来源**：页面标题和章节标题只来自 frontmatter，正文 `#` / `##` 标题仅用于单文件模式拆分 section，多文件模式下被忽略
- **分栏语法**：`columns` 字段支持在 section 内容下直接定义分栏，每个分栏可包含文本、表格、列表、卡片、图表等控件

## 相关文档

- [exmd-spec.md](exmd-spec.md) — EXMD 源格式语法规范（面向内容创作者）
- 本文档 — JSON/YAML 数据格式规范（面向前端渲染引擎）

**文档版本**：2.0
**最后更新**：2026-07-05
