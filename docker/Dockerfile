# 使用更简单的命令：只挂载两个目录
# 示例项目：
#   docker build -t site-hangar .
#   docker run -d --name site-hangar-example -p 80:80 -p 5173:5173 -p 3000:3000 \
#     -v e:\code\sitesanddata\my_sites\example:/app/site_data \
#     -v e:\code\sitesanddata\my_sites:/app/hanger \
#     site-hangar
# 生产环境（online/data 是软链接，需要额外挂载 my_sites_data）：
#   docker run -d --name site-hangar-online -p 80:80 -p 5173:5173 -p 3000:3000 \
#     -v e:\code\sitesanddata\my_sites\online:/app/site_data \
#     -v e:\code\sitesanddata\my_sites:/app/hanger \
#     -v e:\code\sitesanddata\my_sites_data:/app/my_sites_data \
#     site-hangar
# ============================================

FROM docker.m.daocloud.io/library/node:20-slim

WORKDIR /app

# 使用国内镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g; s|security.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources

# 安装 Nginx、Supervisor、Python3 和基础工具
# 注意：python3-minimal 足够运行 build 脚本，无需 python3-pip（避免引入 gcc 等编译依赖）
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    python3-minimal \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 配置 npm 国内镜像
RUN npm config set registry https://registry.npmmirror.com

# 全局安装 tsx（后端热重载）
RUN npm install -g tsx

# 预安装项目依赖到镜像（构建时完成，避免运行时安装）
# 使用 /opt/site-hangar-modules 作为依赖安装目录
WORKDIR /opt/site-hangar-modules

# 先复制各 package.json，利用 Docker 缓存层
COPY src/client/package.json ./client/
COPY src/server/package.json ./server/

# 安装 client 依赖
RUN cd /opt/site-hangar-modules/client && npm install

# 安装 server 依赖
RUN cd /opt/site-hangar-modules/server && npm install

# 复制 Supervisor 配置
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 复制容器引导入口脚本
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 暴露端口
# 80   - Nginx（前端入口）
# 5173 - Vite dev server（HMR，可选暴露）
# 3000 - Node 后端（内部）
EXPOSE 80 5173 3000

# 引导入口：固定调用 /app/site_data/conf/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
