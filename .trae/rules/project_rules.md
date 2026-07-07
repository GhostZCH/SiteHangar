# 项目要求

这是一个博客系统，数据和展示分离，这个项目只是个展示数据的网站系统，前端使用 Vue + vite实现。
后端使用 Node.js 实现。全部数据使用文件系统存储，不涉及数据库。开发前请先阅读文档

原始数据在 E:\code\sitesanddata\my_sites_data\data 目录下，编译结果在 E:\code\sitesanddata\my_sites_data\result 目录下。

## 项目文档索引

项目文档统一存放在 `docs/` 目录下：

| 文档 | 说明 |
|------|------|
| `docs/architecture.md` | 架构设计：部署架构、页面渲染流程、多站点支持、数据目录层级 |
| `docs/project-structure.md` | 代码结构：前后端文件索引、组件说明、第三方依赖 |
| `docs/api-reference.md` | API 接口：公开 API 列表、路由挂载方式、响应格式 |
| `docs/data-format.md` | 数据格式：JSON 页面数据规范、字段说明、完整示例 |
| `docs/deployment.md` | 部署运维：Docker 命令、容器管理、热重载、常见问题 |
| `docs/development-guide.md` | 开发规范：代码风格、文件命名、样式组织、移动端适配、内容规范 |
| `docs/changelog.md` | 变更日志：项目演进记录、技术决策变更、待完成事项 |

详细内容请参阅对应文档。

## 编码规范

- 如果可以使用第三方插件的，尽量使用第三方插件。
- 单个文件建议100-200行代码，最多不超过300行。
- 完成代码前先阅读文档，了解架构和规范
- 涉及以下变更时，必须同步更新对应文档：
- **禁止网页原地编译**：即输入和输出文件夹相同，不能污染原始数据

| 变更类型 | 需更新的文档 |
|----------|-------------|
| 调整技术架构、部署方式、容器进程 | `docs/architecture.md` + `docs/deployment.md` |
| 新增/删除/重命名代码文件或目录 | `docs/project-structure.md` |
| 新增/修改 API 接口 | `docs/api-reference.md` |
| 新增/修改 JSON 数据字段或格式 | `docs/data-format.md` |
| 修改 Docker 命令、端口、挂载路径 | `docs/deployment.md` |
| 修改代码风格、文件命名、样式规范、内容规范 | `docs/development-guide.md` |
| 完成重要功能或做出技术决策变更 | `docs/changelog.md` |