# Example 示例项目

这是一个示例站点，包含两个演示项目：

- **中国旅游** (`travel`) — 中国人文景观、自然景观和休闲放松景点
- **理科知识** (`science`) — 数学、物理、化学、生物等理科知识

## 目录结构

```
example/
├── conf/                # 站点配置
│   ├── config.yaml      # buildOutputDir、icp
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
python tools/builder/build_service.py --clean --data-root example/data --output-dir example/build

# 2. 构建镜像（首次或 Dockerfile 变更后）
docker build -t site-hangar .

# 3. 启动 Docker 容器（只挂载两个目录）
docker run -d --name site-hangar-example -p 80:80 -p 5173:5173 -p 3000:3000 `
  -v e:\code\sitesanddata\site_hangar\example:/app/site_data `
  -v e:\code\sitesanddata\site_hangar:/app/hanger `
  site-hangar
```

## 文件说明

| 路径 | 说明 |
|------|------|
| `example/conf/config.yaml` | 站点配置：`buildOutputDir`、`icp` |
| `example/conf/entrypoint.sh` | 容器入口脚本，读取 `config.yaml` 并启动服务 |
| `example/conf/nginx.conf` | Nginx 虚拟主机配置，映射子域名到站点 |
| `example/data/` | 源数据目录（Markdown 文件） |
| `example/build/` | 编译输出目录，供网站服务读取 |

## 常用命令

### 编译数据

```powershell
# 全量编译
python tools/builder/build_service.py --clean --data-root example/data --output-dir example/build

# 增量编译
python tools/builder/build_service.py --data-root example/data --output-dir example/build

# 预览模式
python tools/builder/build_service.py --dry-run --data-root example/data --output-dir example/build
```

### Docker 管理

```powershell
# 构建镜像（首次或 Dockerfile 变更后）
docker build -t site-hangar .

# 启动容器（只挂载两个目录）
docker run -d --name site-hangar-example -p 80:80 -p 5173:5173 -p 3000:3000 `
  -v e:\code\sitesanddata\site_hangar\example:/app/site_data `
  -v e:\code\sitesanddata\site_hangar:/app/hanger `
  site-hangar

# 重启容器（修改代码后生效）
docker restart site-hangar-example

# 查看日志
docker logs site-hangar-example --tail 50

# 停止并删除
docker stop site-hangar-example
docker rm -f site-hangar-example
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
