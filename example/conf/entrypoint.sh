#!/bin/bash
set -e

PROJECT_DIR="/app/hanger"
SITE_DIR="/app/site_data"
CONFIG_FILE="$SITE_DIR/conf/config.yaml"
BUILD_OUTPUT_DIR="/app/site_data/build"

echo "[entrypoint] SITE_DIR: $SITE_DIR"
echo "[entrypoint] BUILD_OUTPUT_DIR: $BUILD_OUTPUT_DIR"

# 将镜像内的 node_modules 复制到挂载目录（兼容 Windows 挂载的代码）
MODULES_DIR="/opt/site-hangar-modules"
copy_modules_if_empty() {
    local target="$1"
    local source="$2"
    if [ ! -d "$target/node_modules" ] || [ -z "$(ls -A "$target/node_modules" 2>/dev/null)" ]; then
        echo "[entrypoint] Copying node_modules to $target ..."
        mkdir -p "$target/node_modules"
        cp -a "$source/node_modules/." "$target/node_modules/"
    else
        echo "[entrypoint] node_modules already exists at $target/node_modules, skipping"
    fi
}

copy_modules_if_empty "$PROJECT_DIR/src/client" "$MODULES_DIR/client"
copy_modules_if_empty "$PROJECT_DIR/src/server" "$MODULES_DIR/server"

# 应用自定义 Nginx 配置
if [ -f "$SITE_DIR/conf/nginx.conf" ]; then
    echo "[entrypoint] Copying nginx.conf..."
    cp "$SITE_DIR/conf/nginx.conf" /etc/nginx/sites-available/default
    rm -f /etc/nginx/sites-enabled/default
    ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
fi

# 启动 Supervisor
export PROJECT_DIR="$PROJECT_DIR"
export CONFIG_FILE="$CONFIG_FILE"
export BUILD_OUTPUT_DIR="$BUILD_OUTPUT_DIR"
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
