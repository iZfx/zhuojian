import jwt
from datetime import datetime
from flask_login import UserMixin
from flask import current_app

from app import db, login, whooshee


@login.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


book_tag = db.Table('book_tag',
                    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
                    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
                    )

note_tag = db.Table('note_tag',
                    db.Column('note_id', db.Integer, db.ForeignKey('note.id'), primary_key=True),
                    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
                    )


@whooshee.register_model('username')
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    avatar_img = db.Column(db.String(120), default='/static/images/default-avatar.jpg', nullable=False)

    followed = db.relationship('User', secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy=True), lazy=True
                               )

    def __repr__(self):
        return '<User %r>' % self.username

    def generate_resetPwd_token(self):
        return jwt.encode({'id': self.id}, current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def check_resetPwd_token(token):
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithm='HS256')
            return User.query.filter_by(id=data['id']).first()
        except:
            return

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.count(user) > 0


@whooshee.register_model('isbn', 'book_name', 'author')
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(26), unique=True, nullable=False, index=True)
    book_img = db.Column(db.String(120), unique=True, nullable=False)
    book_name = db.Column(db.String(120), nullable=False, index=True)
    author = db.Column(db.String(120), nullable=False, index=True)
    translator = db.Column(db.String(120), nullable=False, index=True)
    publisher = db.Column(db.String(120), nullable=False)
    publish_time = db.Column(db.String(20), nullable=False, index=True)
    page = db.Column(db.String(20), nullable=False)
    book_intro = db.Column(db.Text, nullable=True)
    author_intro = db.Column(db.Text, nullable=True)

    tags = db.relationship('Tag', secondary=book_tag, backref=db.backref('books', lazy=True))

    def __repr__(self):
        return '<Book %r %r>' % (self.book_name, self.author)


@whooshee.register_model('name')
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True, )
    name = db.Column(db.String(20), nullable=False, index=True)

    def __repr__(self):
        return '<Tag %r>' % self.name


@whooshee.register_model('title', 'content')
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=True, index=True)
    content = db.Column(db.Text, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.now, index=True)

    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)

    book = db.relationship('Book', backref=db.backref('comments', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('comments', lazy=True, cascade='all, delete-orphan'))

    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))

    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])

    def __repr__(self):
        self.format = '<Comment {}>'.format(self.content)
        return self.format


@whooshee.register_model('title', 'content')
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=False, index=True)
    page = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.now, index=True)

    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)

    book = db.relationship('Book', backref=db.backref('notes', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('notes', lazy=True, cascade='all, delete-orphan'))

    tags = db.relationship('Tag', secondary=note_tag, backref=db.backref('notes', lazy=True))

    def __repr__(self):
        return '<Note {}>'.format(self.content)


class SensitiveWords(db.Model):
    id = db.Column(db.Integer, primary_key=True, )
    words = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '%r' % self.words
