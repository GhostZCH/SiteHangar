# 变更日志

## 2026-06-27：删除 Admin 功能，新增本地 Markdown 编辑器

### 变更内容

- **删除 Admin 管理后台功能**：
  - 前端：删除 `client/src/views/admin/` 目录（AdminLoginView.vue、AdminDashboardView.vue、AdminEditorView.vue）
  - 前端：删除 `client/src/api/admin.ts`
  - 前端：从 `client/src/router/index.ts` 移除 admin 路由及子域名跳转逻辑
  - 后端：删除 `server/src/routes/admin.routes.ts`
  - 后端：删除 `server/src/middlewares/admin-auth.ts`
  - 后端：从 `server/src/app.ts` 移除 admin 子域名重定向和 CORS 白名单中的 admin 域名
  - 后端：从 `server/src/config/paths.ts` 移除 `ADMIN_CONFIG`

- **新增 `tools/editor/` 本地 Markdown 编辑器**：
  - 独立 Flask Web 服务，启动在 `http://127.0.0.1:5001`
  - 三栏布局：左侧文件树、中间编辑器、右侧实时预览
  - 支持单 MD 模式（`page.md`）和多 MD 模式（`meta.md` + 章节文件）
  - 多 MD 模式下支持新建/删除章节
  - 剪贴板图片粘贴自动保存为文件并插入 Markdown 语法
  - 编辑时防抖 3 秒自动调用编译（`build_page.py`），停止编辑后不再调用
  - Ctrl+S 保存快捷键
  - 直接读写本地文件系统，无需认证

- **文档更新**：
  - `docs/project-structure.md`：移除 admin 文件索引，新增 `tools/editor/` 说明
  - `docs/api-reference.md`：移除所有 `/api/admin/*` 接口
  - `docs/architecture.md`：移除 admin 部署描述

### 技术决策

- Admin 功能（登录认证、站点管理、触发全站编译）使用频率低，且编辑功能与展示系统耦合过深
- 将编辑器提取为独立本地工具，只在开发/编辑时使用，与线上展示系统完全解耦
- 编辑器直接调用现有 `build_page.py` 编译脚本，不修改编译逻辑，保证编译行为一致
- 单页面编译速度快，采用同步调用 + 防抖策略，无需异步任务队列

### 相关文档

- `tools/editor/main.py` — Flask 后端（文件 API + 编译调用）
- `tools/editor/static/index.html` — 编辑器页面
- `tools/editor/static/editor.css` — 暗色主题样式
- `tools/editor/static/editor.js` — 前端逻辑（文件树、编辑器、预览、自动编译）
- `tools/editor/requirements.txt` — Flask 依赖

---

## 2026-06-18：首页视觉效果优化

### 变更内容

- **主题系统增强**：
  - 各主题文件新增 `--home-bg` 和 `--home-bg-variant` 变量（首页专用背景色）
  - 恢复 `--surface` 和 `--surface-variant` 为普通页面原始浅色
  - 涉及文件：`theme-default.css`、`theme-warm.css`、`theme-cold.css`、`theme-eye-care.css`

- **粒子动画系统重构**：
  - `HomeView.vue` 中粒子系统改为持续循环模式（生成→上升→消失→自动补充）
  - `home-view.css` 中粒子动画改为 `particleFloat`（向上运动）
  - 粒子从页面下方 1/3 区域随机出现，大小 1-5px，速度 4-12s 差异化

### 技术决策

- 首页背景色与普通页面背景色分离，避免深色背景影响其他页面阅读体验
- 粒子动画采用持续循环模式，提升首页动态视觉效果

### 相关文档

- `client/src/styles/theme-*.css` — 主题变量定义
- `client/src/styles/home-view.css` — 首页粒子动画样式
- `client/src/views/HomeView.vue` — 首页粒子系统逻辑

---

## 2026-06-24：内容渲染增强与 blocks 顺序渲染机制

