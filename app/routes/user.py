import os
import random

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont

from app import app, db, bcrypt
from app.forms.user import *
from app.models import *
from app.email import send_resetPwd_mail

from app.utils import redirect_back, allowed_file


@app.route('/register', methods=['GET', 'POST'])
def register():
    title = '注册'
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data)

        # 为注册用户生成默认头像
        i = random.randint(1, 500)
        r = lambda: random.randint(128, 255)
        img = Image.new(mode='RGB', size=(100, 100), color=(r(), r(), r()))    # 调用new()创建一个图片对象
        draw = ImageDraw.Draw(img)  # 获取一个画笔对象，将图片对象传过去
        # 获取一个font字体对象参数是ttf的字体文件的目录，以及字体的大小
        # 字体文件的名称，通常为ttf文件，还有少数ttc文件，可以在C:\Windows\Fonts中找到
        font = ImageFont.truetype('simsun.ttc', size=32)
        draw.text((25, 25), username, 0, font=font)   # 在图片上写东西,参数是：定位，字符串，颜色，字体
        filename = 'random_avatar_%d.jpg' % i
        img.save(os.path.join('app', 'static', 'images', 'user', filename))
        avatar_img = '/static/images/user/' + filename

        user = User(username=username, email=email, password=password, avatar_img=avatar_img)
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录', category='success')
        return redirect(url_for('login'))
    return render_template('user/register.html', title=title, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    title = '登录'
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        # check if password is matched
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('用户不存在', category='danger')
        elif user and bcrypt.check_password_hash(user.password, password):
            # user exist and password matched
            login_user(user, remember=remember)
            flash('登录成功', category='info')
            if request.args.get('next'):
                next_page = request.args.get('next')
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', category='danger')
    return render_template('user/login.html', title=title, form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/send_resetPwd', methods=['GET', 'POST'])
def send_resetPwd():
    title = '重置密码'
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = send_resetPwdForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        token = user.generate_resetPwd_token()
        send_resetPwd_mail(user, token)
        flash('邮件已发送，请检查您的邮箱！', category='info')
    return render_template('user/send_resetPwd.html', title=title, form=form)


@app.route('/resetPwd/<token>', methods=['GET', 'POST'])
def resetPwd(token):
    title = '重置密码'
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = resetPwdForm()
    if form.validate_on_submit():
        user = User.check_resetPwd_token(token)
        if user:
            user.password = bcrypt.generate_password_hash(form.password.data)
            db.session.commit()
            flash('密码重置成功，请重新登录。', category='info')
            return redirect(url_for('login'))
        else:
            flash('用户不存在', category='info')
            return redirect(url_for('index'))
    return render_template('user/resetPwd.html', title=title, form=form)


@app.route('/user_page/<username>')
# @login_required
def user_page(username):
    user = User.query.filter_by(username=username).first()
    if user:
        title = user.username
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['COMMENT_NOTE_PER_PAGE']
        pagination_comment = Comment.query.filter_by(user_id=user.id).order_by(Comment.timestamp.desc()).paginate(page, per_page, False)
        pagination_note = Note.query.filter_by(user_id=user.id).order_by(Note.timestamp.desc()).paginate(page, per_page, False)
        if current_user.is_authenticated:
            num_followers = len(current_user.followers)
            num_followed = len(current_user.followed)
            return render_template('user/user_page.html', user=user, title=title, pagination_comment=pagination_comment,
                               pagination_note=pagination_note, num_followers=num_followers, num_followed=num_followed)
        return render_template('user/user_page.html', user=user, title=title, pagination_comment=pagination_comment, pagination_note=pagination_note)
    else:
        return '404'


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user and current_user != user:
        current_user.follow(user)
        db.session.commit()
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['COMMENT_NOTE_PER_PAGE']
        pagination_comment = Comment.query.filter_by(user_id=user.id).order_by(Comment.timestamp.desc()).paginate(page, per_page, False)
        pagination_note = Note.query.filter_by(user_id=user.id).order_by(Note.timestamp.desc()).paginate(page, per_page, False)
        return render_template('user/user_page.html', user=user, pagination_comment=pagination_comment, pagination_note=pagination_note)
    else:
        return redirect_back()


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user:
        current_user.unfollow(user)
        db.session.commit()
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['COMMENT_NOTE_PER_PAGE']
        pagination_comment = Comment.query.filter_by(user_id=user.id).order_by(Comment.timestamp.desc()).paginate(page, per_page, False)
        pagination_note = Note.query.filter_by(user_id=user.id).order_by(Note.timestamp.desc()).paginate(page, per_page, False)
        return render_template('user/user_page.html', user=user, pagination_comment=pagination_comment, pagination_note=pagination_note)
    else:
        return '404'


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = uploadPhotoForm()
    if form.validate_on_submit():
        file = form.photo.data
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('未选择文件', category='danger')
            return render_template('user/edit_profile.html', form=form)
        if file and allowed_file(file.filename):
            # 避免用户输入的某些文件名对网站造成威胁
            filename = secure_filename(file.filename)
            file.save(os.path.join('app', 'static', 'images', 'user', filename))
            current_user.avatar_img = '/static/images/user/' + filename
            db.session.commit()
            return redirect(url_for('user_page', username=current_user.username))
    return render_template('user/edit_profile.html', form=form)