from flask import Blueprint, jsonify, request

from app.data.store import store
from app.services.scheduler import enrich_session, generate_schedule


schedule_bp = Blueprint("schedule", __name__)


@schedule_bp.get("")
def list_schedule():
    return jsonify([enrich_session(item) for item in store.schedule])


@schedule_bp.post("/generate")
def generate():
    payload = request.get_json() or {}
    result = generate_schedule(
        class_id=payload.get("class_id"),
        start_date=payload.get("start_date"),
        days=int(payload.get("days", 8)),
        time_slots=payload.get("time_slots"),
        preview=False,
    )
    return (
        jsonify(
            {
                "sessions": [enrich_session(item) for item in result["sessions"]],
                "skipped": result["skipped"],
            }
        ),
        201,
    )


@schedule_bp.post("/preview")
def preview():
    payload = request.get_json() or {}
    result = generate_schedule(
        class_id=payload.get("class_id"),
        start_date=payload.get("start_date"),
        days=int(payload.get("days", 8)),
        time_slots=payload.get("time_slots"),
        preview=True,
    )
    return jsonify(
        {
            "sessions": [enrich_session(item) for item in result["sessions"]],
            "skipped": result["skipped"],
        }
    )


@schedule_bp.get("/suspended-dates")
def list_suspended_dates():
    return jsonify(store.suspended_dates)


@schedule_bp.post("/suspended-dates")
def add_suspended_date():
    payload = request.get_json() or {}
    date_str = payload.get("date")
    reason = payload.get("reason", "")
    if not date_str:
        return jsonify({"error": "日期不能为空"}), 400
    success = store.add_suspended_date(date_str, reason)
    if success:
        return jsonify({"message": "添加成功"}), 201
    return jsonify({"error": "日期已存在"}), 400


@schedule_bp.delete("/suspended-dates/<date_str>")
def remove_suspended_date(date_str):
    success = store.remove_suspended_date(date_str)
    if success:
        return jsonify({"message": "删除成功"})
    return jsonify({"error": "日期不存在"}), 404
