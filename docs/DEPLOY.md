# 作业登记系统 - 宝塔面板部署手册 (Debian)

## 环境要求

| 组件 | 版本 | 备注 |
|------|------|------|
| 系统 | Debian 11+ | 也适用于 Ubuntu 20+ |
| 宝塔面板 | 7.x/8.x | 面板管理 |
| Python | 3.10+ | FastAPI 运行环境 |
| Node.js | 18+ | 前端构建（仅部署时） |
| Nginx | 宝塔自带 | 反向代理 + 静态文件 |

---

## 一、上传代码

宝塔面板 → 文件 → 上传项目压缩包到 `/www/wwwroot/homework-system`

或在服务器上克隆：
```bash
cd /www/wwwroot
git clone <your-repo-url> homework-system
cd homework-system
```

目录结构：
```
/www/wwwroot/homework-system/
├── backend/
├── frontend/
└── README.md
```

---

## 二、后端部署

### 2.1 安装 Python 环境

```bash
# 安装 Python 3.10（Debian 11 默认可能是 3.9，建议 3.10+）
apt update && apt install -y python3.10 python3.10-venv python3-pip

# 如果已自带 Python3.10，跳过上一步
python3 --version  # 确认 >= 3.10
```

### 2.2 创建虚拟环境并安装依赖

```bash
cd /www/wwwroot/homework-system/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 安装生产环境 gunicorn（可选，推荐）
pip install gunicorn
```

### 2.3 配置环境变量

```bash
# 复制并修改 .env 文件
cp .env.example .env
```

编辑 `.env`，**务必修改 SECRET_KEY**：
```ini
SECRET_KEY=替换成一个随机字符串-建议32位以上
DATABASE_URL=sqlite:///./homework.db
```

生成随机密钥：
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2.4 初始化数据库

```bash
source venv/bin/activate
python -m app.seed
```

看到输出说明成功：
```
Database seeded successfully!
学习委员: 学号=100001, 密码=123456
学生: 学号=2024001~2024005, 密码=123456
```

### 2.5 测试运行

```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

在浏览器访问 `http://服务器IP:8000`，应返回：
```json
{"message": "作业登记系统 API", "version": "1.0.0"}
```

测试 API 文档：`http://服务器IP:8000/docs`

按 `Ctrl+C` 停止测试运行，进入下一步配置守护进程。

### 2.6 配置 Systemd 守护进程

创建服务文件：
```bash
nano /etc/systemd/system/homework-backend.service
```

写入（**修改 `User` 和 `WorkingDirectory`**）：
```ini
[Unit]
Description=Homework Registration System API
After=network.target

[Service]
Type=notify
User=www
WorkingDirectory=/www/wwwroot/homework-system/backend
Environment="PATH=/www/wwwroot/homework-system/backend/venv/bin"
ExecStart=/www/wwwroot/homework-system/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启动并设置开机自启：
```bash
systemctl daemon-reload
systemctl enable homework-backend
systemctl start homework-backend

# 检查状态
systemctl status homework-backend
```

---

## 三、前端构建

```bash
# 在服务器上安装 Node.js（宝塔面板 → 软件商店 → 搜索 Node 管理器 → 安装）
# 或使用 nvm：
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 18

# 安装依赖并构建
cd /www/wwwroot/homework-system/frontend
npm install
npm run build
```

构建完成后，生成的文件在 `frontend/dist/` 目录。

---

## 四、宝塔面板配置

### 4.1 添加网站

宝塔面板 → 网站 → 添加站点：

| 配置项 | 值 |
|--------|-----|
| 域名 | `homework.yourdomain.com`（或服务器IP） |
| PHP版本 | 纯静态 |
| 根目录 | `/www/wwwroot/homework-system/frontend/dist` |

### 4.2 配置反向代理

进入网站设置 → 反向代理 → 添加反向代理：

| 配置项 | 值 |
|--------|-----|
| 代理名称 | homework-api |
| 目标URL | `http://127.0.0.1:8000` |
| 发送域名 | `$host` |
| 代理目录 | `/api` |

