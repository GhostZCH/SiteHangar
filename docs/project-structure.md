# 项目结构

本文档说明前端（client）和后端（server）的代码组织方式，帮助开发者快速定位文件。

## 目录总览

```
my_sites/
├── client/          # Vue 3 前端
├── server/          # Node.js + Express 后端
├── docker/          # Docker 共享配置
│   └── supervisord.conf
├── example/         # 示例站点
│   ├── conf/        # 站点配置（config.yaml、entrypoint.sh、nginx.conf）
│   ├── data/        # 源数据
│   ├── build/       # 编译输出
│   └── README.md
├── Dockerfile
└── docs/            # 项目文档
```

## 前端 client/

### 入口文件

| 文件 | 说明 |
|------|------|
| `src/main.ts` | Vue 应用入口：创建 app、挂载 Pinia、Router |
| `src/App.vue` | 根组件：布局 AppHeader + AppNav + router-view |
| `index.html` | HTML 模板 |
| `vite.config.ts` | Vite 配置（代理 /api 到 localhost:3000） |

### 路由 router/

| 文件 | 说明 |
|------|------|
| `src/router/index.ts` | 路由表：home、info、module、detail、404 |

### 状态管理 stores/

| 文件 | 说明 |
|------|------|
| `src/stores/site.ts` | Pinia store：当前站点 slug、模块列表 |

### API 层 api/

| 文件 | 说明 |
|------|------|
| `src/api/client.ts` | axios 实例配置（baseURL: /api） |
| `src/api/public.ts` | 公开 API：render、listColumns、getPublicConfig |

### 类型定义 types/

| 文件 | 说明 |
|------|------|
| `src/types/content.ts` | 内容数据结构：`Section`（含 `id`/`title`/`subtitle`/`type`/`content`）、`PageData`、`RenderResponse` 等 |
| `src/types/api.ts` | 后端管理接口类型：Module、Page、Config 等 |

### 组合式函数 composables/

| 文件 | 说明 |
|------|------|
| `src/composables/useTheme.ts` | 主题切换逻辑：7 种主题（default/warm/cold/night/glass/eye-care/3d） |

### 布局组件 components/layout/

| 文件 | 说明 |
|------|------|
| `AppHeader.vue` | 顶部导航栏：Logo、站点名、模块链接、主题切换菜单 |
| `AppNav.vue` | 左侧抽屉导航：模块列表/页面目录，支持展开/收起，展开显示完整标题（最多6字），收起显示前2字 |
| `NavList.vue` | 导航列表渲染：根据 `expanded` prop 控制显示短标题或截断标题 |

### 页面视图 views/

| 文件 | 说明 |
|------|------|
| `HomeView.vue` | 首页：Hero + 模块卡片网格 |
| `DetailView.vue` | 详情页：Hero（标题/标签/版本）+ SectionRenderer 列表 |
| `CategoryView.vue` | 分类页：最近更新 + 分类标签页 + 子分类卡片 |
| `InfoView.vue` | 关于页：Hero + sections |
| `NotFoundView.vue` | 404 页面 |

### 内容渲染组件 components/content/

| 文件 | 说明 |
|------|------|
| `SectionRenderer.vue` | 章节渲染器：根据 section.content 分发到各子组件；优先使用 `blocks` 数组顺序渲染，兼容旧数据格式（无 blocks 时回退到原有字段） |
| `SubSectionBlock.vue` | 子章节渲染器：支持 `blocks` 顺序渲染和旧数据兼容 |
| `DescriptionBlock.vue` | 文本段落渲染器：支持 Markdown 内联格式（加粗、斜体、代码、链接、公式）、引用块（`> `）、无序/有序列表（圆角边框+分隔线样式）、三级标题（`###`）和加粗标题（`**标题**`）转为 h4 渲染 |
| `StatsBlock.vue` | 统计卡片网格 |
| `TableBlock.vue` | 表格（支持多组表格） |
| `CardListBlock.vue` | 卡片列表（grid-3，支持多组卡片独立渲染） |
| `ChartBlock.vue` | ECharts 图表（bar/pie/line） |
| `TimelineBlock.vue` | 时间线：支持 `description` 嵌套数组（主条目 + 子条目层级结构） |
| `ListBlock.vue` | 列表（带图标） |
| `ChipsBlock.vue` | 标签芯片 |
| `BranchVisualizerBlock.vue` | 分支发展可视化 |

### 样式 styles/

