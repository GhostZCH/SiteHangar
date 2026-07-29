# AI 协作指南

本文档汇总 SiteHangar 项目中对 AI 生成代码有用的信息，AI 只需阅读本文档即可了解项目全貌，减少搜索代码和远程交互次数。

## 项目定位

SiteHangar 是一个**数据驱动的多站点知识展示框架**。内容以扩展 Markdown（EXMD）编写，经编译器转换为 JSON 后由前端动态渲染成网页。同一套代码可服务多个域名站点，系统只负责展示，不提供用户登录、评论、后台管理等交互功能。

**核心约束**：
- 无数据库，所有数据以文件形式存储
- 只展示不交互：无登录注册、无评论点赞、无后台管理
- 多站点通过请求 Host 头自动匹配数据目录，未匹配返回 404

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + TypeScript + Pinia + Vue Router + Tailwind CSS + ECharts |
| 后端 | Node.js + Express + TypeScript |
| 数据 | Markdown + YAML，编译后生成 JSON 文件 |
| 线下测试 | Docker 单容器（Nginx + Vite dev server + Express + Supervisor） |
| 线上部署 | Nginx + Node.js（systemd），只部署编译产物 |

## 代码规范

### 通用要求

- 单个代码文件建议 100-200 行，最多不超过 300 行
- 优先使用成熟的第三方库，不重复造轮子
- 更新代码时，同步更新相关文档，保持一致
- 所有文本内容禁止使用 Emoji
- 使用 TypeScript，严格类型检查

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件文件 | PascalCase | `HomeView.vue`、`DescriptionBlock.vue` |
| 工具函数 | camelCase | `usePageData.ts`、`getSiteSlugByHost` |
| 路由/服务文件 | kebab-case | `render.routes.ts`、`page-service.ts` |
| 样式文件 | kebab-case | `home-view.css`、`appbar.css` |

### 前端规范

- 使用 Composition API + `<script setup>`
- 样式文件按功能模块拆分，位于 `src/client/src/styles/`
- 移动端断点：`max-width: 768px`
- 主题切换通过 CSS 变量实现，共 7 种主题

### 后端规范

- 使用 async/await，错误通过 `next(err)` 传递
- 所有 API 请求先经过 `resolveSite` 中间件解析站点
- 页面数据直接读文件，不缓存（保证内容实时生效）
- 路径遍历防护：`..` 拒绝 + 白名单正则 + `assertWithinDataRoot` 校验

### 构建工具规范

- 编译脚本为 Python，位于 `tools/builder/`
- 编译入口：`build_service.py`，支持全量、增量、预览模式
- 解析器使用 `_MarkdownParser` 类按语法块类型分发解析

## 数据组织

网站数据按“站点 → 栏目 → 一级分类 → 二级分类 → 文章”五层组织：

```
data/
├── <site-domain>/              # 站点目录，文件夹名即域名
│   ├── meta.yaml               # 站点元数据：标题、栏目、封面、标签
│   ├── image/                  # 站点级封面图
│   ├── info/                   # 站点信息页（关于、帮助等）
│   └── <module>/               # 栏目目录
│       └── <一级分类>/          # 分类目录，支持序号前缀排序
│           └── <二级分类>/
│               └── <article>/   # 文章目录
│                   ├── meta.md 或 page.md
│                   ├── image/
│                   └── data/
```

**要点**：
- `meta.yaml` 中 `modules[].id` 必须与栏目目录名一致
- `modules[].image` 只写文件名，构建时自动转为 `/api/image/<site>/<filename>`
- 分类目录支持序号前缀排序（如 `01 技术类`），展示时自动去除序号

## 内容格式：EXMD

EXMD（Extended Markdown）完全兼容标准 Markdown，并扩展了知识类内容所需的控件和布局能力。

### 标题规则

| 标题 | 作用 | 说明 |
|------|------|------|
| H1 (`#`) | 文章标题 | 正文中被忽略，页面标题只用 frontmatter `title` |
| H2 (`##`) | 章节标题 | 单 MD 模式作为 section 拆分标记；多 MD 模式被忽略 |
| H3 (`###`) | 正文子标题 | 渲染为 `<h3>` |
| H4 (`####`) | 正文二级子标题 | 渲染为 `<h4>` |
| 五级以上 | 不支持 | 不支持 |

### 扩展控件

| 扩展类型 | 引用数据 | 内嵌数据 |
|----------|---------|---------|
| 统计卡片 | `![stats](data/xxx.json)` | code 块 `stats` |
| 卡片列表 | `![cards](data/xxx.json)` | code 块 `cards` |
| 时间线 | `![timeline](data/xxx.json)` | code 块 `timeline` |
| 分支图 | `![branches](data/xxx.json)` | code 块 `branches` |
| 标签芯片 | `![chips](data/xxx.json)` | code 块 `chips` |
| 树状图 | `![tree](data/xxx.json)` | code 块 `tree` |
| 图表 | `![bar](data/xxx.json)`、`![pie](...)`、`![line](...)` | code 块 `bar`/`pie`/`line` |
| 分栏 | `===== ... ----- ... =====` | 最多 4 栏，不可嵌套 |

