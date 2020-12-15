from flask import Blueprint, request, jsonify
from models.utils import *
from helpers.emailTemplate.forgotPassword import *
from services.mailservice import *
from datetime import datetime
import random
import string

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
            """INSERT INTO users (email, password_salt, password_hash, first_name, last_name, permission, createdAt, updatedAt, activate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (user_email, password_salt, password_hash, user_first_name, user_last_name, "user", formatted_date, formatted_date, "1"),
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
    user_token = validate_user(user_email, user_password)
    if user_token:
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        db_write("""UPDATE users SET updatedAt=%s WHERE id=%s""", (formatted_date, current_user[0]["id"]),)
        # send_mail('bluestreak66@protonmail.com', 'sign in', 'test', '<html><body>Hello</body></html>')
        return jsonify({"msg": "login success", "success": "true", "jwt_token": user_token, "permission": current_user[0]["permission"]})
    else:
        return jsonify({"msg": "bad user email or password", "success": "false"}), 201

@auth.route("/forgotpassword", methods=["POST"])
def forgot_password():
    user_email = request.json["email"]
    current_user = db_read("""SELECT * FROM users WHERE email = %s""", (user_email,))
    if len(current_user) == 1:
        letters = string.ascii_letters
        landom_password = ''.join(random.choice(letters) for i in range(6))
        # print("Random string is:", landom_password)
        password_salt = generate_salt()
        password_hash = generate_hash(landom_password, password_salt)
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        db_write("""UPDATE users SET password_salt=%s, password_hash=%s, updatedAt=%s WHERE id=%s""", (password_salt, password_hash, formatted_date, current_user[0]["id"]), )
        html = getForgotPassworHtml(landom_password)
        send_mail(user_email, 'Received New Password from www.accuscript.ai', 'Forgot Password', html)
        return jsonify({"msg": "Success, Please check your email!", "success": "true"})
    else:
        return jsonify({"msg": "Does not exist email, Please sign up first", "success": "false"})