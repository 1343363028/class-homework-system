# 作业登记系统

FastAPI + Vue3 + Element Plus + SQLite

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt
python -m app.seed          # 初始化数据库和测试数据
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 `http://localhost:5173`

## 测试账号

| 角色     | 学号   | 密码   |
| -------- | ------ | ------ |
| 学习委员 | 100001 | 123456 |
| 学生     | 2024001| 123456 |
| 学生     | 2024005| 123456 |

学生可自行注册。

## API 文档

后端启动后访问 `http://localhost:8000/docs` (Swagger)
