from flask import Blueprint, request, Response, jsonify
from models.utils import *
from app import app
from datetime import datetime
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

auth = Blueprint("auth", __name__)

app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)

@auth.route("/register", methods=["POST"])
def register_user():
    user_email = request.json["email"]
    user_password = request.json["password"]
    user_confirm_password = request.json["confirm_password"]
    user_first_name = request.json["first_name"]
    user_last_name = request.json["last_name"]

    current_user = db_read("""SELECT * FROM users WHERE email = %s""", (user_email,))
    if len(current_user) != 0:
        return jsonify({"err_message": "existing the same user"})

    if user_password == user_confirm_password and validate_user_input(
        "authentication", email=user_email, password=user_password
    ):
        password_salt = generate_salt()
        password_hash = generate_hash(user_password, password_salt)
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        if db_write(
            """INSERT INTO users (email, password_salt, password_hash, first_name, last_name, permission, createdAt, updatedAt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (user_email, password_salt, password_hash, user_first_name, user_last_name, "user", formatted_date, formatted_date),
        ):
            user_token = validate_user(user_email, user_password)

            if user_token:
                # Registration Successful
                return jsonify({"jwt_token": user_token}), 201
            else:
                return Response(status=401)
        else:
            # Registration Failed
            return Response(status=409)
    else:
        # Registration Failed
        return Response(status=400)

@auth.route("/login", methods=["POST"])
def login_user():
    user_email = request.json["email"]
    user_password = request.json["password"]

    current_user = db_read("""SELECT * FROM users WHERE email = %s""", (user_email,))

    # user_id = current_user[0].id
    # permission = current_user[0].permission

    app.logger.debug(user_email)
    app.logger.debug(user_password)
    app.logger.debug(current_user[0]["permission"])

    user_token = validate_user(user_email, user_password)

    # user_token = create_access_token(identity={"id": 7, "permission": "user"})

    if user_token:
        return jsonify({"jwt_token": user_token, "permission": current_user[0]["permission"]})
    else:
        return Response(status=401)