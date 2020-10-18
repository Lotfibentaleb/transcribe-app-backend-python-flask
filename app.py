from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS
from settings import MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_HOST, JWT_SECRET_KEY

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.debug = True

app.config["MYSQL_USER"] = MYSQL_USER
app.config["MYSQL_PASSWORD"] = MYSQL_PASSWORD
app.config["MYSQL_DB"] = MYSQL_DB
app.config["MYSQL_HOST"] = MYSQL_HOST
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
db = MySQL(app)
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY

if __name__ == '__main__':
    from controllers.auth import auth
    app.register_blueprint(auth, url_prefix="/api/auth")
    from controllers.users import users
    app.register_blueprint(users, url_prefix="/api/users")
    from controllers.transcribe import transcribe
    app.register_blueprint(transcribe, url_prefix="/api/transcribe")
    from controllers.medias import medias
    app.register_blueprint(medias, url_prefix="/api/medias")
    app.run(host="192.168.149.137", port=5000, debug=True)



