from flask import Blueprint, jsonify, make_response
from data import db_session
from data.mods import Mod

blueprint = Blueprint('mods_api', __name__, template_folder='templates')


@blueprint.route('/api/mods')
def get_mods():
    db_sess = db_session.create_session()
    mods = db_sess.query(Mod).all()
    return jsonify([i.to_dict(only=(
        'id', 'mod_id', 'name', 'description', 'version', 'loader', 'game_version', 'min_loader_version',
        'uploaded_date', 'user_id'
    )) for i in mods])


@blueprint.route('/api/mods/<mod_id>')
def get_mod(user_id: int):
    db_sess = db_session.create_session()
    mod = db_sess.query(Mod).get(user_id)
    if not mod:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(mod.to_dict(only=(
        'id', 'mod_id', 'name', 'description', 'version', 'loader', 'game_version', 'min_loader_version',
        'uploaded_date', 'user_id'
    )))
