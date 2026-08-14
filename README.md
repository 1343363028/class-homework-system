# 班级作业查询系统 v2.0

> 面向高校班级的作业查询与管理系统，支持 Web 端、Windows/Mac 桌面端及移动端。
> 技术栈：Vue 3 + TypeScript + FastAPI + SQLAlchemy + SQLite

## 项目结构

```
homework-system/
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── main.py         # 应用入口（含种子数据初始化）
│   │   ├── config.py       # 配置（学号范围、学委账号、预置科目）
│   │   ├── database.py     # 数据库连接
│   │   ├── models.py       # SQLAlchemy 模型（含 DuePeriod 截止时段）
│   │   ├── schemas.py      # Pydantic 模型
│   │   ├── auth.py         # JWT 认证 + bcrypt
│   │   └── routers/        # 路由（auth/subject/homework）
│   ├── requirements.txt
│   └── homework.db         # SQLite 数据库（自动生成）
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── api/            # Axios 封装
│   │   ├── components/     # 日历、可拖动倒计时、导航栏
│   │   ├── composables/    # 平台适配
│   │   ├── router/         # 路由 + 权限拦截
│   │   ├── stores/         # Pinia 状态
│   │   ├── styles/         # 科技电气风 CSS
│   │   ├── views/          # 页面
│   │   └── types/          # TS 类型
│   ├── package.json
│   └── vite.config.ts
├── desktop/                # Tauri 桌面端配置
└── mobile/                 # Capacitor 移动端配置
```

## 快速开始

### 1. 启动后端

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档：http://localhost:8000/docs

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 手机局域网访问（同一 WiFi）

已配置好局域网访问，前端 Vite 监听 `0.0.0.0`，手机访问电脑 IP 即可。

### 步骤

1. **确认电脑 IP**：假设为 `192.168.1.94`（在 PowerShell 执行 `ipconfig` 查看 IPv4 地址）

2. **启动后端**（监听 0.0.0.0）：
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **启动前端**（已配置 host: 0.0.0.0）：
   ```bash
   npm run dev
   ```
   启动后终端会显示两个地址：
   - `Local: http://localhost:5173/`
   - `Network: http://192.168.1.94:5173/`  ← 手机用这个

4. **Windows 防火墙放行 5173 端口**（首次会弹窗，点"允许访问"；或手动放行）：
   ```powershell
   # 以管理员身份运行 PowerShell
   New-NetFirewallRule -DisplayName "HomeworkSystem-5173" -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow
   New-NetFirewallRule -DisplayName "HomeworkSystem-8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
   ```

5. **手机访问**：手机浏览器打开 `http://192.168.1.94:5173`

### 工作原理
手机访问 `http://192.168.1.94:5173` → 前端页面加载 → 页面发起 `/api/xxx` 请求 → Vite dev server 代理转发到 `http://localhost:8000`（后端）。手机端无需任何特殊配置，API 请求自动经前端代理。

### 常见问题
- **手机打不开**：检查电脑防火墙是否放行 5173 端口
- **页面打开但登录失败**：检查后端是否启动、防火墙是否放行 8000 端口（通常不需要，因为走代理）
- **IP 地址变了**：WiFi 切换后 IP 可能变化，重新 `ipconfig` 查看新 IP

## 登录规则

### 学号范围
`U202512647` ~ `U202512680`（包含两端）

### 登录方式
1. **选择角色**：登录页先选择"学生"或"学委"
2. **学生登录**：输入学号即可，无需密码
3. **学委登录**：输入学号 + 密码（初始密码 `123456`）

### 学委账号
| 学号 | 说明 |
|------|------|
| U202512649 | 学委 |
| U202512660 | 学委 |
| U202512670 | 学委 |
| U202512676 | 学委 |

### 学生账号
`U202512647` ~ `U202512680` 中除学委外的所有学号，免密登录。

## 核心功能

### 1. 日历主页
- 以日历为核心视图，点击日期查看当日作业
- 布置日（青绿点）、截止日（红色点）特殊标注
- 当天高亮、过期置灰

### 2. 截止倒计时（可拖动）
- 固定悬浮在右下角，**支持鼠标拖动到任意位置**
- 位置自动保存到 localStorage，刷新后保持
- 按紧迫度分级着色（今日截止/紧急/即将/已截止）
- 已截止作业显示"已截止"而非负数天数

### 3. 作业管理（学委）
- 添加/修改/删除作业
- **支持设置截止时段：中午 / 晚上**
- 布置日与截止日校验

### 4. 科目管理（学委）
- 预置六门科目：大学物理、电路理论、复变函数、模拟电子技术、马克思主义基本原理、习近平新时代中国特色社会主义思想概论
- **支持修改科目属性**（名称、颜色、图标）
- **图标支持自定义**：可从预置 emoji 选择，也可直接输入任意文本/emoji
- 同一科目全局使用同一种颜色图标

## 权限说明

| 功能 | 学生 | 学委 |
|------|:----:|:----:|
| 登录 | 免密 | 需密码 |
| 日历查看作业 | ✓ | ✓ |
| 当日作业详情 | ✓ | ✓ |
| 倒计时提醒 | ✓ | ✓ |
| 添加/修改/删除作业 | ✗ | ✓ |
| 添加/修改/删除科目 | ✗ | ✓ |
| 初始化预置科目 | ✗ | ✓ |

## 跨平台打包

### Windows / Mac 桌面端（Tauri）

```bash
cargo install tauri-cli --version "^2.0"
cd desktop/src-tauri
cargo tauri build
# 产物：target/release/bundle/
#   Windows: .msi / .exe (NSIS)
#   macOS:   .app / .dmg
```

### 移动端（Capacitor）

```bash
cd mobile
npm install
cd ../frontend && npm run build && cd ../mobile
npx cap add android
npx cap sync
npx cap open android
```

## 技术亮点

- **科技电气风 UI**：深蓝基调 + 科技蓝强调色 + 网格背景 + 微交互动画
- **可拖动倒计时**：鼠标拖拽定位，位置持久化
- **截止时段**：中午/晚上两种截止时段，精细化作业管理
- **自定义图标**：科目图标支持 emoji 与任意文本输入
- **权限控制**：JWT + 角色工厂，路由守卫 + Axios 拦截器双重拦截
