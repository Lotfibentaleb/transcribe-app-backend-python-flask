from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS
from settings import MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_HOST, JWT_SECRET_KEY, S3_MEDIA_BUCKET, S3_TRANSCRIBE_BUCKET, UPLOAD_FOLDER, AUDIO_EXTENSION, VIDEO_EXTENSION
from flask_jwt_extended import (
    JWTManager
)
import logging

app = Flask(__name__)
CORS(
    app, origins="*", allow_headers=[
        "Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
        supports_credentials=True, intercept_exceptions=False
)

# CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
# CORS(app, expose_headers='Authorization')

# app.config['CORS_ORIGINS'] = '*'
# app.config['CORS_SUPPORTS_CREDENTIALS'] = 'True'
# app.config['CORS_HEADERS'] = 'Content-Type'

app.debug = True
app.config['PROPAGATE_EXCEPTIONS'] = True
logging.getLogger('flask_cors').level = logging.DEBUG
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["AUDIO_EXTENSION"] = AUDIO_EXTENSION
app.config["VIDEO_EXTENSION"] = VIDEO_EXTENSION
app.config["MYSQL_USER"] = MYSQL_USER
app.config["MYSQL_PASSWORD"] = MYSQL_PASSWORD
app.config["MYSQL_DB"] = MYSQL_DB
app.config["MYSQL_HOST"] = MYSQL_HOST
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
app.config["S3_MEDIA_LOCATION"] = 'https://{}.s3.amazonaws.com/'.format(S3_MEDIA_BUCKET)
app.config["S3_TRANSCRIBE_LOCATION"] = 'https://{}.s3.amazonaws.com/'.format(S3_TRANSCRIBE_BUCKET)
app.config["S3_AUDIO_SUB_FOLDER"] = 'audio-datas'
app.config["S3_VIDEO_SUB_FOLDER"] = 'video-datas'
db = MySQL(app)
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
jwt = JWTManager(app)

if __name__ == '__main__':
    @app.route("/")
    def hello():
        return "Hello world!"
    from controllers.auth import auth
    app.register_blueprint(auth, url_prefix="/api/auth")
    from controllers.users import users
    app.register_blueprint(users, url_prefix="/api/users")
    from controllers.transcribe import transcribe
    app.register_blueprint(transcribe, url_prefix="/api/transcribe")
    from controllers.medias import medias
    app.register_blueprint(medias, url_prefix="/api/medias")
    app.run(host="0.0.0.0", port=5000, debug=True)



