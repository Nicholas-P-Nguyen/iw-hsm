import flask
import json
from . import crypto
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask import url_for, redirect, session, jsonify


app = flask.Flask(__name__, template_folder='../templates', static_folder='../static')

@app.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html')

#-----------------------------------------------------------------------
# Encryption/Decryption routes
#-----------------------------------------------------------------------

@app.route('/encrypt', methods=["POST"])
def encrypt():
    file = flask.request.files.get("file")

    if not file:
        return "No file uploaded", 400
    
    file_bytes = file.read()
    payload = crypto.encrypt_data(file_bytes, file.filename, file.mimetype)
    return jsonify(payload)
    
@app.route('/decrypt', methods=["POST"])
def decrypt():
    file = flask.request.files.get("payload")
    if not file:
        return "No file uploaded", 400
    
    try:
        payload = json.load(file)
        decrypted_data, filename, mimetype = crypto.decrypt_data(payload)
        return decrypted_data, 200, {
            'Content-Type': mimetype,
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
    except Exception as e:
        return f"Decryption failed: {str(e)}", 500
    