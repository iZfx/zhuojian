from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length


class writeCommentForm(FlaskForm):
    title = TextAreaField('标题', validators=[DataRequired(), Length(min=1, max=40)])
    content = TextAreaField('内容', validators=[DataRequired(), Length(min=1)])
    submit = SubmitField('发表')


class ReplyForm(FlaskForm):
    content = TextAreaField('回复内容', validators=[DataRequired(), Length(min=1)])
    submit = SubmitField('提交')


class writeNoteForm(FlaskForm):
    page = IntegerField('页码', validators=[DataRequired()])
    title = TextAreaField('标题', validators=[DataRequired(), Length(min=1, max=40)])
    content = TextAreaField('内容', validators=[DataRequired(), Length(min=1)])
    tag = StringField('标签分类（多个标签用空格拆分）', validators=[Length(0, 64)])
    submit = SubmitField('发表')
