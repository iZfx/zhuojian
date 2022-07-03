from flask import url_for, redirect
from flask_admin import BaseView, expose
from flask_login import current_user, logout_user
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import upload

from app import admin, User, db, Book, Comment, Note, Tag, os, SensitiveWords
from config import basedir

file_path = os.path.join(basedir, 'app/static/images/')


class BookView(ModelView):
    # 这三个变量定义管理员是否可以增删改，默认为True
    can_delete = True
    can_edit = True
    can_create = True
    # 这里是为了自定义显示的column名字
    column_labels = dict(book_img='图书封面地址',
                         book_name='书名',
                         author='作者',
                         translator='译者',
                         publisher='出版商',
                         publish_time='出版时间',
                         page='页数',
                         book_intro='图书简介',
                         author_intro='作者简介',
                         tags='标签',
                         comments='评论',
                         notes='笔记')
    # 设置可搜索的字段
    column_searchable_list = ['book_name', 'author', 'translator', 'publisher']
    # 如果不想显示某些字段，可以重载这个变量
    column_exclude_list = ('book_intro', 'author_intro')
    # book_img为需要上传图片的字段
    form_extra_fields = {'图书封面': upload.ImageUploadField(label='上传图片', base_path=file_path + 'book/')}

    def is_accessible(self):
        if current_user.is_authenticated and current_user.username == "admin":
            return True
        return False


class UserView(ModelView):
    can_edit = False
    can_create = False
    column_exclude_list = ('password',)
    column_labels = dict(username='用户名',
                         password='密码',
                         email='电子邮件',
                         avatar_img='用户头像')
    column_searchable_list = ['username', 'email']

    def is_accessible(self):
        if current_user.is_authenticated and current_user.username == "admin":
            return True
        return False


class CommentView(ModelView):
    can_edit = False
    can_create = False
    column_labels = dict(title='标题',
                         content='内容',
                         timestamp='发表时间',
                         book='图书',
                         user='用户',
                         replied='回复目标')
    column_searchable_list = ['title', 'content']

    def is_accessible(self):
        if current_user.is_authenticated and current_user.username == "admin":
            return True
        return False


class NoteView(ModelView):
    can_edit = False
    can_create = False
    column_labels = dict(title='标题',
                         page='页码',
                         content='内容',
                         timestamp='发表时间',
                         book='图书',
                         user='用户')
    column_searchable_list = ['title', 'content']

    def is_accessible(self):
        if current_user.is_authenticated and current_user.username == "admin":
            return True
        return False


class TagView(ModelView):
    column_labels = dict(name='标签',
                         books='书籍',
                         notes='笔记')
    column_searchable_list = ['name']

    def is_accessible(self):
        if current_user.is_authenticated and current_user.username == "admin":
            return True
        return False


class SensitiveWordsView(ModelView):
    column_labels = dict(words='关键词')
    column_searchable_list = ['words']

    def is_accessible(self):
        if current_user.is_authenticated and current_user.username == "admin":
            return True
        return False


class DocumentView(FileAdmin):
    column_labels = dict(name='文件名',
                         size='大小',
                         date='创建日期')

    def is_accessible(self):
        if current_user.is_authenticated and current_user.username == "admin":
            return True
        return False


class LogoutView(BaseView):
    # 这里类似于app.route()，处理url请求
    @expose('/')
    def logout(self):
        logout_user()
        return redirect(url_for('login'))

    def is_accessible(self):
        if current_user.is_authenticated and current_user.username == "admin":
            return True
        return False


# 在这里初始化Flask Flask-SQLAlchemy Flask-Admin
# 只需把自己写的处理模型的视图加进去就行了，category是可选的目录
admin.add_view(BookView(Book, db.session, name='图书管理'))
admin.add_view(UserView(User, db.session, name='用户管理'))
admin.add_view(CommentView(Comment, db.session, name='评论管理'))
admin.add_view(NoteView(Note, db.session, name='笔记管理'))
admin.add_view(TagView(Tag, db.session, name='标签管理'))
admin.add_view(SensitiveWordsView(SensitiveWords, db.session, name='关键词管理'))
# 文件管理:管理上传文件和图片
admin.add_view(DocumentView(file_path, name='文件管理'))
admin.add_view(LogoutView(name='退出'))
