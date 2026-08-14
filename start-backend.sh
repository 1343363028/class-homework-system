#!/bin/bash
set -e
cd "$(dirname "$0")/backend"
if [ ! -d "venv" ]; then
    echo "[1/3] 创建虚拟环境..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "[2/3] 安装依赖..."
pip install -q -r requirements.txt
echo "[3/3] 启动后端服务..."
echo "  API 文档: http://localhost:8000/docs"
echo "  学委账号: U202512649 / U202512660 / U202512670 / U202512676 (密码 123456)"
echo "  学生账号: U202512647 ~ U202512680 (免密登录)"
echo ""
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
