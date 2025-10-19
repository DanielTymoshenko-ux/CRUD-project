from flask import Blueprint, jsonify, request
from models import Task
from app import db
from datetime import datetime

api_bp = Blueprint("api", __name__)

@api_bp.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "done": t.done,
            "priority": t.priority,
            "deadline": t.deadline.isoformat() if t.deadline else None,
            "created_date": t.created_date.isoformat(),
            "category": t.category.name if t.category else None
        } for t in tasks
    ])

@api_bp.route("/tasks/<int:id>", methods=["GET"])
def get_task(id):
    t = Task.query.get_or_404(id)
    return jsonify({
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "done": t.done,
        "priority": t.priority,
        "deadline": t.deadline.isoformat() if t.deadline else None,
        "created_date": t.created_date.isoformat(),
        "category": t.category.name if t.category else None
    })

@api_bp.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    if not data.get("title"):
        return jsonify({"error": "Title is required"}), 400
    try:
        deadline = datetime.fromisoformat(data["deadline"]).date() if data.get("deadline") else None
    except ValueError:
        return jsonify({"error": "Invalid date format (use YYYY-MM-DD)"}), 400

    new_task = Task(
        title=data["title"],
        description=data.get("description", ""),
        done=data.get("done", False),
        priority=int(data.get("priority", 3)),
        deadline=deadline,
        category_id=data.get("category_id")
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"id": new_task.id}), 201

@api_bp.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    t = Task.query.get_or_404(id)
    data = request.get_json()
    if "deadline" in data:
        try:
            t.deadline = datetime.fromisoformat(data["deadline"]).date() if data["deadline"] else None
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400

    t.title = data.get("title", t.title)
    t.description = data.get("description", t.description)
    t.done = data.get("done", t.done)
    t.priority = int(data.get("priority", t.priority))
    t.category_id = data.get("category_id", t.category_id)
    db.session.commit()
    return jsonify({"message": "Updated successfully"}), 200

@api_bp.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    t = Task.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({"message": "Deleted successfully"}), 204
