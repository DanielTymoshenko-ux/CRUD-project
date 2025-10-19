from flask import Flask, jsonify, request, abort
abort(400, description='Field "rating" must be a number')


@app.route('/api/books', methods=['GET'])
def list_books():
return jsonify([b.to_dict() for b in Book.query.all()]), 200


@app.route('/api/books/<int:id>', methods=['GET'])
def get_book(id):
b = Book.query.get_or_404(id)
return jsonify(b.to_dict()), 200


@app.route('/api/books', methods=['POST'])
def create_book():
data = request.get_json()
_validate_book_payload(data)
b = Book(
title=data['title'].strip(),
author=data['author'].strip(),
published_date=datetime.fromisoformat(data['published_date']).date() if data.get('published_date') else None,
pages=int(data.get('pages', 0)),
genre=data.get('genre'),
rating=float(data.get('rating', 0.0))
)
db.session.add(b)
db.session.commit()
return jsonify(b.to_dict()), 201


@app.route('/api/books/<int:id>', methods=['PUT'])
def update_book(id):
b = Book.query.get_or_404(id)
data = request.get_json()
_validate_book_payload(data, partial=True)
if 'title' in data and data['title'] is not None: b.title = data['title']
if 'author' in data and data['author'] is not None: b.author = data['author']
if 'pages' in data and data['pages'] is not None: b.pages = int(data['pages'])
if 'published_date' in data:
b.published_date = datetime.fromisoformat(data['published_date']).date() if data['published_date'] else None
if 'genre' in data:
b.genre = data['genre']
if 'rating' in data:
b.rating = float(data['rating']) if data['rating'] is not None else 0.0
db.session.commit()
return jsonify(b.to_dict()), 200


@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
b = Book.query.get_or_404(id)
db.session.delete(b)
db.session.commit()
return ('', 204)


if __name__ == '__main__':
app.run(debug=True)
