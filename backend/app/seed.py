"""Seed script to create default test data."""
from app.database import engine, SessionLocal, Base
from app.models import User, Role
from app.password import hash_password


def seed():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            print("Database already seeded.")
            return

        # Create committee member
        committee = User(
            student_id="100001",
            name="张三(学习委员)",
            password=hash_password("123456"),
            role=Role.COMMITTEE,
        )
        db.add(committee)

        # Create test students
        students = [
            User(student_id="2024001", name="李四", password=hash_password("123456"), role=Role.STUDENT),
            User(student_id="2024002", name="王五", password=hash_password("123456"), role=Role.STUDENT),
            User(student_id="2024003", name="赵六", password=hash_password("123456"), role=Role.STUDENT),
            User(student_id="2024004", name="小明", password=hash_password("123456"), role=Role.STUDENT),
            User(student_id="2024005", name="小红", password=hash_password("123456"), role=Role.STUDENT),
        ]
        for s in students:
            db.add(s)

        db.commit()
        print("Database seeded successfully!")
        print("学习委员: 学号=100001, 密码=123456")
        print("学生: 学号=2024001~2024005, 密码=123456")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
