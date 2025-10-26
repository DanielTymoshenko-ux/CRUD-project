from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, Task

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "secret_key_123"
db.init_app(app)



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]

        if len(password) < 4:
            return render_template("register.html", error="Password too short (min 4 ).")

        existing = User.query.filter_by(login=login).first()
        if existing:
            return render_template("register.html", error="Login already exist.")

        new_user = User(
            login=login,
            hasloHash=generate_password_hash(password),
            rola="USER"
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")

    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]

        user = User.query.filter_by(login=login).first()
        if user and check_password_hash(user.hasloHash, password):
            session["user_id"] = user.id
            session["login"] = user.login
            return redirect("/tasks")
        else:
            return render_template("login.html", error="Wrong login or password.")

    return render_template("login.html")



@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



@app.route("/tasks")
def tasks():
    if "user_id" not in session:
        return redirect("/login")

    tasks = Task.query.filter_by(user_id=session["user_id"]).all()
    return render_template("tasks.html", tasks=tasks, user=session["login"])



@app.route("/add_task", methods=["POST"])
def add_task():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    new_task = Task(
        title=data.get("title"),
        category=data.get("category"),
        priority=data.get("priority"),
        deadline=datetime.strptime(data.get("deadline"), "%Y-%m-%d") if data.get("deadline") else None,
        user_id=session["user_id"]
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task added"}), 201



@app.route("/delete_task/<int:id>", methods=["DELETE"])
def delete_task(id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    task = Task.query.get(id)
    if not task or task.user_id != session["user_id"]:
        return jsonify({"error": "Forbidden"}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Deleted"})



@app.route("/update_task/<int:id>", methods=["PUT"])
def update_task(id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    task = Task.query.get(id)
    if not task or task.user_id != session["user_id"]:
        return jsonify({"error": "Forbidden"}), 403

    data = request.json
    task.title = data.get("title", task.title)
    task.category = data.get("category", task.category)
    task.priority = data.get("priority", task.priority)
    if data.get("deadline"):
        task.deadline = datetime.strptime(data["deadline"], "%Y-%m-%d")
    else:
        task.deadline = None

    db.session.commit()
    return jsonify({"message": "Updated"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
   
    app.run(host="0.0.0.0", port=port, debug=False)