### 变更内容

- **新增 `blocks` 顺序渲染机制**（v2.0 数据格式）：
  - 编译脚本 `build_page_parser.py` 构建 `blocks` 数组，按原始文档顺序记录内容块
  - 前端 `SectionRenderer.vue` / `SubSectionBlock.vue` 优先按 `blocks` 顺序渲染，兼容旧数据格式
  - 解决文字与控件（表格、卡片等）渲染顺序错乱问题

- **DescriptionBlock 渲染增强**：
  - 支持 Markdown 引用块（`> `）渲染为 `<blockquote>`
  - 支持单独一行的 `**标题**` 自动转为 h4 标题（与 `### 标题` 等效）
  - 无序列表样式优化：圆角边框容器、分隔线、左侧强调竖条、hover 淡色背景
  - 自动包裹逻辑：`<li>` 无 `<ul>`/`<ol>` 包裹时自动补全

- **TimelineBlock 嵌套数组支持**：
  - `description` 支持 `(string | string[])[]` 类型
  - 字符串元素渲染为主条目（实心圆点），数组元素渲染为主条目 + 子条目（空心圆点 + 缩进）

- **编译脚本解析逻辑更新**：
  - 普通 Markdown 列表（无 `|` 分隔符）作为整体保留在 `description` 中
  - 带 `|` 分隔符的列表解析为 `list` 类型（带图标列表）
  - `cards` 和 `tables` 支持多组独立渲染（`CardItem[][]` / `TableItem[]`）

- **类型定义更新**（`content.ts`）：
  - 新增 `ContentBlock` 接口
  - `SectionContent` / `SubSectionContent` 添加 `blocks` 字段
  - `cards` 类型改为 `CardItem[][]`
  - `TimelineItem.description` 改为 `(string | string[])[]`

### 技术决策

- 引入 `blocks` 数组是为了解决原有独立字段（`description` → `stats` → `tables` → ...）固定顺序导致的渲染顺序错乱问题
- 旧数据无 `blocks` 字段时自动回退到原有字段顺序，保证向后兼容
- Timeline 嵌套数组比空格前缀更语义化，符合 JSON 规范

### 相关文档

- [docs/data-format.md](data-format.md) — 新增 `blocks` 字段说明、更新 `cards`/`tables`/`timeline` 示例
- [docs/project-structure.md](project-structure.md) — 更新组件说明（SectionRenderer、SubSectionBlock、DescriptionBlock、TimelineBlock）

---

## 2026-06-18：代码文件拆分（大文件治理）

### 变更内容

- **拆分超过 500 行的代码文件**，每个文件控制在 200 行左右，保持功能完整：
  - `tools/build_page.py` (574行) → `build_page_parser.py` (Markdown语法解析器) + `build_page.py` (页面编译主逻辑)
  - `tools/build_service.py` (526行) → `build_service_info.py` (Info页面编译) + `build_service.py` (站点构建主流程)
  - `client/src/views/HomeView.vue` (617行) → `HomeView.vue` (脚本+模板) + `styles/home-view.css` (组件样式)
- **更新 `docs/project-structure.md`**：同步新增文件说明
- **拆分原则**：按功能模块拆分，不破坏原有接口，保证每个文件功能完整

### 相关文档

- [docs/project-structure.md](project-structure.md) — 更新构建工具章节文件列表

---

### 变更内容

- **修复 `ziliudi` 站点标题栏栏目显示英文的问题**：
  - 根因：`build_service.py` 编译时容器内缺少 `yaml` 模块，导致 `read_meta` 无法读取栏目目录的 `meta.yaml`，`index.json` 中的 `hero.title` 回退为目录名（英文）
  - 修复：安装 `pyyaml` 模块，确保 `meta.yaml` 可被正确解析
