from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    text = TextAreaField('Комментарий', validators=[DataRequired()])
    rate = SelectField('Оценка', choices=[1, 2, 3, 4, 5], validators=[DataRequired()])
    submit = SubmitField('Опубликовать')
