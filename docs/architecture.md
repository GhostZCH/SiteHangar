# 架构设计

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + TypeScript + Pinia + Vue Router + Tailwind CSS |
| 后端 | Node.js + Express + TypeScript |
| 数据 | Markdown + YAML，编译后生成 JSON 文件 |
| 部署 | Docker（Node.js + Nginx + Supervisor 单容器） |

## 部署架构

单一 Docker 容器内运行三个进程，由 Supervisor 统一管理：

| 进程 | 端口 | 说明 |
|------|------|------|
| Nginx | 80 | 统一入口，反向代理 API 和 Vite dev server |
| Vite dev server | 5173 | 开发服务器，支持 HMR |
| Express 后端 | 3000 | API 服务，内部端口，通过 Nginx 反代暴露 |

### Nginx 反代规则

- `/api/` -> `http://localhost:3000`（Express 后端）
- `/@vite/` -> `http://localhost:5173`（WebSocket HMR）
- `/` -> `http://localhost:5173`（Vite dev server）

## 核心设计理念：数据与展示分离

所有页面内容以 Markdown 文件形式存储，编译后生成 JSON 文件。系统启动时扫描数据目录生成站点结构。前端通过 API 获取 JSON 数据，由 Vue 组件动态渲染页面。

### 页面渲染流程

```
用户请求 URL
    -> Nginx（端口 80）
    -> Vite dev server（localhost:5173）
    -> Vue Router 匹配路由，加载视图组件
    -> 视图组件调用 API（/api/render/*path）获取 JSON 数据
    -> Express 后端从 build/ 目录读取数据文件
    -> Vue 组件根据数据内容动态渲染页面
```

### 页面类型自动判断

Vue Router 根据数据内容自动判断页面类型：

| 页面类型 | 数据特征 | 渲染视图 |
|----------|----------|----------|
| 首页 | 有 `modules` 字段 | HomeView（模块卡片） |
| 分类页 | 有 `categories` 或 `recent` 字段，无 `sections` | CategoryView |
| 详情页 | 有 `sections` 字段 | DetailView（hero + 导航 + sections） |
| 混合页 | 既有 `sections` 又有 `categories`/`recent` | DetailView |

## 多站点支持

同一套前端代码支持多个站点，通过请求 `Host` 头或查询参数确定当前站点，映射到对应的数据目录。

典型结构如下：

| 站点 | 数据目录 | 示例栏目 |
|------|----------|----------|
| 站点 A | `build/site-a/` | wiki, topic, tools |
| 站点 B | `build/site-b/` | reading, blog, daily |

实际站点名称、域名和栏目由部署时的配置决定。

## 数据目录层级（5 层结构）

```
build/
├── <site>/                   # 第一层：站点目录
│   ├── index.json            # 站点首页数据（modules 字段定义栏目）
│   ├── info.json             # 关于/帮助页面数据
│   ├── info/                 # 关于页面源文件（可选，编译后生成 info.json）
│   │   ├── data.md           # 关于页面元数据
│   │   ├── 01-xxx.md         # 章节文件
│   │   └── 02-xxx.md
│   └── <column>/             # 第二层：栏目
│       ├── index.json        # 栏目首页（categories/recent 字段定义分类结构）
│       └── <category>/       # 第三层：一级分类（支持 `01 ` 序号前缀排序）
│           └── <subcategory>/ # 第四层：二级分类（支持 `01 ` 序号前缀排序）
│               └── <page>/    # 第五层：具体页面目录
│                   ├── data.json    # 页面渲染数据
│                   └── images/      # 页面图片资源
```

### URL 映射规则

| URL 路径 | 数据文件路径 | 说明 |
|----------|-------------|------|
| `/` | `build/<site>/index.json` | 首页 |
| `/info` | `build/<site>/info.json` | 关于页 |
| `/wiki` | `build/<site>/wiki/index.json` | 栏目首页 |
| `/wiki/social-sciences/economics/macroeconomics` | `build/<site>/wiki/social-sciences/economics/macroeconomics/data.json` | 详情页 |

## 数据编译流程

```
Markdown 源数据
    -> tools/build_service.py
    -> 解析 Frontmatter、特殊语法块
    -> 生成 data.json、index.json
    -> 输出到 build/<site>/ 目录
    -> Express 后端读取并返回
```

- 源数据目录：站点目录下的 `data/` 或 `site_data/`（由部署配置决定）
- 编译输出目录：`build/`（由 `config.yaml` 的 `buildOutputDir` 指定）
- 编译后只需部署 `build/` 目录即可运行网站