- **新增 `ziliudi` 栏目目录 `meta.yaml`**：
  - `blog/meta.yaml`：定义 `hero.title: 技术博客`
  - `opensource/meta.yaml`：定义 `hero.title: 开源项目`
  - `reading/meta.yaml`：定义 `hero.title: 阅读笔记`
- **更新 `docs/data-format.md`**：
  - 添加栏目目录 `meta.yaml` 简化版示例（无 `categories` 结构）
  - 补充说明 `modules` 未定义但存在的栏目目录也会被扫描生成索引
  - 添加 `generatedAt` 字段说明

### 相关文档

- [docs/data-format.md](data-format.md) — 更新 `meta.yaml` 格式说明和字段描述

---

## 2026-06-08 ~ 2026-06-09：v2 初始构建

### 目标

将原静态站点改造为 Vue 3 + Vite + Node.js + Express 全栈应用。

### 技术决策

| 项 | 决定 |
|---|---|
| 前端 | Vue 3 + Vite + TypeScript + Pinia + Vue Router + Tailwind CSS + ECharts |
| 后端 | Node.js + Express + TypeScript |
| 数据 | JSON 文件（`my_sites_data` 目录） |
| 部署 | 单一 Docker 容器（Node.js + Nginx + Supervisor） |

### 执行记录

- **2026-06-08 23:22**：创建项目目录
- **2026-06-08 23:30**：脚手架配置就位（package.json、tsconfig、vite 配置）
- **2026-06-08 23:40**：后端源码就位（8 个路由文件 + 中间件）
- **2026-06-08 23:55**：前端源码就位（30+ 文件）
- **2026-06-09 00:30**：Docker 化完成
  - 决策变更：原计划"前后端各自一个容器 + Nginx 容器" -> 改为单一 Docker 镜像
  - 删除 `server/Dockerfile`、`client/Dockerfile`
  - 新建根 `Dockerfile`（3 阶段：client-build -> server-build -> runtime）
  - 配置 Supervisor 管理三个进程
- **2026-06-09 00:50**：README + plan.md 文档就位
- **2026-06-09 01:10**：国内源加速配置
  - 基础镜像：`docker.m.daocloud.io`
  - npm 包：`registry.npmmirror.com`
  - Prisma 引擎：`registry.npmmirror.com/-/binary/prisma`
- **2026-06-09 01:40**：修复基础镜像源（`dockerhub.azk8s.cn` 弃用，切换至 `docker.m.daocloud.io`）

## 2026-06-17：目录栏交互优化与 shortTitle 字段移除

### 变更内容

- **目录栏默认打开**：`App.vue` 中 `navExpanded` 默认值从 `false` 改为 `true`
- **目录标题显示规则调整**：
  - 展开时：显示完整标题（最多6字，超过显示"..."）
  - 收起时：显示标题前2字
  - 展开/收起按钮只显示箭头（«/»），不再显示文字
- **移除 `shortTitle` 字段**：由于 `shortTitle` 导致目录标题与内容标题不一致，完全删除该字段
  - 前端：`content.ts` 类型定义、`AppNav.vue`、`DetailView.vue`、`MobileNav.vue`、`usePageSections.ts`、`SectionRenderer.vue`、`AdminEditorView.vue`
  - 构建脚本：`build_page.py`、`build_service.py`
  - 文档：`data-format.md`、`data-format-multi.md`、`exmd-spec.md`
- **NavList 组件重构**：新增 `expanded` prop，组件内部控制展开/收起显示逻辑，不再依赖全局 CSS 类

### 相关文档

- [docs/project-structure.md](project-structure.md) — 更新 `AppNav.vue` 和 `NavList.vue` 说明
- [docs/data-format.md](data-format.md) — 删除 `shortTitle` 字段说明
- [docs/exmd-spec.md](exmd-spec.md) — 删除 `shortTitle` 相关语法和示例

---

## 2026-06-17：编译脚本重构与 Bug 修复

### 变更内容

