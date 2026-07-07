# 开发规范

## 代码风格

- 使用 TypeScript，严格类型检查
- 前端使用 Composition API + `<script setup>`
- 后端使用 async/await，错误通过 next(err) 传递

## 文件命名

- 组件：PascalCase（如 `SectionRenderer.vue`）
- 工具函数：camelCase（如 `readJsonFile.ts`）
- 路由/服务：kebab-case（如 `render.routes.ts`）

## 状态管理

- 前端使用 Pinia，`useSiteStore` 管理当前站点和栏目列表
- 后端无状态，数据完全存储在 JSON 文件中

## 文件大小规范

- **每个代码文件控制在 200 行左右，最多不超过 500 行**
- 当文件超过 200 行时，应按功能模块拆分为多个小文件
- 拆分后的文件命名应清晰反映其职责，如 `responsive-mobile-layout.css`、`theme-night.css`
- 此规范适用于所有 CSS、TypeScript、JavaScript 和 Vue 文件（JSON 数据文件除外）

## 样式文件组织

所有样式文件位于 `client/src/styles/`，按功能模块拆分：

| 文件 | 职责 |
|------|------|
| `main.css` | CSS 变量与主题定义（默认、warm、cold、night、glass、eye-care、3d） |
| `base.css` | 基础重置与 body 样式 |
| `responsive.css` | **移动端适配样式**（`@media (max-width: 768px)`） |
| `content.css` | 内容区布局（section、subsection、description、introduction） |
| `hero.css` | 页面头部（hero）样式 |
| `navigation.css` | 左侧导航栏（nav-drawer）样式 |
| `appbar.css` | 顶部标题栏（appbar）样式 |
| `pages.css` | 首页与分类页样式 |
| `components.css` | 通用组件（cards、tables、lists、chips） |
| `timeline.css` | 时间线组件样式 |
| `charts.css` | ECharts 图表容器样式 |
| `glass-theme.css` | 玻璃主题专属样式 |
| `theme-switcher.css` | 主题切换器样式 |

## 移动端适配规范

- 移动端断点：`max-width: 768px`
- 桌面端 `.detail-page` 有 `margin-left: var(--nav-width)`（68px）为左侧导航栏留白
- **移动端必须覆盖 `.detail-page` 的左外边距**：`margin-left: 0 !important`
- 底部章节导航栏（`.mobile-nav-bar`）仅在移动端显示，固定定位在页面底部
- 内容区在移动端需保留底部 padding（如 `padding-bottom: 72px`）避免被导航栏遮挡
- 各主题（night、glass、3d 等）的移动端覆盖样式也需要同步维护

## 内容规范

### 严禁使用 Emoji 表情

- **所有页面内容严禁使用 Emoji 表情符号**（如 💔、🏛️、👩 等）
- 列表图标、卡片图标等应使用文字描述、SVG 图标或留空，禁止使用 Emoji
- 此规则适用于所有 JSON 数据文件中的 `icon` 字段、`description` 字段以及任何文本内容

### 图片与可视化

- 鼓励使用图片增强页面视觉效果：卡片图片、时间轴图片、背景图等
- 鼓励使用 ECharts 图表（柱状图、饼图、折线图等）展示数据
- 图片可使用在线 URL 或存放于页面目录的 `images/` 文件夹中

## 测试页面规范

- **所有测试页面必须放在对应站点的 `data/<site>/tools/` 目录下**，不得在正式内容模块中创建测试页面
- 测试页面目录名使用小写形式，如 `branch-test`、`chart-demo` 等
- 测试页面同样遵循数据驱动架构，包含 `data.json` 文件
- 访问路径为 `/tools/<test-name>`

## 用户输入提示词执行规则

- 新建一个关于某个主题的 Wiki 页面需要使用 create-page 技能，并严格遵守技能要求
- 每个知识页面的目录名必须是主题名称的小写形式，如 `africa`、`china-geography` 等
- 新页面必须放在对应站点的对应模块目录下，例如 `data/<site>/{wiki,topic,tools}/`
- **严禁直接修改 `client/src/` 下的核心渲染组件。** 所有内容变更应通过修改 JSON 数据文件实现
- 所有样式修改应通过 `client/src/styles/` 下的 CSS 文件进行
- **关于页面（/info）的内容通过修改 `data/<site>/info.json` 来更新**
