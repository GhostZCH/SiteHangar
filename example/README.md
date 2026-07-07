# Example 示例项目

这是一个示例站点，包含两个演示项目：

- **中国旅游** (`travel`) — 中国人文景观、自然景观和休闲放松景点
- **理科知识** (`science`) — 数学、物理、化学、生物等理科知识

## 目录结构

```
example/
├── conf/                # 站点配置
│   ├── config.yaml      # buildOutputDir、icp、allowedHosts
│   ├── entrypoint.sh    # 容器入口脚本
│   └── nginx.conf       # Nginx 虚拟主机配置
├── data/                # 源数据目录（Markdown 文件）
│   ├── science/         # 理科知识站点
│   └── travel/          # 中国旅游站点
├── build/               # 编译输出目录（JSON 数据）
└── README.md
```

## 快速开始

```powershell
# 1. 编译源数据
python tools/build_service.py --clean --data-root example/data --output-dir example/build

# 2. 构建镜像（首次或 Dockerfile 变更后）
docker build -t kc-v2 .

# 3. 启动 Docker 容器（只挂载两个目录）
docker run -d --name kc-v2-example -p 80:80 -p 5173:5173 -p 3000:3000 `
  -v e:\code\sitesanddata\my_sites\example:/app/site_data `
  -v e:\code\sitesanddata\my_sites:/app/hanger `
  kc-v2
```

## 文件说明

| 路径 | 说明 |
|------|------|
| `example/conf/config.yaml` | 站点配置：`buildOutputDir`、`icp`、`allowedHosts` |
| `example/conf/entrypoint.sh` | 容器入口脚本，读取 `config.yaml` 并启动服务 |
| `example/conf/nginx.conf` | Nginx 虚拟主机配置，映射子域名到站点 |
| `example/data/` | 源数据目录（Markdown 文件） |
| `example/build/` | 编译输出目录，供网站服务读取 |

## 常用命令

### 编译数据

```powershell
# 全量编译
python tools/build_service.py --clean --data-root example/data --output-dir example/build

# 增量编译
python tools/build_service.py --data-root example/data --output-dir example/build

# 预览模式
python tools/build_service.py --dry-run --data-root example/data --output-dir example/build
```

### Docker 管理

```powershell
# 构建镜像（首次或 Dockerfile 变更后）
docker build -t kc-v2 .

# 启动容器（只挂载两个目录）
docker run -d --name kc-v2-example -p 80:80 -p 5173:5173 -p 3000:3000 `
  -v e:\code\sitesanddata\my_sites\example:/app/site_data `
  -v e:\code\sitesanddata\my_sites:/app/hanger `
  kc-v2

# 重启容器（修改代码后生效）
docker restart kc-v2-example

# 查看日志
docker logs kc-v2-example --tail 50

# 停止并删除
docker stop kc-v2-example
docker rm -f kc-v2-example
```

## 访问地址

启动容器后，在本地 hosts 文件添加：

```
127.0.0.1  travel.example.local science.example.local
```

然后访问：

- `http://travel.example.local` — 中国旅游首页
- `http://science.example.local` — 理科知识首页
- `http://travel.example.local/culture` — 人文景观栏目
- `http://science.example.local/math` — 数学栏目

## 注意事项

1. **编译与运行分离**：网站服务只读取 `build/` 目录，不直接读取 `data/`。修改数据后需要重新编译。
2. **目录名规范**：栏目下的分类目录建议使用 `01 名称`、`02 名称` 格式，便于排序。
3. **图片资源**：站点图片放在 `data/{site}/image/`，编译时会自动复制到 `build/`。
4. **关于页面**：每个站点需要创建 `info/` 目录存放关于页面数据。
5. **node_modules**：首次启动时，容器会将镜像内预装的依赖复制到 `client/node_modules` 和 `server/node_modules` 目录下，这是正常现象。
