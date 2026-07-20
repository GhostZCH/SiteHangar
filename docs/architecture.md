# 架构设计

本文档说明 SiteHangar 的整体架构、技术选型、代码模块、核心文件作用、数据流转、API 流程以及多站点映射机制。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + TypeScript + Pinia + Vue Router + Tailwind CSS + ECharts |
| 后端 | Node.js + Express + TypeScript |
| 数据 | Markdown + YAML，编译后生成 JSON 文件 |
| 部署 | Docker 单容器（Nginx + Vite dev server + Express + Supervisor） |

## 部署架构

单一 Docker 容器内运行三个进程，由 Supervisor 统一管理：

| 进程 | 端口 | 说明 |
|------|------|------|
| Nginx | 80 | 统一入口，反向代理 API 和 Vite dev server |
| Vite dev server | 5173 | 开发服务器，支持 HMR |
| Express 后端 | 3000 | API 服务，内部端口，通过 Nginx 反代暴露 |

### Nginx 反代规则

- `/api/` → `http://localhost:3000`（Express 后端）
- `/@vite/` → `http://localhost:5173`（WebSocket HMR）
- `/` → `http://localhost:5173`（Vite dev server）

## 数据与展示分离

所有内容以 Markdown 文件形式存储，编译后生成 JSON 文件。网站服务只读取编译结果，不直接读取源数据。前端通过 API 获取 JSON 数据，由 Vue 组件动态渲染页面。

### 页面渲染流程

```
用户请求 URL
    -> Nginx（端口 80）
    -> Vite dev server（localhost:5173）
    -> Vue Router 匹配路由，加载视图组件
    -> 视图组件调用 API（/api/render/*path）获取 JSON 数据
    -> Express 后端从 DATA_ROOT 目录读取数据文件
    -> Vue 组件根据数据内容动态渲染页面
```

### 页面类型与路由映射

前端 Vue Router 按 URL 直接映射到视图组件，后端 `/api/render/*path` 同时在响应中用 `type` 字段标识页面类型：

| 页面类型 | URL 路由 | 渲染视图 | 后端 `type` |
|----------|----------|----------|-------------|
| 首页 | `/` | HomeView（模块卡片） | `home` |
| 分类页 | `/:moduleSlug` | CategoryView | `category` |
| 详情页 | `/:moduleSlug/:path*` | DetailView（hero + 导航 + sections） | `detail` |
| 关于页 | `/info` | DetailView | `detail` |

视图组件根据返回数据的字段（`modules` / `categories` / `sections` 等）决定渲染哪些内容块。

## 数据编译流程

```
Markdown 源数据
    -> tools/builder/build_service.py
    -> 解析 Frontmatter、特殊语法块
    -> 生成 data.json、index.json
    -> 输出到 DATA_ROOT/<site>/ 目录
    -> Express 后端读取并返回
```

- **源数据目录**：站点目录下的 `data/`（如 `example/data/`）
- **编译输出目录**：由 `config.yaml` 的 `buildOutputDir` 指定（如 `example/build/`）
- 编译后只需部署编译输出目录即可运行网站

## 多站点支持

同一套前端代码支持多个站点，通过请求 `Host` 头确定当前站点，映射到对应的数据目录。

| 站点 | 数据目录 | 示例栏目 |
|------|----------|----------|
| 站点 A | `DATA_ROOT/site-a/` | wiki, topic, tools |
| 站点 B | `DATA_ROOT/site-b/` | reading, blog, daily |

实际站点名称、域名和栏目由部署时的配置决定。

## 数据目录层级（5 层结构）

```
DATA_ROOT/                    # 编译输出目录（如 example/build 或 my_sites_data/result）
├── <site>/                   # 第一层：站点目录
│   ├── index.json            # 站点首页数据（modules 字段定义栏目）
│   ├── info/                 # 关于页面目录（编译后生成 info/data.json）
│   │   ├── data.json         # 关于/帮助页面渲染数据
│   │   ├── meta.md           # 关于页面元数据（源文件，多 MD 模式）
│   │   ├── 01-xxx.md         # 章节文件（源文件）
│   │   └── 02-xxx.md
│   └── <column>/             # 第二层：栏目
│       ├── index.json        # 栏目首页（categories/recent 字段定义分类结构）
│       └── <category>/       # 第三层：一级分类（支持 01 序号前缀排序）
│           └── <subcategory>/ # 第四层：二级分类（支持 01 序号前缀排序）
│               └── <page>/    # 第五层：具体页面目录
│                   ├── data.json    # 页面渲染数据
│                   └── image/       # 页面图片资源
```

### URL 映射规则

