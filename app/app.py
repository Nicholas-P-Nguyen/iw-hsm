import flask
import json
import io
import crypto
from werkzeug.utils import secure_filename

app = flask.Flask(__name__, template_folder='templates')

#-----------------------------------------------------------------------
# Applications routes
#-----------------------------------------------------------------------
@app.route('/encrypt', methods=["POST"])
def encrypt():
    # TODO: Connect with the front end to get the file user wants to encrypt
    file = flask.request.files.get("file")

    if not file:
        return "No file uploaded", 400
    
    file_bytes = file.stream.read()
    payload = crypto.encrypt_data(file_bytes)

    payload["original_filename"] = secure_filename(file.filename)
    payload["original_mimetype"] = file.mimetype

    json_data = json.dumps(payload, indent=2)
    encrypted_file = io.BytesIO(json_data.encode("utf-8"))

    return flask.send_file(
        encrypted_file,
        as_attachment=True,
        download_name="encrypted_payload.json",
        mimetype="application/json"
    )
    
@app.route('/decrypt', methods=["POST"])
def decrypt():
    # TODO: Connect with the front end to get payload user wants to decrypt
    file = flask.request.files.get("payload")
    if not file:
        return "No file uploaded", 400
    
    try:
        payload = json.load(file)
        decrypted_data = crypto.decrypt_data(payload)
        decrypted_file = io.BytesIO(decrypted_data)
        download_name = payload.get("original_filename", "decrypted_file.txt")
        mimetype = payload.get("original_mimetype", "application/octet-stream")
        return flask.send_file(
            decrypted_file,
            as_attachment=True,
            download_name=download_name,
            mimetype=mimetype
        )
    except Exception as e:
        return f"Decryption failed: {str(e)}", 500
    
