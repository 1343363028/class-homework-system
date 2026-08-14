#!/bin/bash
set -e
cd "$(dirname "$0")/frontend"
if [ ! -d "node_modules" ]; then
    echo "[1/2] 安装依赖..."
    npm install
fi
echo "[2/2] 启动前端开发服务器..."
echo "  访问地址: http://localhost:5173"
echo ""
exec npm run dev