| URL 路径 | 数据文件路径 | 说明 |
|----------|-------------|------|
| `/` | `DATA_ROOT/<site>/index.json` | 首页 |
| `/info` | `DATA_ROOT/<site>/info/data.json` | 关于页 |
| `/wiki` | `DATA_ROOT/<site>/wiki/index.json` | 栏目首页 |
| `/wiki/social-sciences/economics/macroeconomics` | `DATA_ROOT/<site>/wiki/social-sciences/economics/macroeconomics/data.json` | 详情页 |

## 代码模块与文件作用

### 项目目录总览

```
site_hangar/
├── src/
│   ├── client/          # Vue 3 前端
│   └── server/          # Node.js + Express 后端
├── docker/              # Docker 配置
│   ├── Dockerfile
│   ├── supervisord.conf
│   └── entrypoint.sh
├── example/             # 示例站点
│   ├── conf/            # 站点配置（config.yaml、entrypoint.sh、nginx.conf）
│   ├── data/            # 源数据
│   ├── build/           # 编译输出
│   └── README.md
├── tools/               # 构建工具
│   ├── builder/         # 编译脚本（build_service.py 等）
│   └── editor/          # 本地 Markdown 编辑器
└── docs/                # 项目文档
```

### 前端 client/

| 文件/目录 | 作用 |
|-----------|------|
| `src/main.ts` | Vue 应用入口：创建 app、挂载 Pinia、Router |
| `src/App.vue` | 根组件：布局 AppHeader + AppNav + router-view |
| `src/router/index.ts` | 路由表：home、info、module、detail、404 |
| `src/stores/site.ts` | Pinia store：当前站点 slug、模块列表 |
| `src/api/client.ts` | axios 实例配置（baseURL: /api） |
| `src/api/public.ts` | 公开 API 封装：render、listColumns、getGlobalConfig |
| `src/types/content.ts` | 内容数据结构：Section、PageData、RenderResponse 等 |
| `src/composables/useTheme.ts` | 主题切换逻辑：7 种主题 |
| `src/composables/usePageData.ts` | 页面数据加载：处理路由切换竞态（丢弃过期响应） |
| `src/composables/usePageSections.ts` | 章节导航提取与滚动监听 |
| `src/composables/useKatex.ts` | KaTeX 懒加载封装（动态 import，就绪后触发公式重渲染） |
| `src/views/HomeView.vue` | 首页：Hero + 模块卡片网格 |
| `src/views/DetailView.vue` | 详情页：Hero + SectionRenderer 列表 |
| `src/views/CategoryView.vue` | 分类页：最近更新 + 分类标签页 |
| `src/components/content/SectionRenderer.vue` | 章节渲染器，根据内容类型分发到各子组件 |
| `src/components/content/` | 内容块组件：DescriptionBlock、ChartBlock、MermaidBlock、TimelineBlock、TableBlock、StatsBlock、CardListBlock、ChipsBlock、ColumnBlock、ListBlock、TreeBlock、BranchVisualizerBlock、SubSectionBlock、DetailHero、DetailContent、PageLoading、PageError |
| `src/components/layout/AppHeader.vue` | 顶部导航栏 |
| `src/components/layout/AppNav.vue` | 左侧抽屉导航 |
| `src/styles/*.css` | 按功能模块拆分的样式文件 |

### 后端 server/

| 文件/目录 | 作用 |
|-----------|------|
| `src/server.ts` | 服务器启动：监听 PORT，打印访问地址 |
| `src/app.ts` | Express 应用：中间件、路由挂载、静态文件、SPA fallback |
| `src/config/paths.ts` | 数据根目录、站点/页面/模块/首页/关于页路径生成函数 |
| `src/config/sites.ts` | 读取 config.yaml，根据 Host 解析数据目录 |
| `src/middlewares/resolve-site.ts` | 根据请求 Host 头解析 siteSlug |
| `src/middlewares/error-handler.ts` | 全局错误处理：HttpError / 500 / 404 |
| `src/routes/public.routes.ts` | 路由入口：汇总挂载 config + image + render + module 路由 |
| `src/routes/render.routes.ts` | `/api/render/*path`：首页/详情页/分类页/info 页渲染 |
| `src/routes/module.routes.ts` | `/api/sites/:siteSlug/columns`、`:columnSlug/pages` |
| `src/routes/image.routes.ts` | `/api/image/:site/:filename`、页面静态资源 |
| `src/routes/config.routes.ts` | `/api/config`：读取网站公开配置 |
| `src/services/page-service.ts` | 页面操作：getPage、getHomePage、getInfoPage（直接读文件，不缓存） |
| `src/services/column-scanner.ts` | 栏目扫描：getColumns（从 index.json 的 modules 读取栏目） |
| `src/services/page-scanner.ts` | 页面扫描：getColumnPages（递归扫描栏目下的页面目录） |
| `src/services/config-service.ts` | 配置操作：getSiteConfig |
| `src/services/cache.ts` | 内存缓存工具：cacheKey / getCached / setCached / clearCached（当前仅用于写操作后的缓存失效） |
| `src/services/fs-utils.ts` | 文件工具：readJsonFile / writeJsonFile / removePath |

