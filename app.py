from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS
from settings import MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_HOST


app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.debug = True

app.config["MYSQL_USER"] = MYSQL_USER
app.config["MYSQL_PASSWORD"] = MYSQL_PASSWORD
app.config["MYSQL_DB"] = MYSQL_DB
app.config["MYSQL_HOST"] = MYSQL_HOST
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

db = MySQL(app)


if __name__ == '__main__':
    from blueprint_auth import auth
    app.register_blueprint(auth, url_prefix="/api/auth")
    from blueprint_users import users
    app.register_blueprint(users, url_prefix="/api/users")
    app.run(host="192.168.149.136", port=5000, debug=True)



