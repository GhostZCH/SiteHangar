#!/bin/bash
set -e

# 通用站点入口脚本
# 项目代码目录挂载到 /app/hanger
# 站点数据目录挂载到 /app/site_data

PROJECT_DIR="/app/hanger"
SITE_DIR="/app/site_data"
CONFIG_FILE="$SITE_DIR/conf/config.yaml"

echo "[entrypoint] SITE_DIR: $SITE_DIR"
echo "[entrypoint] CONFIG_FILE: $CONFIG_FILE"

# 处理 online/data 软链接：如果指向的 my_sites_data 被挂载到 /app/my_sites_data，重建链接
if [ -L "$SITE_DIR/data" ] && [ ! -e "$SITE_DIR/data" ]; then
    echo "[entrypoint] Site data is a symlink, checking target ..."
    if [ -d "/app/my_sites_data/data" ]; then
        echo "[entrypoint] Re-linking site data to /app/my_sites_data/data"
        rm -f "$SITE_DIR/data"
        ln -s /app/my_sites_data/data "$SITE_DIR/data"
    else
        echo "[entrypoint] WARNING: /app/my_sites_data/data not found, site data symlink may be broken"
    fi
fi

if [ -f "$CONFIG_FILE" ]; then
    echo "[entrypoint] Using config file: $CONFIG_FILE"
    # 读取 buildOutputDir，不依赖 PyYAML
    BUILD_OUTPUT_DIR=$(grep -E '^buildOutputDir:' "$CONFIG_FILE" | sed 's/^buildOutputDir:[[:space:]]*//' | tr -d '"' | tr -d "'" | tr -d ' ')
else
    echo "[entrypoint] WARNING: Config file not found at $CONFIG_FILE, using default build dir"
    BUILD_OUTPUT_DIR=""
fi

# 默认使用站点目录下的 build 文件夹
if [ -z "$BUILD_OUTPUT_DIR" ]; then
    BUILD_OUTPUT_DIR="$SITE_DIR/build"
fi

echo "[entrypoint] BUILD_OUTPUT_DIR set to: $BUILD_OUTPUT_DIR"

# 镜像内预装的依赖目录
MODULES_DIR="/opt/kc-v2-modules"

# 将镜像内的 node_modules 复制到挂载目录（如果挂载目录为空）
# 使用 Volume 挂载 node_modules，本地不会出现该文件夹
copy_modules_if_empty() {
    local target="$1"
    local source="$2"
    if [ ! -d "$target/node_modules" ] || [ -z "$(ls -A "$target/node_modules" 2>/dev/null)" ]; then
        echo "[entrypoint] Copying node_modules to $target ..."
        mkdir -p "$target/node_modules"
        cp -a "$source/node_modules/." "$target/node_modules/"
    else
        echo "[entrypoint] node_modules already exists at $target/node_modules, skipping copy"
    fi
}

copy_modules_if_empty "$PROJECT_DIR/client" "$MODULES_DIR/client"
copy_modules_if_empty "$PROJECT_DIR/server" "$MODULES_DIR/server"

# 从 config 所在目录复制 nginx.conf 到 Nginx 配置目录
CONFIG_DIR=$(dirname "$CONFIG_FILE")
if [ -f "$CONFIG_DIR/nginx.conf" ]; then
    echo "[entrypoint] Copying nginx.conf from $CONFIG_DIR..."
    cp "$CONFIG_DIR/nginx.conf" /etc/nginx/sites-available/default
    rm -f /etc/nginx/sites-enabled/default
    ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
else
    echo "[entrypoint] WARNING: nginx.conf not found in $CONFIG_DIR, using default Nginx config"
fi

# 启动 Supervisor
export PROJECT_DIR="$PROJECT_DIR"
export DATA_ROOT="$BUILD_OUTPUT_DIR"
export CONFIG_FILE="$CONFIG_FILE"
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