### 构建工具 tools/

| 文件 | 作用 |
|------|------|
| `tools/builder/build_utils.py` | 公共工具：日志、文件读写、Frontmatter 解析、目录扫描、序号前缀去除 |
| `tools/builder/build_page_parser.py` | Markdown 特殊语法解析器（`_MarkdownParser` 类按语法块类型分发解析） |
| `tools/builder/build_page.py` | 单页面编译模块（单 MD 模式 + 多 MD 模式） |
| `tools/builder/build_index.py` | 索引生成：元数据合并、分类扫描 |
| `tools/builder/build_service_info.py` | Info 页面编译模块 |
| `tools/builder/build_service.py` | 全体编译入口 |
| `tools/editor/` | 本地 Markdown 编辑器：独立 Web 服务，支持编辑和实时预览 |

## API 流程

### 公开 API

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/render/*path` | GET | 通配渲染：首页 / 详情页 / 分类页 / info 页 |
| `/api/sites/:siteSlug/columns` | GET | 列出站点所有栏目 |
| `/api/sites/:siteSlug/columns/:columnSlug/pages` | GET | 列出栏目下所有页面 |
| `/api/image/:site/:filename` | GET | 站点级图片 |
| `/api/page-asset/:site/*path` | GET | 页面级静态资源 |
| `/api/config` | GET | 读取网站公开配置 |

### 路由挂载

```typescript
// app.ts
app.use('/api', publicRoutes);

// public.routes.ts
router.use(renderRoutes);   // /render/*path
router.use(moduleRoutes);   // /sites/:siteSlug/columns
router.use(imageRoutes);    // /image/:site/:filename, /page-asset/:site/*path
```

### 响应格式

`/api/render/*path` 成功时返回页面渲染数据（无 `success` 包装字段）：

```json
{
  "site": { "slug": "site-slug" },
  "column": { "slug": "wiki" },
  "page": { "slug": "xxx", "title": "页面标题" },
  "type": "home | category | detail",
  "data": { "...": "页面数据（modules / categories / sections 等）" }
}
```

`type` 取值与页面类型对应：`home`（首页）、`category`（栏目/分类页）、`detail`（详情页/关于页）。

`/api/sites/:siteSlug/columns` 返回 `{ "columns": [...] }`，`/api/config` 返回 `{ "icp": "..." }`。

错误时返回相应 HTTP 状态码和 `error` 字段：

```json
{
  "error": "NOT_FOUND"
}
```

常见 HTTP 状态码：

| 状态码 | 含义 | 常见原因 |
|--------|------|----------|
| 200 | 成功 | — |
| 400 | 非法路径 | 路径包含 `..` 等非法字符 |
| 403 | 禁止访问 | 路径解析后超出 DATA_ROOT 范围 |
| 404 | 资源未找到 | 路径不存在、站点未配置、数据文件缺失 |
| 500 | 服务器内部错误 | 数据文件解析失败、权限问题 |

## 图片资源

- 站点级图片：放在 `<site>/image/` 目录下，在 `meta.yaml` 中引用文件名
- 页面级图片：放在页面目录下的 `image/` 目录下，在 EXMD 中引用 `image/xxx.jpg`
- 图片服务：`/api/image/:site/:filename` 从 `DATA_ROOT/<site>/image/` 读取站点级图片；页面级图片通过 `/api/page-asset/:site/*path` 读取

## 开发规范

- 使用 TypeScript，严格类型检查
- 前端使用 Composition API + `<script setup>`
- 后端使用 async/await，错误通过 next(err) 传递
- 单个代码文件建议 100-200 行，最多不超过 300 行
- 所有文本内容禁止使用 Emoji
- 组件文件使用 PascalCase，工具函数使用 camelCase，路由/服务使用 kebab-case
- 样式文件按功能模块拆分，位于 `src/client/src/styles/`
- 移动端断点：`max-width: 768px`

## 相关文档

- [exmd.md](exmd.md) — EXMD 内容格式说明
- [deployment.md](deployment.md) — 部署运维指南
- [changelog.md](changelog.md) — 变更日志
