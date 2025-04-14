import flask
import json
import io
from . import crypto
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from authlib.integrations.flask_client import OAuth
from flask import url_for, redirect, session, jsonify


app = flask.Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.getenv("APP_SECRET_KEY")
oauth = OAuth(app)

# Oauth config
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'profile email'}
)

#-----------------------------------------------------------------------
# OAuth Routes for Authorization
#-----------------------------------------------------------------------
@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo', token=token)
    user_info = resp.json()
    return redirect('/')


#-----------------------------------------------------------------------
# Encryption/Decryption routes
#-----------------------------------------------------------------------

@app.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


@app.route('/encrypt', methods=["POST"])
def encrypt():
    file = flask.request.files.get("file")

    if not file:
        return "No file uploaded", 400
    
    file_bytes = file.read()
    payload = crypto.encrypt_data(file_bytes)
    return jsonify(payload)
    
@app.route('/decrypt', methods=["POST"])
def decrypt():
    # TODO: Connect with the front end to get payload user wants to decrypt
    file = flask.request.files.get("payload")
    if not file:
        return "No file uploaded", 400
    
    try:
        payload = json.load(file)
        decrypted_data = crypto.decrypt_data(payload)
        return decrypted_data, 200, {
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': 'attachment; filename="decrypted_output"'
        }
    except Exception as e:
        return f"Decryption failed: {str(e)}", 500
    