**已废弃语法**：`:::` 围栏块语法已废弃，统一使用 JSON 文件引用或 Markdown Code 块。

### 两种文章模式

| 模式 | 文件结构 | 适用场景 | 优点 |
|------|---------|---------|------|
| 单文件 | `page.md` + `image/` + `data/` | 简短笔记、备忘 | 人工快速编辑 |
| 多文件 | `meta.md` + `01-xxx.md` + `image/` + `data/` | 长文 | AI 并行生成，局部修改快速省 token |

## 编译流程

```
Markdown 源数据
    ↓ build_service.py 编译
JSON 数据 + 索引文件
    ↓ Express 读取
前端 Vue 动态渲染
```

- **编译工具**：`tools/builder/build_service.py`
- **编译产物**：站点首页 `index.json`、栏目首页 `index.json`、文章 `data.json`、附件资源
- **编译输出目录**：由 `config.yaml` 的 `buildOutputDir` 指定
- **优势**：内容修改后重新编译即可生效，无需重启服务

## 页面渲染流程

### 线下调试

```
用户请求 URL
    -> Nginx（端口 80）
    -> Nginx 反代到 Vite dev server（端口 5173）
    -> Vite dev server 返回前端页面，启动 HMR WebSocket
    -> Vue Router 匹配路由，加载视图组件
    -> 视图组件调用 API（/api/render/*path）
    -> Nginx 反代 /api/ 到 Express 后端（端口 3000）
    -> Express 后端从 DATA_ROOT 目录读取 JSON 数据文件
    -> Vue 组件根据数据内容动态渲染页面
```

### 线上部署

```
用户请求 URL
    -> Nginx（端口 80 / 443）
    -> Nginx 直接托管前端 dist 静态文件（SPA fallback 到 index.html）
    -> Vue Router 匹配路由，加载视图组件
    -> 视图组件调用 API（/api/render/*path）
    -> Nginx 反代 /api/ 到 Express 后端（端口 3000）
    -> Express 后端从 DATA_ROOT 目录读取 JSON 数据文件
    -> Vue 组件根据数据内容动态渲染页面
```

## 页面类型与路由映射

