from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODELS
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    tasks = db.relationship('Task', backref='category', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)       
    description = db.Column(db.String(200))                
    done = db.Column(db.Boolean, default=False)            
    created_date = db.Column(db.DateTime, default=datetime.utcnow) 
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

#  HTML ROUTES 
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

# REST API 

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([
        {
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'done': t.done,
            'created_date': t.created_date.isoformat(),
            'category': t.category.name if t.category else None
        } for t in tasks
    ])


@app.route('/api/tasks/<int:id>', methods=['GET'])
def get_task(id):
    t = Task.query.get_or_404(id)
    return jsonify({
        'id': t.id,
        'title': t.title,
        'description': t.description,
        'done': t.done,
        'created_date': t.created_date.isoformat(),
        'category': t.category.name if t.category else None
    })


@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    new_task = Task(
        title=data['title'],
        description=data.get('description', ''),
        done=data.get('done', False),
        category_id=data.get('category_id')
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'id': new_task.id}), 201


@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    t = Task.query.get_or_404(id)
    data = request.get_json()
    t.title = data.get('title', t.title)
    t.description = data.get('description', t.description)
    t.done = data.get('done', t.done)
    t.category_id = data.get('category_id', t.category_id)
    db.session.commit()
    return jsonify({'message': 'Updated successfully'}), 200


@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    t = Task.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({'message': 'Deleted successfully'}), 204

# RUN APP 
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
