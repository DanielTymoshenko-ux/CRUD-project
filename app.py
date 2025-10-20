from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(30), nullable=True)
    tasks = db.relationship('Task', backref='category', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    done = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    priority = db.Column(db.Integer, nullable=False, default=3)   
    deadline = db.Column(db.Date, nullable=True)                

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'done': self.done,
            'created_date': self.created_date.isoformat(),
            'category': self.category.name if self.category else None,
            'priority': self.priority,
            'deadline': self.deadline.isoformat() if self.deadline else None
        }


@app.route('/')
def index():
    tasks = Task.query.all()
    categories = Category.query.all()
    return render_template('index.html', tasks=tasks, categories=categories)

@app.route('/add', methods=['POST'])
def add():
    title = request.form['title']
    description = request.form.get('description')
    category_id = request.form.get('category_id') or None
    # pobierz dodatkowe pola (jeśli formularz wysyła)
    priority = int(request.form.get('priority') or 3)
    deadline_raw = request.form.get('deadline') or None
    deadline = None
    if deadline_raw:
        try:
            deadline = datetime.fromisoformat(deadline_raw).date()
        except ValueError:
            # ignoruj niepoprawny format w trybie HTML (możesz dodać walidację UI)
            deadline = None
    new_task = Task(title=title, description=description, category_id=category_id,
                    priority=priority, deadline=deadline)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form['name']
    color = request.form.get('color')
    new_category = Category(name=name, color=color)
    db.session.add(new_category)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get(id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('index'))

# GET /api/tasks  — lista (z priority + deadline)
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([t.to_dict() for t in tasks]), 200

# GET /api/tasks/{id}
@app.route('/api/tasks/<int:id>', methods=['GET'])
def get_task(id):
    t = Task.query.get_or_404(id)
    return jsonify(t.to_dict()), 200

# POST /api/tasks  — walidacja priority i deadline
@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json() or {}
    title = data.get('title')
    if not title or not isinstance(title, str) or not title.strip():
        return jsonify({'error': 'title is required and must be a non-empty string'}), 400

    # priority: int 1..5
    try:
        priority = int(data.get('priority', 3))
    except (ValueError, TypeError):
        return jsonify({'error': 'priority must be an integer'}), 400
    if priority < 1 or priority > 5:
        return jsonify({'error': 'priority must be between 1 and 5'}), 400

    # deadline: ISO date YYYY-MM-DD or null
    deadline_raw = data.get('deadline')
    deadline = None
    if deadline_raw:
        try:
            deadline = datetime.fromisoformat(deadline_raw).date()
        except Exception:
            return jsonify({'error': 'deadline must be ISO date (YYYY-MM-DD)'}), 400

    new_task = Task(
        title=title.strip(),
        description=data.get('description', ''),
        done=bool(data.get('done', False)),
        category_id=data.get('category_id'),
        priority=priority,
        deadline=deadline
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

# PUT /api/tasks/{id} — partial update allowed, walidacja
@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    t = Task.query.get_or_404(id)
    data = request.get_json() or {}

    if 'title' in data:
        if not data['title'] or not isinstance(data['title'], str) or not data['title'].strip():
            return jsonify({'error': 'title must be non-empty string'}), 400
        t.title = data['title'].strip()

    if 'description' in data:
        t.description = data.get('description')

    if 'done' in data:
        t.done = bool(data.get('done'))

    if 'category_id' in data:
        t.category_id = data.get('category_id')

    if 'priority' in data:
        try:
            p = int(data.get('priority'))
        except (ValueError, TypeError):
            return jsonify({'error': 'priority must be integer'}), 400
        if p < 1 or p > 5:
            return jsonify({'error': 'priority must be between 1 and 5'}), 400
        t.priority = p

    if 'deadline' in data:
        dr = data.get('deadline')
        if dr in (None, ''):
            t.deadline = None
        else:
            try:
                t.deadline = datetime.fromisoformat(dr).date()
            except Exception:
                return jsonify({'error': 'deadline must be ISO date (YYYY-MM-DD)'}), 400

    db.session.commit()
    return jsonify(t.to_dict()), 200

# DELETE /api/tasks/{id}
@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task_api(id):
    t = Task.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    # 204 No Content
    return ('', 204)

f __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000)) 
    app.run(host="0.0.0.0", port=port, debug=False)