| 页面类型 | URL 路由 | 渲染视图 | 后端 `type` |
|----------|----------|----------|-------------|
| 首页 | `/` | HomeView（模块卡片） | `home` |
| 分类页 | `/:moduleSlug` | CategoryView | `category` |
| 详情页 | `/:moduleSlug/:path*` | DetailView | `detail` |
| 关于页 | `/info` | DetailView | `detail` |

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/render/*path` | GET | 通配渲染：首页 / 详情页 / 分类页 / info 页 |
| `/api/sites/:siteSlug/columns` | GET | 列出站点所有栏目 |
| `/api/sites/:siteSlug/columns/:columnSlug/pages` | GET | 列出栏目下所有页面 |
| `/api/image/:site/:filename` | GET | 站点级图片 |
| `/api/page-asset/:site/*path` | GET | 页面级静态资源 |
| `/api/config` | GET | 读取网站公开配置（ICP 等） |

**响应格式**（`/api/render/*path`）：

```json
{
  "site": { "slug": "site-slug" },
  "column": { "slug": "wiki" },
  "page": { "slug": "xxx", "title": "页面标题" },
  "type": "home | category | detail",
  "data": { "...": "页面数据（modules / categories / sections 等）" }
}
```

**错误响应**：

```json
{ "error": "NOT_FOUND" }
```

常见 HTTP 状态码：200（成功）、400（非法路径）、403（禁止访问）、404（资源未找到）、500（服务器内部错误）

## 多站点机制

- 后端通过 `resolveSite` 中间件解析请求 Host 头
- 优先完整域名匹配数据目录名，其次匹配第一段子域名
- 未匹配到站点时返回 404 `SITE_NOT_FOUND`
- `localhost` 不会匹配任何站点目录

## 项目目录结构

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
│   └── build/           # 编译输出
├── tools/               # 工具
│   ├── builder/         # 编译脚本（build_service.py 等）
│   └── editor/          # 本地 Markdown 编辑器
└── docs/                # 项目文档
```

## 关键文件速查

### 前端

| 文件 | 作用 |
|------|------|
| `src/client/src/main.ts` | Vue 应用入口 |
| `src/client/src/App.vue` | 根组件 |
| `src/client/src/router/index.ts` | 路由表 |
| `src/client/src/stores/site.ts` | Pinia store |
| `src/client/src/api/public.ts` | 公开 API 封装 |
| `src/client/src/composables/usePageData.ts` | 页面数据加载 |
| `src/client/src/views/HomeView.vue` | 首页 |
| `src/client/src/views/DetailView.vue` | 详情页 |
| `src/client/src/components/content/SectionRenderer.vue` | 章节渲染器 |

### 后端

| 文件 | 作用 |
|------|------|
| `src/server/src/server.ts` | 服务器启动 |
| `src/server/src/app.ts` | Express 应用 |
| `src/server/src/config/paths.ts` | 数据路径配置 |
| `src/server/src/config/sites.ts` | 站点解析 |
| `src/server/src/middlewares/resolve-site.ts` | Host 解析中间件 |
| `src/server/src/routes/render.routes.ts` | 渲染路由 |
| `src/server/src/services/page-service.ts` | 页面操作 |

### 构建工具

| 文件 | 作用 |
|------|------|
| `tools/builder/build_service.py` | 全体编译入口 |
| `tools/builder/build_page_parser.py` | Markdown 特殊语法解析器 |
| `tools/builder/build_page.py` | 单页面编译模块 |
| `tools/builder/build_index.py` | 索引生成 |

## 编译产物数据结构

编译后生成两类 JSON 文件：

| 文件 | 位置 | 内容 |
|------|------|------|
| `index.json` | `DATA_ROOT/<site>/` | 站点首页数据：`page`、`hero`、`modules`（栏目列表） |
| `index.json` | `DATA_ROOT/<site>/<column>/` | 栏目首页数据：`page`、`categories`、`recent` |
| `data.json` | `DATA_ROOT/<site>/<column>/.../<article>/` | 文章内容：`page`、`hero`、`introduction`、`sections` |

`sections` 中的 `content.blocks` 按原始文档顺序记录内容块，前端按此顺序渲染。

## 图片资源引用

| 类型 | 存放位置 | 引用方式 |
|------|---------|---------|
| 站点级图片 | `<site>/image/` | `meta.yaml` 中 `modules[].image` 只写文件名，构建时转为 `/api/image/<site>/<filename>` |
| 页面级图片 | `<article>/image/` | EXMD 中引用 `image/xxx.jpg`，构建后通过 `/api/page-asset/<site>/<path>/image/xxx.jpg` 访问 |

## 配置文件

`config.yaml` 主要配置项：

| 配置项 | 说明 |
|--------|------|
| `buildOutputDir` | 编译输出目录，后端通过 `DATA_ROOT` 读取 |
| `icp` | ICP 备案号，渲染到页面底部 |

后端通过环境变量 `CONFIG_FILE` 定位 `config.yaml`。

## 环境差异速查

| 环节 | 线下调试 | 线上部署 |
|---|---|---|
| 前端来源 | Vite dev server（端口 5173） | Nginx 托管的 dist 静态文件 |
| 热更新 | 支持 HMR | 无 HMR，更新需重新构建部署 |
| 前端构建 | 无需构建，Vite 实时编译 | 需先执行 `npm run build` |
| 后端运行 | `tsx watch` 自动重启 | `node dist/server.js` 由 systemd 管理 |
| Nginx | 反代 Vite 和 API | 托管 dist + 反代 API |

## 常用命令速查

```powershell
# 编译数据
python tools/builder/build_service.py --clean --data-root example/data --output-dir example/build

# 构建前端
cd src/client && npm install && npm run build

# 编译后端
cd src/server && npm install && npm run build

# 线下启动容器
docker run -d --name site-hangar -p 80:80 -p 5173:5173 -p 3000:3000 `
  -v <项目根目录>\example:/app/site_data `
  -v <项目根目录>:/app/hanger `
  site-hangar

# 线上启动后端
CONFIG_FILE=<应用目录>/my_sites_data/conf/config.yaml NODE_ENV=production PORT=3000 node dist/server.js
```

## 设计决策与注意事项

- **页面数据直接读文件、不缓存**：保证内容实时生效，缓存设施仅用于写操作后的失效清理
- **KaTeX 懒加载**：动态 import，首屏不打包公式库，加载完成后自动重渲染
- **ECharts 主题适配**：从 `getComputedStyle` 读取 CSS 变量实色值，ECharts 无法解析 CSS 变量
- **路径遍历防护**：`..` 拒绝 + 白名单正则 + `assertWithinDataRoot` 最终路径校验
- **无 Admin 后台**：所有修改通过编辑数据文件完成，与线上展示系统完全解耦
- **本地编辑器独立**：`tools/editor/` 是独立 Flask 服务，只在开发/编辑时使用

## 相关文档

| 文档 | 说明 |
|------|------|
| [01.requirement.md](01.requirement.md) | 需求：概述、特性、功能需求、非功能需求 |
| [02.architecture.md](02.architecture.md) | 架构设计：技术栈、代码模块、数据流、API 流程 |
| [03.deployment.md](03.deployment.md) | 部署运维：线下测试、线上部署、容器管理 |
| [04.data-format.md](04.data-format.md) | 数据格式：文件夹结构、EXMD 语法、编译结果 |
| [exmd-for-ai.md](exmd-for-ai.md) | EXMD 生成规范：面向 AI 的内容生成指南 |
| [05.changelog.md](05.changelog.md) | 变更日志：项目演进记录 |
