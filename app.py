import os
from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from models import db, User, Task

from sqlalchemy.exc import IntegrityError

import os


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "secret_key_123")
db.init_app(app)




def error_payload(status:int, error:str, field_errors:list = None):
   
    ts = datetime.utcnow().isoformat() + "Z"
    payload = {
        "timestamp": ts,
        "status": status,
        "error": error,
    }
    if field_errors:
        payload["fieldErrors"] = field_errors
    return jsonify(payload), status

def validate_title(title):
    if title is None:
        return ("title", "MISSING", "Title is required")
    t = title.strip()
    if len(t) < 3 or len(t) > 50:
        return ("title", "INVALID_LENGTH", "Title must be 3–50 characters")
    return None

def validate_category(category):
    if not category:
        return None
    c = category.strip()
   
    import re
    if len(c) > 50:
        return ("category", "INVALID_LENGTH", "Category too long (max 50)")
    if not re.match(r"^[A-Za-z0-9\s\-]+$", c):
        return ("category", "INVALID_FORMAT", "Category contains invalid characters")
    return None

def validate_priority(priority):
    try:
        p = int(priority)
    except Exception:
        return ("priority", "INVALID_FORMAT", "Priority must be an integer")
    if p < 1 or p > 5:
        return ("priority", "OUT_OF_RANGE", "Priority must be between 1 and 5")
    return None

def parse_deadline(deadline_str):
    if not deadline_str:
        return None, None
    try:
        d = datetime.strptime(deadline_str, "%Y-%m-%d").date()
    except Exception:
        return None, ("deadline", "INVALID_FORMAT", "Deadline must be YYYY-MM-DD")
    
    if d < date.today():
        return None, ("deadline", "INVALID_VALUE", "Deadline cannot be in the past")
    return d, None


# ---------- public routes ----------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status":"ok","timestamp": datetime.utcnow().isoformat()+"Z"}), 200




@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        login_name = request.form.get("login", "").strip()
        password = request.form.get("password", "")

       
        if not login_name or len(login_name) < 3 or len(login_name) > 50:
            return render_template("register.html", error="Login must be 3–50 characters.")
        if not password or len(password) < 6:
            return render_template("register.html", error="Password must be at least 6 characters.")

        if User.query.filter_by(login=login_name).first():
          
            return render_template("register.html", error="Login already exists."), 409

        user = User(login=login_name, hasloHash=generate_password_hash(password), rola="USER")
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return render_template("register.html", error="Login already exists."), 409

       
        session["user_id"] = user.id
        session["login"] = user.login
        return redirect("/tasks")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_name = request.form.get("login", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(login=login_name).first()
        if not user or not check_password_hash(user.hasloHash, password):
            return render_template("login.html", error="Wrong login or password."), 401

        session["user_id"] = user.id
        session["login"] = user.login
        return redirect("/tasks")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")




@app.route("/tasks")
def tasks_page():
    if "user_id" not in session:
        return redirect("/login")
    tasks = Task.query.filter_by(user_id=session["user_id"]).all()
    return render_template("tasks.html", tasks=tasks, user=session["login"])




def require_login_json():
    if "user_id" not in session:
        return error_payload(401, "Unauthorized")


@app.route("/tasks", methods=["GET"])
def api_list_tasks():
    if "user_id" not in session:
        return error_payload(401, "Unauthorized")
    tasks = Task.query.filter_by(user_id=session["user_id"]).all()
    return jsonify([{
        "id": t.id,
        "title": t.title,
        "category": t.category,
        "priority": t.priority,
        "deadline": t.deadline.isoformat() if t.deadline else None,
        "created_date": t.created_date.isoformat()
    } for t in tasks]), 200


@app.route("/add_task", methods=["POST"])
def add_task():
    if "user_id" not in session:
        return error_payload(401, "Unauthorized")
    data = request.get_json() or {}

 
    v = validate_title(data.get("title"))
    if v:
        return error_payload(400, "Bad Request", [ {"field": v[0], "code": v[1], "message": v[2]} ])

    v = validate_category(data.get("category"))
    if v:
        return error_payload(400, "Bad Request", [ {"field": v[0], "code": v[1], "message": v[2]} ])

    v = validate_priority(data.get("priority", 3))
    if v:
        return error_payload(400, "Bad Request", [ {"field": v[0], "code": v[1], "message": v[2]} ])

    dl, dl_err = parse_deadline(data.get("deadline"))
    if dl_err:
        return error_payload(422, "Unprocessable Entity", [ {"field": dl_err[0], "code": dl_err[1], "message": dl_err[2]} ])

    # duplicate title for same user -> 409
    existing = Task.query.filter_by(user_id=session["user_id"], title=data.get("title").strip()).first()
    if existing:
        return error_payload(409, "Conflict", [ {"field":"title","code":"DUPLICATE","message":"Task with this title already exists"} ])

    task = Task(
        title=data.get("title").strip(),
        category=data.get("category"),
        priority=int(data.get("priority",3)),
        deadline=dl,
        user_id=session["user_id"]
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({"message":"Task added","id":task.id}), 201


@app.route("/update_task/<int:id>", methods=["PUT"])
def update_task(id):
    if "user_id" not in session:
        return error_payload(401, "Unauthorized")
    task = Task.query.get(id)
    if not task:
        return error_payload(404, "Not Found")
    if task.user_id != session["user_id"]:
        return error_payload(403, "Forbidden")

    data = request.get_json() or {}

    if "title" in data:
        v = validate_title(data.get("title"))
        if v:
            return error_payload(400, "Bad Request", [ {"field": v[0], "code": v[1], "message": v[2]} ])
        # duplicate check
        other = Task.query.filter_by(user_id=session["user_id"], title=data.get("title").strip()).first()
        if other and other.id != task.id:
            return error_payload(409, "Conflict", [ {"field":"title","code":"DUPLICATE","message":"Task with this title already exists"} ])
        task.title = data.get("title").strip()

    if "category" in data:
        v = validate_category(data.get("category"))
        if v:
            return error_payload(400, "Bad Request", [ {"field": v[0], "code": v[1], "message": v[2]} ])
        task.category = data.get("category")

    if "priority" in data:
        v = validate_priority(data.get("priority"))
        if v:
            return error_payload(400, "Bad Request", [ {"field": v[0], "code": v[1], "message": v[2]} ])
        task.priority = int(data.get("priority"))

    if "deadline" in data:
        dl, dl_err = parse_deadline(data.get("deadline"))
        if dl_err:
            return error_payload(422, "Unprocessable Entity", [ {"field": dl_err[0], "code": dl_err[1], "message": dl_err[2]} ])
        task.deadline = dl

    db.session.commit()
    return jsonify({"message":"Updated"}), 200


@app.route("/delete_task/<int:id>", methods=["DELETE"])
def delete_task(id):
    if "user_id" not in session:
        return error_payload(401, "Unauthorized")
    task = Task.query.get(id)
    if not task:
        return error_payload(404, "Not Found")
    if task.user_id != session["user_id"]:
        return error_payload(403, "Forbidden")
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message":"Deleted"}), 200




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