- 重构 `tools/build_service.py`（1221 行 -> ~200 行），拆分为 4 个模块：
  - `tools/build_utils.py`：公共工具函数（日志、文件读写、Frontmatter 解析、目录扫描）
  - `tools/build_page.py`：单页面编译（单 MD 模式 + 多 MD 模式）
  - `tools/build_index.py`：索引生成（元数据合并、分类扫描）
  - `tools/build_service.py`：全体编译入口（站点扫描、并发编译、资源拷贝）
- 修复 5 个系统功能缺陷：
  1. **元数据合并**：`build_index.py` 完整合并 `meta.yaml` 中所有字段（page、hero、subtitle、introduction 等）到 `index.json`
  2. **帮助文档结构**：`info` 目录编译按二级标题拆分为 `sections`，`introduction` 置空
  3. **Wiki 元数据合并**：`wiki/index.json` 正确合并 `meta.yaml` 中的 page、hero、categories 等配置
  4. **分类目录结构**：子类型目录（如 `aerospace`、`agriculture`）不再生成 `index.json`，仅栏目目录（如 `engineering`）生成
  5. **文章内容拷贝**：页面目录下的 `data/` 和 `images/` 子目录正确拷贝到 `result` 目录
- 新增 `build_page.py` Markdown 特殊语法解析器：
  - `::: stats` -> `content.stats`
  - Markdown 表格 -> `content.tables`
  - `::: cards` -> `content.cards`
  - `::: timeline` -> `content.timeline`
  - `::: branches` -> `content.branchVisualizer`
  - `::: chips` -> `content.chips`
  - `![type](data/xxx.json)` -> `content.charts`
  - 普通文本段落 -> `content.description`（保留加粗、斜体等 Markdown 内联语法）
- 更新 `docs/project-structure.md`：更新 `tools/` 章节说明新文件结构

### 相关文档

- [docs/project-structure.md](project-structure.md) — 代码结构和构建工具说明
- [docs/data-format.md](data-format.md) — JSON 数据格式规范

## 2026-06-16：EXMD 语法规范入档

### 变更内容

- 将 `my_sites_data/spec.md`（EXMD 语法说明书）迁移至项目文档目录 `docs/exmd-spec.md`
- 更新 `docs/data-format.md`：
  - 在知识详情页章节增加 EXMD 数据来源说明
  - 添加与 `exmd-spec.md` 的交叉引用
  - 文档版本升至 1.5
- 更新 `docs/project-structure.md`：
  - 新增 `tools/` 构建工具章节，说明 `build_service.py` 的用途
  - 添加与 `exmd-spec.md` 的交叉引用
- 所有变更遵循项目规则：新增/修改 JSON 数据字段或格式 -> 同步更新 `docs/data-format.md`

### 相关文档

- [docs/exmd-spec.md](exmd-spec.md) — EXMD 完整语法参考（面向 AI 和内容创作者）
- [docs/data-format.md](data-format.md) — JSON 数据格式规范（面向前端渲染引擎）
- [docs/project-structure.md](project-structure.md) — 代码结构和构建工具说明

### 架构变更说明

原 v2 计划使用 Prisma + SQLite 数据库，后改为纯 JSON 文件驱动。数据与展示完全分离，通过扫描数据目录动态生成站点结构。

### 待完成

- [ ] 启动 Docker Desktop 验证
- [ ] `docker compose up -d --build` 构建并启动
- [ ] 验证 `http://localhost:3000` 可访问
- [ ] 在后台添加 siteSlug "www"、模块、页面
- [ ] 删除 `tools/node-v20.18.0-win-x64/` 冗余
- [ ] 备份脚本：每日 SQLite 自动备份

## 2026-06-16：文档整理

### 变更内容

- 将 README 中详细的 Docker 启动命令和访问地址说明迁移至 `docs/deployment.md`
- README 中的快速启动改为简要步骤 + 引用 deployment.md 的指引
- 保持单一信息来源，避免 README 与 deployment.md 重复