| 文件 | 说明 |
|------|------|
| `main.css` | 入口：Tailwind + 导入所有子样式 |
| `themes.css` | CSS 变量与 7 套主题定义 |
| `base.css` | 全局重置、body 样式 |
| `layout.css` | AppBar、NavDrawer、Hero、Footer 布局 |
| `components.css` | 卡片、表格、按钮、芯片、列表、投票等组件样式 |
| `timeline.css` | 时间线组件样式 |
| `charts.css` | 图表容器、分支可视化、中国地图样式 |
| `pages.css` | 首页模块卡片、分类页布局 |
| `home-view.css` | HomeView 组件专属样式：全局背景、Hero、模块卡片网格 |
| `responsive.css` | 响应式断点（1024px / 768px） |
| `glass-theme.css` | 毛玻璃主题全局覆盖 |

## 后端 server/

### 入口文件

| 文件 | 说明 |
|------|------|
| `src/server.ts` | 服务器启动：监听 PORT，打印访问地址 |
| `src/app.ts` | Express 应用：中间件、路由挂载、静态文件、SPA fallback |

### 配置 config/

| 文件 | 说明 |
|------|------|
| `src/config/paths.ts` | 数据根目录、站点/页面/模块/首页/关于页路径生成函数 |
| `src/config/sites.ts` | 读取 config.yaml，根据 Host 解析数据目录 |

### 中间件 middlewares/

| 文件 | 说明 |
|------|------|
| `src/middlewares/resolve-site.ts` | 根据请求 Host 头解析 siteSlug |
| `src/middlewares/error-handler.ts` | 全局错误处理：HttpError / 500 / 404 |

### 路由 routes/

| 文件 | 说明 |
|------|------|
| `src/routes/public.routes.ts` | 路由入口：汇总挂载 render + module 路由 |
| `src/routes/render.routes.ts` | `/api/render/*path`：首页/详情页/分类页/info 页渲染 |
| `src/routes/module.routes.ts` | `/api/sites/:siteSlug/columns`、`:columnSlug/pages` |

### 服务 services/

| 文件 | 说明 |
|------|------|
| `src/services/fs-utils.ts` | 文件系统基础：readJsonFile、writeJsonFile、removePath、listDirs、listFiles |
| `src/services/site-service.ts` | 站点操作：getSites、siteExists |
| `src/services/module-service.ts` | 模块操作：getModules、getModule、getModulePages（递归扫描） |
| `src/services/page-service.ts` | 页面操作：getPage、savePage、deletePage、getHomePage、getInfoPage |
| `src/services/config-service.ts` | 配置操作：getSiteConfig、saveSiteConfig |

## 构建工具 tools/

| 文件 | 说明 |
|------|------|
| `tools/build_utils.py` | 编译工具公共模块：文件读写（JSON/YAML/Markdown）、日志、日期格式化、Frontmatter 解析、目录扫描、**序号前缀去除**（`strip_order_prefix`） |
| `tools/build_page_parser.py` | Markdown 特殊语法解析器：stats/cards/timeline/branches/chips/表格/图表/列表等语法块解析 |
| `tools/build_page.py` | 单页面编译模块：编译单 MD 文件（page.md）和多 MD 文件（meta.md + 章节）为 `data.json` |
| `tools/build_index.py` | 索引生成模块：读取 `meta.yaml` 合并元数据，扫描子目录生成 `index.json` |
| `tools/build_service_info.py` | Info 页面编译模块：编译站点 info 文件夹为 `info.json` |
| `tools/build_service.py` | 全体编译入口：扫描所有站点、并发编译页面、拷贝资源、生成各级索引 |
| `tools/rename_data_files.py` | 数据文件重命名辅助脚本 |
| `tools/editor/` | 本地 Markdown 编辑器：独立 Web 服务，支持单/多 MD 模式编辑、实时预览、图片粘贴、自动编译 |

## 文档样例 docs/

| 目录 | 说明 |
|------|------|
| `docs/single-md-example/` | 单 Markdown 格式样例：`page.md`（简单模式） |
| `docs/multi-md-example/` | 多 Markdown 格式样例：`meta.md` + `01-10` 章节文件（复杂模式） |

> 样例文件供开发者参考 Markdown 源文件格式，与 `data-format-single.md`、`data-format-multi.md` 规范对应。

## 第三方依赖

| 包名 | 用途 | 安装位置 |
|------|------|----------|
| `vue` / `vue-router` / `pinia` | 前端框架 | `client/package.json` |
| `echarts` / `vue-echarts` | 图表渲染 | `client/package.json` |
| `axios` | HTTP 请求 | `client/package.json` |
| `tailwindcss` | 原子 CSS | `client/package.json` |
| `express` / `cors` / `morgan` / `cookie-parser` | 后端框架 | `server/package.json` |
| `js-yaml` | 读取 config.yaml | `server/package.json` |
| `jsonwebtoken` / `zod` | 认证与校验 | `server/package.json` |

> 所有第三方依赖均通过 npm 安装，无 CDN 外链。
