from sqlalchemy import or_
from app import app, db
from app.models import Link, User
from app.errors import error_response
from flask import jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth


#### Section for Authentication
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

## Tokens-Section
@app.route('/api/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return jsonify({'token':token})

@app.route('/api/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204


# Helper for HttpAuth
@basic_auth.verify_password
def verify_password(username,password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None

@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)

@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None

@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)


## End Tokens

@app.route('/api/links/<string:search>', methods=['GET'])
@token_auth.login_required
def get_links_of(search):
    links = Link.query.filter(or_(
            Link.keywords.ilike(f'%{search}%'),
            Link.link.ilike(f'%{search}%')
        )).all()

    data = {'links':[link.to_dict() for link in links]}
    return jsonify(data)

@app.route('/api/links', methods=['GET'])
@token_auth.login_required
def get_links():
    data = Link.to_collection()
    return jsonify(data)