或者手动编辑 Nginx 配置文件（网站设置 → 配置文件），在 `server` 块中加入：

```nginx
server {
    listen 80;
    server_name homework.yourdomain.com;

    # 前端静态文件
    root /www/wwwroot/homework-system/frontend/dist;
    index index.html;

    # SPA 路由 - 所有非 API 请求回退到 index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

保存后重载 Nginx：
```bash
nginx -t           # 检查配置
systemctl reload nginx
```

### 4.3 配置 SSL（推荐）

宝塔面板 → 网站设置 → SSL → Let's Encrypt → 填写邮箱 → 申请

申请成功后强制 HTTPS 跳转。

---

## 五、防火墙设置

宝塔面板 → 安全 → 放行端口（**仅开发调试需要，生产不需要**）：

| 端口 | 用途 |
|------|------|
| 8000 | 后端 API（生产环境通过 Nginx 代理，无需对外开放） |

生产环境只需要开放 `80` 和 `443`。

---

## 六、验证部署

```bash
# 1. 检查后端进程
systemctl status homework-backend

# 2. 检查 Nginx 状态
systemctl status nginx

# 3. 测试 API
curl http://localhost/api/
# 期望返回: {"message": "作业登记系统 API", "version": "1.0.0"}

# 4. 测试登录
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"student_id":"100001","password":"123456"}'
# 期望返回包含 access_token 的 JSON

# 5. 浏览器访问
# http://homework.yourdomain.com 或 http://服务器IP
```

---

## 七、日常运维

### 查看后端日志
```bash
journalctl -u homework-backend -f --since "1 hour ago"
```

### 重启后端
```bash
systemctl restart homework-backend
```

### 更新代码后重新部署

```bash
cd /www/wwwroot/homework-system

# 更新后端
cd backend
source venv/bin/activate
pip install -r requirements.txt   # 如果有新依赖
python -m app.seed                # 如果修改了数据库结构

# 更新前端
cd ../../frontend
npm run build

# 重启后端
systemctl restart homework-backend

# 重载 Nginx（如需）
nginx -s reload
```

### 数据库备份
```bash
# SQLite 数据库文件直接备份
cp /www/wwwroot/homework-system/backend/homework.db \
   /www/backup/homework_db_$(date +%Y%m%d).db
```

---

## 八、常见问题

### 端口被占用
```bash
ss -tlnp | grep 8000    # 查看谁占用了 8000 端口
```

### 权限问题
```bash
chown -R www:www /www/wwwroot/homework-system
```

### 虚拟环境激活失败
```bash
# 确认 Python 版本
/www/wwwroot/homework-system/backend/venv/bin/python --version
```

### Nginx 502 错误
- 检查后端是否运行：`systemctl status homework-backend`
- 检查端口是否正确：后端监听了 8000，Nginx proxy_pass 也要指向 8000

---

## 附：完整的一键部署脚本

```bash
#!/bin/bash
# deploy.sh - 一键部署脚本
set -e

APP_DIR="/www/wwwroot/homework-system"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"

echo "=== 1. 安装后端依赖 ==="
cd "$BACKEND_DIR"
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt

# 生成密钥
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
if [ ! -f .env ]; then
    echo "SECRET_KEY=$SECRET_KEY" > .env
    echo 'DATABASE_URL=sqlite:///./homework.db' >> .env
    echo "已生成 .env 文件，密钥: $SECRET_KEY"
fi

echo "=== 2. 初始化数据库 ==="
python -m app.seed

echo "=== 3. 构建前端 ==="
cd "$FRONTEND_DIR"
npm install --silent
npm run build

echo "=== 4. 重启后端服务 ==="
systemctl restart homework-backend || true

echo "=== 部署完成 ==="
echo "访问: http://你的域名"
echo "学习委员: 100001 / 123456"
```

用法：
```bash
chmod +x deploy.sh
./deploy.sh
```
