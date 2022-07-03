from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app import mail, app


def send_async_mail(app, msg):
    with app.app_context():
        mail.send(msg)


def send_resetPwd_mail(user, token):
    msg = Message("【卓见】重置密码",
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[user.email],
                  html=render_template('user/resetPwd_mail.html', user=user, token=token))
    # mail.send(msg)
    # 利用线程加速发送认证邮件
    Thread(target=send_async_mail, args=(app, msg)).start()
