from copy import deepcopy
from datetime import date


class TrainingStore:
    def __init__(self):
        self.suspended_dates = []
        self.classes = [
            {
                "id": 1,
                "name": "Python Flask 周末班",
                "level": "入门",
                "teacher": "张老师",
                "room": "A-201",
                "status": "开课中",
                "capacity": 28,
                "students": [
                    {"id": 1, "name": "李明", "phone": "13800000001"},
                    {"id": 2, "name": "王雨", "phone": "13800000002"},
                    {"id": 3, "name": "陈晨", "phone": "13800000003"},
                ],
            },
            {
                "id": 2,
                "name": "React 全栈进阶班",
                "level": "进阶",
                "teacher": "刘老师",
                "room": "B-105",
                "status": "招生中",
                "capacity": 24,
                "students": [
                    {"id": 4, "name": "赵一", "phone": "13800000004"},
                    {"id": 5, "name": "周航", "phone": "13800000005"},
                ],
            },
        ]
        self.courses = [
            {"id": 1, "title": "Flask API 设计", "duration": 2, "category": "后端"},
            {"id": 2, "title": "React 组件化开发", "duration": 2, "category": "前端"},
            {"id": 3, "title": "数据库建模实践", "duration": 2, "category": "工程"},
            {"id": 4, "title": "项目联调与部署", "duration": 3, "category": "工程"},
        ]
        self.schedule = [
            {
                "id": 1,
                "class_id": 1,
                "course_id": 1,
                "date": str(date.today()),
                "time": "09:00-11:00",
                "room": "A-201",
                "teacher": "张老师",
            }
        ]
        self.attendance = [
            {"id": 1, "session_id": 1, "student_id": 1, "status": "present"},
            {"id": 2, "session_id": 1, "student_id": 2, "status": "late"},
            {"id": 3, "session_id": 1, "student_id": 3, "status": "absent"},
        ]

    def next_id(self, collection):
        values = getattr(self, collection)
        return max([item["id"] for item in values], default=0) + 1

    def snapshot(self):
        return deepcopy(
            {
                "classes": self.classes,
                "courses": self.courses,
                "schedule": self.schedule,
                "attendance": self.attendance,
                "suspended_dates": self.suspended_dates,
            }
        )

    def add_suspended_date(self, date_str, reason=""):
        if date_str not in [item["date"] for item in self.suspended_dates]:
            self.suspended_dates.append(
                {
                    "id": self.next_id("suspended_dates"),
                    "date": date_str,
                    "reason": reason or "停课",
                }
            )
            return True
        return False

    def remove_suspended_date(self, date_str):
        initial_length = len(self.suspended_dates)
        self.suspended_dates = [
            item for item in self.suspended_dates if item["date"] != date_str
        ]
        return len(self.suspended_dates) < initial_length

    def is_suspended(self, date_str):
        return any(item["date"] == date_str for item in self.suspended_dates)

    def get_suspended_reason(self, date_str):
        for item in self.suspended_dates:
            if item["date"] == date_str:
                return item["reason"]
        return None


store = TrainingStore()
