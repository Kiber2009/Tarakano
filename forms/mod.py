from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField, TextAreaField, FileField
from wtforms.validators import DataRequired
from engine import SymbolsAnyOf
from string import digits, ascii_letters, ascii_lowercase


class UploadForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    mod_id = StringField('Идентификатор мода', validators=[DataRequired(), SymbolsAnyOf(
        ascii_lowercase + digits + '_')])
    version = StringField('Версия', validators=[DataRequired(), SymbolsAnyOf(
        digits + ascii_letters + '._-')])
    loader = SelectField('Ядро', validators=[DataRequired()], choices=['Forge', 'Fabric', 'NeoForge'])
    game_version = StringField('Версия игры', validators=[DataRequired(), SymbolsAnyOf(digits + '.x')])
    min_loader_version = StringField('Минимальная версия ядра', validators=[DataRequired(), SymbolsAnyOf(
        digits + '.x')])
    file = FileField('Файл', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')


class EditModForm(UploadForm):
    file = FileField('Файл')


class DownloadModForm(FlaskForm):
    submit = SubmitField('Скачать')
