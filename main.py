import os
import config
from flask import Flask, render_template, redirect, abort, send_file
from forms.user import LoginForm, RegisterForm, EditUserForm, DeleteUserForm
from forms.mod import UploadForm, EditModForm, DownloadModForm
from forms.comment import CommentForm
from data import db_session
from data.users import User
from data.mods import Mod
from data.comments import Comment
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from engine import cut_str

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = config.PERMANENT_SESSION_LIFETIME
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    mods = db_sess.query(Mod)
    return render_template('index.html',
                           title='Tarakano',
                           mods=mods)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html',
                               title='Авторизация',
                               message='Неправильный логин или пароль',
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message='Пароли не совпадают')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message='Такой пользователь уже есть')
        user = User(
            name=form.email.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/user/<user_id>')
def user(user_id: int):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        abort(404)
    return render_template('user.html',
                           title=user.name,
                           user=user,
                           cut_str=cut_str)


@app.route('/user/<user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id: int):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        abort(404)
    if current_user != user:
        abort(403)
    form = EditUserForm()
    if form.validate_on_submit():
        user.name = form.name.data
        user.about = form.about.data
        db_sess.commit()
        return redirect(f'/user/{user_id}')
    form.name.data = user.name
    form.about.data = user.about
    return render_template('edit_user.html',
                           title='Изменение пользователя',
                           user=user,
                           form=form)


@app.route('/user/<user_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_user(user_id: int):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        abort(404)
    if current_user != user:
        abort(403)
    form = DeleteUserForm()
    if form.validate_on_submit():
        if user.check_password(form.password.data):
            for i in user.mods:
                db_sess.delete(i)
            for i in user.comments:
                db_sess.delete(i)
            db_sess.delete(user)
            db_sess.commit()
        return redirect('/')
    return render_template('delete_user.html',
                           title='Удаление пользователя',
                           user=user,
                           form=form)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Mod).filter(Mod.mod_id == form.mod_id.data).first():
            return render_template('upload.html', title='Публикация мода', form=form,
                                   message='мод с таким id уже существует')
        mod = Mod(
            name=form.name.data,
            mod_id=form.mod_id.data,
            description=form.description.data,
            version=form.version.data,
            loader=form.loader.data,
            game_version=form.game_version.data,
            min_loader_version=form.min_loader_version.data,
            filename=form.mod_id.data + '.jar'
        )
        current_user.mods.append(mod)
        form.file.data.save(os.path.join(app.config['UPLOAD_FOLDER'], form.mod_id.data + '.jar'))
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(f'/mod/{db_sess.query(Mod).filter(Mod.mod_id == form.mod_id.data).first().id}')
    return render_template('upload.html', title='Публикация мода', form=form)


@app.route('/mod/<mod_id>', methods=['GET', 'POST'])
def mod(mod_id: int):
    db_sess = db_session.create_session()
    form = CommentForm()
    download_form = DownloadModForm()
    if form.validate_on_submit():
        mod = db_sess.query(Mod).get(mod_id)
        comment = Comment(rate=form.rate.data, text=form.text.data)
        mod.comments.append(comment)
        db_sess.merge(mod)
        db_sess.commit()
        db_sess = db_session.create_session()
        current_user.comments.append(comment)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(f'/mod/{mod_id}')
    mod = db_sess.query(Mod).get(mod_id)
    if not mod:
        abort(404)
    if download_form.validate_on_submit():
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], mod.mod_id + '.jar'))
    user_comments = list(filter(lambda x: x.user == current_user, mod.comments))
    can_comment = not bool(user_comments)
    return render_template('mod.html',
                           title=mod.name,
                           mod=mod,
                           form=form,
                           can_comment=can_comment,
                           user_comment=user_comments[0] if user_comments else None,
                           download_form=download_form)


@app.route('/mod/<mod_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_mod(mod_id: int):
    db_sess = db_session.create_session()
    mod = db_sess.query(Mod).get(mod_id)
    if not user:
        abort(404)
    if current_user != mod.user:
        abort(403)
    form = EditModForm()
    if form.validate_on_submit():
        mod.name = form.name.data
        mod.description = form.description.data
        mod.mod_id = form.mod_id.data
        mod.version = form.version.data
        mod.loader = form.loader.data
        mod.game_version = form.game_version.data
        mod.min_loader_version = form.min_loader_version.data
        if form.file.data.filename != '':
            form.file.data.save(os.path.join(app.config['UPLOAD_FOLDER'], form.mod_id.data + '.jar'))
        db_sess.commit()
        return redirect(f'/mod/{mod_id}')
    form.name.data = mod.name
    form.description.data = mod.description
    form.mod_id.data = mod.mod_id
    form.version.data = mod.version
    form.loader.data = mod.loader
    form.game_version.data = mod.game_version
    form.min_loader_version.data = mod.min_loader_version
    return render_template('upload.html',
                           title='Изменение мода',
                           form=form)


@app.route('/mod/<mod_id>/delete')
@login_required
def delete_mod(mod_id: int):
    db_sess = db_session.create_session()
    mod = db_sess.query(Mod).get(mod_id)
    if not mod:
        abort(404)
    if current_user != mod.user:
        abort(403)
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], mod.mod_id + '.jar'))
    for i in mod.comments:
        db_sess.delete(i)
    db_sess.delete(mod)
    db_sess.commit()
    return redirect('/')


@app.route('/comment/<comment_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_comment(comment_id: int):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).get(comment_id)
    if not comment:
        abort(404)
    if current_user != comment.user:
        abort(403)
    mod_id = comment.mod.id
    db_sess.delete(comment)
    db_sess.commit()
    return redirect(f'/mod/{mod_id}')


def main():
    db_session.global_init('db/blogs.db')
    app.run(host='127.0.0.1', port=5000)


if __name__ == '__main__':
    main()
