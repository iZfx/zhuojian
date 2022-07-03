import time

from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_required, current_user
from gensim import corpora, models, similarities

from app import app, db
from app.DFA_filter import DFAFilter
from app.forms.book import *
from app.models import *
from app.utils import tokenization


@app.route('/books_info/<isbn>', methods=['GET', 'POST'])
def books_info(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    if book:
        title = book.book_name
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['COMMENT_NOTE_PER_PAGE']
        pagination_comment = Comment.query.filter_by(book_id=book.id).order_by(Comment.timestamp.desc()).paginate(page, per_page, False)
        pagination_note = Note.query.filter_by(book_id=book.id).order_by(Note.timestamp.desc()).paginate(page, per_page, False)

        form = ReplyForm()
        if form.validate_on_submit():
            if current_user.is_authenticated:

                time1 = time.time()
                sw = DFAFilter()
                path = current_app.config['SENSITIVE_WORDS_PATH']
                sw.parse(path)

                title = 'None'
                content_text = form.content.data

                content = sw.filter(content_text)
                time2 = time.time()
                print('总共耗时：' + str(time2 - time1) + 's')

                comment = Comment(title=title, content=content)
                user_id = current_user.id
                user = User.query.filter_by(id=user_id).first()
                book = Book.query.filter_by(isbn=isbn).first()
                comment.user = user
                comment.book = book
                replied_id = request.args.get('reply')
                if replied_id:
                    replied_comment = Comment.query.get_or_404(replied_id)
                    comment.replied = replied_comment
                    db.session.add(comment)
                    db.session.commit()
                    flash('回复成功', category='success')
                else:
                    flash('请选择选择回复对象', category='warning')
                return redirect(url_for('books_info', isbn=book.isbn))
            else:
                flash('登录后使用此功能', category='info')
                return redirect(url_for('login'))
        return render_template('book/books_info.html', title=title, book=book, form=form,
                               pagination_comment=pagination_comment, pagination_note=pagination_note)
    else:
        return '404'


@app.route('/reply/comment/<comment_id>')
@login_required
def reply(comment_id):
    print(comment_id)
    comment = Comment.query.get_or_404(comment_id)
    print(comment)
    return redirect(url_for('books_info', isbn=comment.book.isbn, reply=comment_id, author=comment.user.username) + '#reply-form')


@app.route('/category/<name>')
def category(name):
    tag = Tag.query.filter_by(name=name).first()
    if tag:
        title = tag.name
        category = request.args.get('category', 'book')
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['BOOK_TAG_PER_PAGE']
        tags = Tag.query.order_by(Tag.id).all()
        if category == 'note':
            pagination = Note.query.with_parent(tag).order_by(Note.timestamp.desc()).paginate(page, per_page, False)
        else:
            pagination = Book.query.with_parent(tag).order_by(Book.publish_time.desc()).paginate(page, per_page, False)
        return render_template('book/category.html', title=title, tags=tags, pagination=pagination, category=category)
    else:
        return '404'


@app.route('/write_comment/<isbn>', methods=['GET', 'POST'])
@login_required
def write_comment(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    title = '写书评'
    form = writeCommentForm()
    if form.validate_on_submit():
        time1 = time.time()

        title_text = form.title.data
        content_text = form.content.data

        sw = DFAFilter()
        sw.parse()
        title = sw.filter(title_text)
        content = sw.filter(content_text)
        time2 = time.time()
        print('总共耗时：' + str(time2 - time1) + 's')

        comment = Comment(title=title, content=content)
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()
        book = Book.query.filter_by(isbn=isbn).first()
        comment.user = user
        comment.book = book
        db.session.add(comment)
        db.session.commit()
        flash('书评发表成功', category='success')
        return redirect(url_for('books_info', isbn=isbn))
    return render_template('book/write_comment.html', title=title, book=book, form=form)


@app.route('/write_note/<isbn>', methods=['GET', 'POST'])
@login_required
def write_note(isbn):
    book = Book.query.filter_by(isbn=isbn).first()
    title = '写笔记'
    form = writeNoteForm()
    if form.validate_on_submit():
        time1 = time.time()

        title_text = form.title.data
        content_text = form.content.data

        # 相似度检测
        print(content_text)

        exist_contents = Note.query.filter_by().all()
        print(exist_contents)
        if exist_contents:
            corpus = [tokenization(exist_content.content) for exist_content in exist_contents]

            # 把语料库转化成向量表示，这里使用词袋表示，具体来说就是每个词出现的次数。
            # 连接词和次数就用字典表示。然后，用doc2bow()函数统计词语的出现次数。
            dictionary = corpora.Dictionary(corpus)
            print(dictionary)
            word_vectors = [dictionary.doc2bow(word) for word in corpus]
            print(word_vectors)

            # 准备需要对比相似度的内容
            new_vec = dictionary.doc2bow(tokenization(content_text))

            # lsi模型判断相似度
            lsi = models.LsiModel(word_vectors, id2word=dictionary, num_topics=500)
            content_index = similarities.MatrixSimilarity(lsi[word_vectors])
            sims = content_index[lsi[new_vec]]
            res = list(sims)
            print(res)

            for res in res:
                if res >= 0.95:
                    print(res)
                    flash('你的内容与网站已存在的内容相似度极高，请重新编辑', category='warning')
                    return redirect(url_for('write_note', isbn=isbn))
        # 相似度检测end

        # 关键词处理
        sw = DFAFilter()
        sw.parse()
        title = sw.filter(title_text)
        content = sw.filter(content_text)
        time2 = time.time()
        print('总共耗时：' + str(time2 - time1) + 's')

        page = form.page.data
        note = Note(title=title, page=page, content=content)
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()
        book = Book.query.filter_by(isbn=isbn).first()
        note.user = user
        note.book = book
        db.session.add(note)
        db.session.commit()

        for name in form.tag.data.split():
            tag = Tag.query.filter_by(name=name).first()
            if tag is None:
                tag = Tag(name=name)
                db.session.add(tag)
                db.session.commit()
            if tag not in note.tags:
                note.tags.append(tag)
                db.session.commit()

        flash('笔记提交成功', category='success')
        return redirect(url_for('books_info', isbn=isbn))
    return render_template('book/write_note.html', title=title, book=book, form=form)