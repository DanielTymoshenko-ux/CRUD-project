from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#  Модель Category 
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(30), nullable=True)

    tasks = db.relationship("Task", backref="category", lazy=True)

#  Модель Task 
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))
    is_done = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)
