from datetime import date, datetime, timedelta

from app.data.store import store


DEFAULT_TIME_SLOTS = ["09:00-11:00", "14:00-16:00", "19:00-21:00"]


def _parse_date(date_str):
    if isinstance(date_str, date):
        return date_str
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def generate_schedule(
    class_id=None,
    start_date=None,
    days=10,
    time_slots=None,
    preview=False,
):
    classes = store.classes
    if class_id:
        classes = [item for item in classes if item["id"] == int(class_id)]

    if not classes:
        return {"sessions": [], "skipped": []}

    if time_slots is None:
        time_slots = DEFAULT_TIME_SLOTS

    if not time_slots:
        time_slots = DEFAULT_TIME_SLOTS

    if start_date:
        cursor = _parse_date(start_date)
    else:
        cursor = date.today() + timedelta(days=1)

    generated = []
    skipped = []
    course_index = 0
    days_generated = 0
    max_iterations = days * 10

    while days_generated < days and max_iterations > 0:
        max_iterations -= 1
        date_str = cursor.isoformat()

        if cursor.weekday() >= 5:
            skipped.append(
                {"date": date_str, "reason": "周末"}
            )
            cursor += timedelta(days=1)
            continue

        if store.is_suspended(date_str):
            reason = store.get_suspended_reason(date_str) or "停课"
            skipped.append(
                {"date": date_str, "reason": reason}
            )
            cursor += timedelta(days=1)
            continue

        day_sessions = []
        for training_class in classes:
            for time_slot in time_slots:
                if days_generated >= days:
                    break
                course = store.courses[course_index % len(store.courses)]
                session = {
                    "id": store.next_id("schedule"),
                    "class_id": training_class["id"],
                    "course_id": course["id"],
                    "date": date_str,
                    "time": time_slot,
                    "room": training_class["room"],
                    "teacher": training_class["teacher"],
                }
                if not preview:
                    store.schedule.append(session)
                day_sessions.append(session)
                course_index += 1
                days_generated += 1
                if days_generated >= days:
                    break
            if days_generated >= days:
                break

        generated.extend(day_sessions)
        cursor += timedelta(days=1)

    return {"sessions": generated, "skipped": skipped}


def enrich_session(session):
    training_class = next(
        (item for item in store.classes if item["id"] == session["class_id"]), None
    )
    course = next((item for item in store.courses if item["id"] == session["course_id"]), None)
    return {
        **session,
        "class_name": training_class["name"] if training_class else "未知班级",
        "course_title": course["title"] if course else "未知课程",
        "duration": course["duration"] if course else 0,
    }
