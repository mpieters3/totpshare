from .config import Config
from .token import get_token
from .forms import AddForm
from .totpshare import oidc, app, secrets
from .secrets_providers import secretsmetadata
try:
    from flask import Flask, request, flash, jsonify, render_template, redirect
except:
    raise ImportError("Unable to access Crypto.Cipher")

@app.route('/')
@oidc.require_login
def index():
    return render_template('index.html', secrets=secrets.list_keys())

@app.route('/admin', methods=['GET', 'POST'])
@oidc.require_login
def admin():
    user_groups = oidc.user_getinfo(['groups'])['groups']
    if(Config.AUTHZ_ADMIN is not None and Config.AUTHZ_ADMIN not in user_groups):
        flash('Admins must be a member of the {} group, has {}'.format(Config.AUTHZ_ADMIN, str(user_groups)))
        return redirect('/')
    form = AddForm()
    if form.validate_on_submit():
        secrets.add_key(secretsmetadata(form.id.data,form.display_name.data), form.secret.data)
        flash('Added key {}({})'.format(form.display_name.data, form.id.data))
        return redirect('/')
    return render_template('admin.html', title='Manage Keys', form=form, secrets=secrets.list_keys())

@app.route('/logout', methods=['GET'])
def logout():
    oidc.logout()
    return render_template('logout.html', title='Manage Keys')

@app.route('/secret/<string:key>')
@oidc.require_login
def view_secret(key: str):
    key = secrets.get_secret(key)
    token, time_remaining = get_token(key)
    return jsonify(token=token, time_remaining=time_remaining)

@app.route('/api/secrets', methods=['GET'])
@oidc.require_login
def list_secrets():
    return jsonify([e.serialize() for e in secrets.list_keys()]), 200

@app.route('/api/secrets', methods=['POST'])
@oidc.require_login
def add_secret():
    user_groups = oidc.user_getinfo(['groups'])['groups']
    if(Config.AUTHZ_ADMIN is not None and Config.AUTHZ_ADMIN not in user_groups):
        flash('Admins must be a member of the {} group, has {}'.format(Config.AUTHZ_ADMIN, str(user_groups)))
        return redirect('/')
    data = request.get_json()
    id = secrets.add_key(secretsmetadata(data['id'],data['display_name']), data['key'])
    return jsonify({'key': id}), 200

@app.route('/api/secrets/<string:key>', methods=['GET'])
@oidc.require_login
def get_secret(key: str):
    key = secrets.get_secret(key)
    token, time_remaining = get_token(key)
    return jsonify({
        'token': token,
        'time_remaining': time_remaining
    })

@app.route('/api/secrets/<string:key>', methods=['DELETE', 'POST'])
@oidc.require_login
def delete_token(key: str):
    user_groups = oidc.user_getinfo(['groups'])['groups']
    if(Config.AUTHZ_ADMIN is not None and Config.AUTHZ_ADMIN not in user_groups):
        flash('Admins must be a member of the {} group, has {}'.format(Config.AUTHZ_ADMIN, str(user_groups)))
        return redirect('/')
    secrets.delete_key(key)
    if request.method == 'POST':
        return redirect('/admin')
    return None, 204
