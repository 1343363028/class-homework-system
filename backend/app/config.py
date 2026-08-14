"""应用配置"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 数据库：默认 SQLite（开发零配置），生产可切换 PostgreSQL
DATABASE_URL = f"sqlite:///{BASE_DIR / 'homework.db'}"

# JWT 配置
SECRET_KEY = os.getenv("SECRET_KEY", "homework-system-dev-secret-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24h

# CORS（允许局域网访问：手机通过电脑 IP 访问前端时，请求经 Vite 代理转发到后端）
# 开发环境直接允许所有来源，避免手机切换 WiFi 后 IP 变化导致跨域问题
CORS_ORIGINS = [
    "*",
]

# ===== 学号范围与学委账号配置 =====
# 学号范围：U202512647 ~ U202512680（包含两端）
STUDENT_ID_PREFIX = "U2025126"
STUDENT_ID_MIN = 47   # U202512647
STUDENT_ID_MAX = 80   # U202512680

# 学委账号列表
COMMISSARY_IDS = {"U202512649", "U202512660", "U202512670", "U202512676"}
# 学委初始密码
COMMISSARY_DEFAULT_PASSWORD = "123456"


def is_valid_student_id(student_id: str) -> bool:
    """校验学号是否在允许范围内 U202512647 ~ U202512680"""
    if not student_id or not student_id.startswith(STUDENT_ID_PREFIX):
        return False
    suffix = student_id[len(STUDENT_ID_PREFIX):]
    if not suffix.isdigit():
        return False
    num = int(suffix)
    return STUDENT_ID_MIN <= num <= STUDENT_ID_MAX


def is_commissary_id(student_id: str) -> bool:
    """判断是否为学委账号"""
    return student_id in COMMISSARY_IDS


# 预置科目
PRESET_SUBJECTS = [
    {"name": "大学物理", "color": "#2E86C1", "icon": "atom"},
    {"name": "电路理论", "color": "#E67E22", "icon": "lightning"},
    {"name": "复变函数", "color": "#8E44AD", "icon": "function"},
    {"name": "模拟电子技术", "color": "#16A085", "icon": "wave"},
    {"name": "马克思主义基本原理", "color": "#C0392B", "icon": "book"},
    {"name": "习近平新时代中国特色社会主义思想概论", "color": "#D4AC0D", "icon": "star"},
]
