from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Book(db.Model):
__tablename__ = 'books'
id = db.Column(db.Integer, primary_key=True)
title = db.Column(db.String(255), nullable=False)
author = db.Column(db.String(255), nullable=False)
published_date = db.Column(db.Date)
pages = db.Column(db.Integer, default=0)
# DODATKOWE POLA
genre = db.Column(db.String(100), nullable=True) # tekst
rating = db.Column(db.Float, default=0.0) # liczba (0-5)


def to_dict(self):
return {
'id': self.id,
'title': self.title,
'author': self.author,
'published_date': self.published_date.isoformat() if self.published_date else None,
'pages': self.pages,
'genre': self.genre,
'rating': self.rating
}
