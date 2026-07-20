# 部署与运维

本文档说明 SiteHangar 的 Docker 构建、容器启动、挂载路径、热重载和常见问题。

## 目录约定

本框架以 **example/** 目录作为示例站点运行，同时支持与项目规则一致的独立数据目录。

| 环境 | 站点数据目录 | 编译输出目录 | 项目代码目录 |
|------|-------------|-------------|-------------|
| 示例（example） | `example/` | `example/build/` | 项目根目录 |
| 生产（按项目规则） | `E:\code\sitesanddata\my_sites_data\data` | `E:\code\sitesanddata\my_sites_data\result` | 项目根目录 |

无论哪种环境，容器内统一使用 `/app/site_data` 作为站点数据目录，`/app/hanger` 作为项目代码目录。`config.yaml` 的 `buildOutputDir` 决定网站服务读取的编译结果路径。

更多架构说明请参阅 [architecture.md](architecture.md)。

## Docker 构建与启动

### 构建镜像

Dockerfile 位于 `docker/Dockerfile`，构建命令：

```powershell
docker build -t site-hangar -f docker/Dockerfile .
```

### 运行示例容器

```powershell
# 1. 先编译示例数据
python tools/builder/build_service.py --clean --data-root example/data --output-dir example/build

# 2. 启动容器（挂载 example 作为站点数据，项目根目录作为代码）
docker run -d --name site-hangar-example -p 80:80 -p 5173:5173 -p 3000:3000 `
  -v e:\code\sitesanddata\site_hangar\example:/app/site_data `
  -v e:\code\sitesanddata\site_hangar:/app/hanger `
  site-hangar
```

### 挂载路径说明

| 宿主机路径 | 容器内路径 | 说明 |
|-----------|-----------|------|
| `example/` 或 `my_sites_data/data/` 的父目录 | `/app/site_data` | 站点数据（包含 `conf/`、`data/`、`build/`） |
| 项目根目录 | `/app/hanger` | 项目代码（`src/client`、`src/server` 等） |

如果站点数据目录内有软链接指向 `my_sites_data/`（如 `online/data`），需要额外挂载 `-v e:\code\sitesanddata\my_sites_data:/app/my_sites_data`。

## 访问地址

| 地址 | 说明 |
|------|------|
| `http://travel.example.local` | 示例项目 - 中国旅游 |
| `http://science.example.local` | 示例项目 - 理科知识 |
| `http://localhost` | 默认首页 |
| `http://localhost:5173` | Vite dev server（直接访问） |

本地测试域名：需在宿主机 `hosts` 文件中添加 `travel.example.local`、`science.example.local` 指向 `127.0.0.1`：

```
127.0.0.1  travel.example.local science.example.local
```

## 容器进程管理

容器内由 Supervisor 管理三个进程：

| 进程 | 端口 | 说明 |
|------|------|------|
| backend | 3000 | Express 后端，提供 API |
| vite | 5173 | Vite dev server，支持 HMR |
| nginx | 80 | Nginx 反代，统一入口 |

更多架构说明请参阅 [architecture.md](architecture.md)。

## 启动流程

容器启动时执行以下步骤：

1. **引导入口**：固定调用 `/app/site_data/conf/entrypoint.sh`
2. **读取配置**：从 `/app/site_data/conf/config.yaml` 读取 `buildOutputDir`
3. **复制 node_modules**：将镜像内预装的依赖复制到 `/app/hanger/src/client/node_modules` 和 `/app/hanger/src/server/node_modules`
4. **复制 nginx.conf**：从 `/app/site_data/conf/nginx.conf` 复制到 Nginx 配置目录
5. **启动 Supervisor**：管理 backend、vite、nginx 三个进程

网站只使用编译结果，启动时不自动编译。修改源数据后需手动运行 `build_service.py` 重新编译。

## 数据编译命令

```powershell
# 全量编译示例数据
python tools/builder/build_service.py --clean --data-root example/data --output-dir example/build

# 增量编译
python tools/builder/build_service.py --data-root example/data --output-dir example/build

# 预览模式（不写入文件）
python tools/builder/build_service.py --dry-run --data-root example/data --output-dir example/build
```

## 热重载与目录更新

- **前端**：挂载本地代码目录，Vite HMR 通过 Nginx WebSocket 代理正常工作
- **后端**：使用 `tsx watch` 实现文件变更自动重启
- **Nginx 配置**：`nginx.conf` 在容器启动时从 `/app/site_data/conf/` 复制，修改后重启容器生效
- **node_modules**：首次启动时从镜像复制到 `/app/hanger/src/client/node_modules` 和 `/app/hanger/src/server/node_modules`，本地代码目录会出现这两个文件夹
- **数据目录变更**：新增栏目、分类或页面后，需**重新编译**并刷新页面生效

## 停止与日志

```powershell
# 停止容器
docker stop site-hangar-example

# 查看日志
docker logs site-hangar-example
```

Supervisor 会将所有进程日志输出到 stdout。

## 常见问题

### Q: 容器启动后访问 localhost 显示 404？
A: 检查 Nginx 配置是否正确复制到 `/etc/nginx/sites-enabled/default`，以及 Vite 是否正常启动。

### Q: 数据修改后没有实时生效？
A: 后端每次请求都会读取文件，应该实时生效。如果栏目结构变更（新增/删除栏目），需要刷新页面重新获取栏目列表。

### Q: 编译失败怎么办？
A: 检查 `build_service.py` 输出日志。常见原因：
- 源数据目录不存在或权限不足
- Markdown 文件格式错误
- 磁盘空间不足

### Q: 本地 hosts 已配置但子域名无法访问？
A: 确认 `config.yaml` 的 `allowedHosts` 包含该域名，且 Nginx 配置中有对应 server_name。

## 相关文档

- [architecture.md](architecture.md) — 架构设计与数据流
- [exmd.md](exmd.md) — 内容格式说明
- [changelog.md](changelog.md) — 变更日志
