from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#  МОДЕЛІ 
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    tasks = db.relationship('Task', backref='category', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(200))
    done = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

# ROUTES HTML 
@app.route('/')
def index():
    tasks = Task.query.all()
    categories = Category.query.all()
    return render_template('index.html', tasks=tasks, categories=categories)

@app.route('/add', methods=['POST'])
def add():
    title = request.form['title']
    description = request.form['description']
    category_id = request.form.get('category_id')
    new_task = Task(title=title, description=description, category_id=category_id)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form['name']
    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

#  REST API 
@app.route('/api/tasks')
def get_tasks():
    tasks = Task.query.all()
    return jsonify([
        {
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'done': t.done,
            'category': t.category.name if t.category else None
        } for t in tasks
    ])

@app.route('/api/categories')
def get_categories():
    categories = Category.query.all()
    return jsonify([
        {
            'id': c.id,
            'name': c.name,
            'task_count': len(c.tasks)
        } for c in categories
    ])

# RUN APP 
if __name__ == '__main__':
    with app.app_context():
        db.drop_all()   
        db.create_all() 
    app.run(debug=True)
