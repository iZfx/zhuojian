from flask import render_template, flash, request
from sqlalchemy import func

from app import app
from app.models import *
from app.utils import redirect_back


@app.route('/', methods=['GET', 'POST'])
def index():
    title = '首页'
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BOOK_DISPLAY_PER_PAGE']
    pagination = Book.query.order_by(func.random()).paginate(page, per_page, False)
    tags = Tag.query.order_by(Tag.id).all()
    return render_template('index/index.html', title=title, pagination=pagination, tags=tags)


@app.route('/search')
def search():
    title = '搜索'
    q = request.args.get('q', '').strip()
    print(q)
    if q == '':
        flash('请输入关键字用于搜索.', 'warning')
        return redirect_back()
    category = request.args.get('category', 'book')
    print(category)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BOOK_TAG_PER_PAGE']
    if category == 'user':
        pagination = User.query.whooshee_search(q).order_by(User.id.desc()).paginate(page, per_page)
    elif category == 'tag':
        pagination = Tag.query.whooshee_search(q).order_by(Tag.id.desc()).paginate(page, per_page)
    elif category == 'comment':
        pagination = Comment.query.whooshee_search(q).order_by(Comment.id.desc()).paginate(page, per_page)
    elif category == 'note':
        pagination = Note.query.whooshee_search(q).order_by(Note.id.desc()).paginate(page, per_page)
    else:
        pagination = Book.query.whooshee_search(q).order_by(Book.publish_time.desc()).paginate(page, per_page)
    print(pagination.total)
    results = pagination.items
    print(results)
    return render_template('index/search.html', title=title, q=q, results=results, pagination=pagination, category=category)
