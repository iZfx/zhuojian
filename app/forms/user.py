from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User


class RegisterForm(FlaskForm):
    username = StringField('用 户 名', validators=[DataRequired(), Length(min=3, max=9)])
    email = StringField('电子邮件', validators=[DataRequired(), Email()])
    password = PasswordField('密 码', validators=[DataRequired(), Length(min=6, max=9)])
    confirm = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    # recaptcha = RecaptchaField()
    submit = SubmitField('确认注册')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该电子邮件已被使用')


class LoginForm(FlaskForm):
    username = StringField('用 户 名', validators=[DataRequired(), Length(min=3, max=9)])
    password = PasswordField('密 码', validators=[DataRequired(), Length(min=6, max=9)])
    remember = BooleanField('记住登录')
    submit = SubmitField('登 录')


class send_resetPwdForm(FlaskForm):
    email = StringField('电子邮件', validators=[DataRequired(), Email()])
    submit = SubmitField('发 送')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('该电子邮件不存在')


class resetPwdForm(FlaskForm):
    password = PasswordField('新 密 码', validators=[DataRequired(), Length(min=6, max=9)])
    confirm = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('重置密码')


class uploadPhotoForm(FlaskForm):
    photo = FileField('选择图片', validators=[FileRequired()])
    submit = SubmitField('上传头像')
