from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------ MODEL ------------------
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    published_date = db.Column(db.Date, nullable=True)
    pages = db.Column(db.Integer, default=0)
    genre = db.Column(db.String(50))
    rating = db.Column(db.Float, default=0.0)
    # ✅ nowe pola:
    publisher = db.Column(db.String(100))   
    price = db.Column(db.Float, default=0.0)  

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "pages": self.pages,
            "genre": self.genre,
            "rating": self.rating,
            "publisher": self.publisher,
            "price": self.price
        }



@app.route('/api/books', methods=['GET'])
def list_books():
    books = Book.query.all()
    return jsonify([b.to_dict() for b in books]), 200


@app.route('/api/books/<int:id>', methods=['GET'])
def get_book(id):
    b = Book.query.get_or_404(id)
    return jsonify(b.to_dict()), 200


@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.get_json()
    if not data.get("title") or not data.get("author"):
        return jsonify({"error": "title and author are required"}), 400

    try:
        published_date = datetime.fromisoformat(data["published_date"]).date() if data.get("published_date") else None
    except ValueError:
        return jsonify({"error": "Invalid date format (use YYYY-MM-DD)"}), 400

    b = Book(
        title=data["title"].strip(),
        author=data["author"].strip(),
        published_date=published_date,
        pages=int(data.get("pages", 0)),
        genre=data.get("genre"),
        rating=float(data.get("rating", 0.0)),
        publisher=data.get("publisher"),   # nowe pole
        price=float(data.get("price", 0.0))  # nowe pole
    )
    db.session.add(b)
    db.session.commit()
    return jsonify(b.to_dict()), 201


@app.route('/api/books/<int:id>', methods=['PUT'])
def update_book(id):
    b = Book.query.get_or_404(id)
    data = request.get_json()

    if "published_date" in data:
        try:
            b.published_date = datetime.fromisoformat(data["published_date"]).date() if data["published_date"] else None
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400

    b.title = data.get("title", b.title)
    b.author = data.get("author", b.author)
    b.pages = int(data.get("pages", b.pages))
    b.genre = data.get("genre", b.genre)
    b.rating = float(data.get("rating", b.rating))
    b.publisher = data.get("publisher", b.publisher)
    b.price = float(data.get("price", b.price))

    db.session.commit()
    return jsonify(b.to_dict()), 200


@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    b = Book.query.get_or_404(id)
    db.session.delete(b)
    db.session.commit()
    return '', 204




if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)
