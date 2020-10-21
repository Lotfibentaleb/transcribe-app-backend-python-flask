from flask import Blueprint, request, Response, jsonify
from models.utils import *
from datetime import datetime
from flask_jwt_extended import create_access_token

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["POST"])
def register_user():
    user_email = request.json["email"]
    user_password = request.json["password"]
    user_confirm_password = request.json["confirm_password"]
    user_first_name = request.json["first_name"]
    user_last_name = request.json["last_name"]

    current_user = db_read("""SELECT * FROM users WHERE email = %s""", (user_email,))
    if len(current_user) != 0:
        return jsonify({"msg": "existing the same user", "success": "false"})

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

            return jsonify({"msg": "Registration Success", "success": "true"}), 201

        else:
            # Registration Failed
            return jsonify({"msg": "Registration Failed", "success": "false"}), 401
    else:
        # Registration Failed
        return jsonify({"msg": "Registration Failed", "success": "false"}), 401

@auth.route("/login", methods=["POST"])
def login_user():
    user_email = request.json["email"]
    user_password = request.json["password"]
    current_user = db_read("""SELECT * FROM users WHERE email = %s""", (user_email,))
    # user_token = validate_user(user_email, user_password)

    user_token = create_access_token(identity=user_email)

    if user_token:
        return jsonify({"msg": "login success", "success": "true", "jwt_token": user_token, "permission": current_user[0]["permission"]})
    else:
        return Response(status=401)