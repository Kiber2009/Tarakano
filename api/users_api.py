from flask import Blueprint, jsonify, make_response
from data import db_session
from data.users import User

blueprint = Blueprint('users_api', __name__, template_folder='templates')


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify([i.to_dict(only=('id', 'name', 'about', 'created_date')) for i in users])


@blueprint.route('/api/users/<user_id>')
def get_user(user_id: int):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(user.to_dict(only=('id', 'name', 'about', 'created_date')))
