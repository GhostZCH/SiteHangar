# SiteHanger 框架

Vue 3 + Vite + Express + TypeScript，单一 Docker 容器部署。数据与展示分离，通过扫描数据目录动态生成站点结构。

## 核心理念

- **数据与展示分离**：所有内容以 JSON 文件存储，前端通过 API 获取数据并动态渲染
- **多站点共享**：同一套代码支持多个站点，通过子域名或域名区分
- **数据驱动**：新增栏目、页面只需添加 JSON 文件，无需修改代码

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + TypeScript + Pinia + Vue Router + Tailwind CSS |
| 后端 | Node.js + Express + TypeScript |
| 数据 | JSON 文件（`my_sites_data` 目录） |
| 部署 | Docker（Node.js + Nginx + Supervisor 单容器） |

## 快速启动

详细部署命令请参阅 [docs/deployment.md](docs/deployment.md)。

简要步骤：

```powershell
docker build -t kc-v2 .
docker run -d -p 80:80 -p 5173:5173 -p 3000:3000 --name kc-v2 kc-v2
```

> 首次运行前请阅读 deployment.md 中的挂载路径和 hosts 配置说明。

## 项目文档

| 文档 | 说明 |
|------|------|
| [docs/architecture.md](docs/architecture.md) | 架构设计：部署架构、页面渲染流程、多站点支持、数据目录层级 |
| [docs/project-structure.md](docs/project-structure.md) | 代码结构：前后端文件索引、组件说明、第三方依赖 |
| [docs/api-reference.md](docs/api-reference.md) | API 接口：公开 API 列表、路由挂载方式、响应格式 |
| [docs/data-format.md](docs/data-format.md) | 数据格式总览：JSON 页面数据规范、字段说明 |
| [docs/data-format-multi.md](docs/data-format-multi.md) | 多 Markdown 格式（复杂模式）：多章节知识页面 |
| [docs/data-format-single.md](docs/data-format-single.md) | 单 Markdown 格式（简单模式）：单文件知识页面 |
| [docs/deployment.md](docs/deployment.md) | 部署运维：Docker 命令、容器管理、热重载、常见问题 |
| [docs/development-guide.md](docs/development-guide.md) | 开发规范：代码风格、**文件大小限制（200行）**、样式组织、移动端适配、内容规范 |
| [docs/changelog.md](docs/changelog.md) | 变更日志：项目演进记录、技术决策变更、待完成事项 |
