#!/bin/bash
set -e

# 容器引导入口
# 固定调用 /app/site_data/conf/entrypoint.sh
# 项目代码挂载到 /app/hanger

ENTRYPOINT="/app/site_data/conf/entrypoint.sh"

if [ ! -f "$ENTRYPOINT" ]; then
    echo "ERROR: entrypoint not found at $ENTRYPOINT"
    echo "Please mount site data directory to /app/site_data"
    exit 1
fi

exec "$ENTRYPOINT"
