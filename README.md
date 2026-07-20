# SiteHangar

SiteHangar 是一个**数据驱动的多站点博客框架**。前端基于 Vue 3 + Vite，后端基于 Node.js + Express，所有内容以 Markdown/JSON 文件存储，无需数据库，通过 Docker 单一容器部署。

## 核心理念

- **数据与展示分离**：内容以 Markdown 编写，编译为 JSON 后由前端动态渲染，修改内容无需改动代码。
- **多站点共享**：同一套代码支持多个站点，通过域名或子域名区分，每个站点拥有独立的栏目和内容。
- **数据驱动**：新增栏目、分类或页面只需添加数据文件，系统自动生成导航和页面结构。

## 技术实现

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + TypeScript + Pinia + Vue Router + Tailwind CSS + ECharts |
| 后端 | Node.js + Express + TypeScript |
| 数据 | Markdown + YAML，编译后生成 JSON 文件 |
| 部署 | Docker 单容器（Nginx + Vite dev server + Express + Supervisor） |

### 架构一句话

用户请求 → Nginx → Vite dev server → Vue Router → 调用 `/api/render/*` → Express 读取 JSON 数据 → 动态渲染页面。

## 快速开始

```powershell
# 1. 编译示例数据
python tools/builder/build_service.py --clean --data-root example/data --output-dir example/build

# 2. 构建 Docker 镜像
docker build -t site-hangar -f docker/Dockerfile .

# 3. 启动容器
docker run -d --name site-hangar-example -p 80:80 -p 5173:5173 -p 3000:3000 `
  -v e:\code\sitesanddata\site_hangar\example:/app/site_data `
  -v e:\code\sitesanddata\site_hangar:/app/hanger `
  site-hangar
```

首次运行前请阅读 [docs/deployment.md](docs/deployment.md) 了解挂载路径、hosts 配置和常见问题的详细说明。

## 项目文档

| 文档 | 说明 |
|------|------|
| [docs/architecture.md](docs/architecture.md) | 架构设计：技术栈、代码模块、文件作用、数据流、API 流程、多站点、目录层级 |
| [docs/deployment.md](docs/deployment.md) | 部署运维：Docker 命令、容器管理、热重载、常见问题 |
| [docs/exmd.md](docs/exmd.md) | EXMD 格式说明：面向内容创作者的扩展 Markdown 语法，包含单文档和多文档模式 |
| [docs/changelog.md](docs/changelog.md) | 变更日志：项目演进记录和技术决策变更 |
| [docs/content-optimization-suggestion.md](docs/content-optimization-suggestion.md) | 内容优化建议 |
