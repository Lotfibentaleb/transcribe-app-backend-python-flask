from flask import Blueprint, request, jsonify
from models.utils import *
from datetime import datetime
from flask_jwt_extended import (jwt_required, get_jwt_identity)

users = Blueprint("users", __name__)

@users.route("/", methods=["GET"])
@jwt_required
def user_list():
    current_user = get_jwt_identity()
    user_id = current_user["user_id"]
    user_permission = current_user["permission"]
    if user_permission == "admin":
        user_list = db_read("""SELECT id, email, first_name, last_name, permission, createdAt, updatedAt FROM users WHERE activate=%s""", ("1",),)
    else:
        user_list = db_read("""SELECT id, email, first_name, last_name, permission, createdAt, updatedAt FROM users WHERE id=%s""", (str(user_id),),)
    if user_list:
        return jsonify({"jwt_token": refresh_token(), "msg": "success", "success": "true", "users": user_list})
    else:
        return jsonify({"jwt_token": refresh_token(), "msg": "fail", "success": "false"})

@users.route("/add", methods=["POST"])
@jwt_required
def user_add():
    user_email = request.json["email"]
    user_password = "123456"
    user_first_name = request.json["first_name"]
    user_last_name = request.json["last_name"]

    current_user = db_read("""SELECT * FROM users WHERE email = %s""", (user_email,))
    if len(current_user) != 0:
        return jsonify({"jwt_token": refresh_token(), "msg": "existing the same user"})

    password_salt = generate_salt()
    password_hash = generate_hash(user_password, password_salt)
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    if db_write(
            """INSERT INTO users (email, password_salt, password_hash, first_name, last_name, permission, createdAt, updatedAt, activate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (user_email, password_salt, password_hash, user_first_name, user_last_name, "user", formatted_date, formatted_date, "1"),
    ):
        user_list = db_read("""SELECT id, email, first_name, last_name, createdAt, updatedAt FROM users WHERE activate=%s""", ("1",),)
        if user_list:
            return jsonify({"jwt_token": refresh_token(), "users": user_list, "msg": "success", "success": "true"})
        else:
            return jsonify({"jwt_token": refresh_token(), "msg": "fail"}), 409
    else:
        return jsonify({"jwt_token": refresh_token(), "msg": "fail"}), 409

@users.route("/edit/<int:user_id>", methods=["POST"])
@jwt_required
def user_edit(user_id):
    user_email = request.json["email"]
    user_first_name = request.json["first_name"]
    user_last_name = request.json["last_name"]

    if db_write("""UPDATE users SET email=%s, first_name=%s, last_name=%s WHERE id=%s""", (user_email, user_first_name, user_last_name, [user_id]),
    ):
        user_list = db_read("""SELECT id, email, first_name, last_name, createdAt, updatedAt FROM users""", (), )
        if user_list:
            return jsonify({"jwt_token": refresh_token(), "users": user_list, "msg": "success"})
        else:
            return jsonify({"jwt_token": refresh_token(), "msg": "fail"}), 409
    else:
        return jsonify({"jwt_token": refresh_token(), "msg": "fail"}), 409

@users.route("/delete/<int:user_id>", methods=["GET"])
@jwt_required
def user_delete(user_id):
    if db_write("""UPDATE users SET activate=%s WHERE id=%s""", ('0', [user_id])):
        user_list = db_read("""SELECT id, email, first_name, last_name, createdAt, updatedAt FROM users WHERE activate=%s""", ("1",), )
        if user_list:
            return jsonify({"jwt_token": refresh_token(), "users": user_list, "msg": "success", "success": "true"})
        else:
            return jsonify({"jwt_token": refresh_token(), "msg": "fail", "success": "false"}), 409
    else:
        return jsonify({"jwt_token": refresh_token(), "msg": "fail", "success": "false"}), 409

@users.route("/profile", methods=["GET"])
@jwt_required
def user_profile():
    current_user = get_jwt_identity()
    user_id = current_user["user_id"]
    profile = db_read("""SELECT id, email, first_name, last_name, permission, createdAt, updatedAt FROM users WHERE id=%s""", (str(user_id),),)
    if profile:
        return jsonify({"jwt_token": refresh_token(), "msg": "success", "success": "true", "profile": profile})
    else:
        return jsonify({"jwt_token": refresh_token(), "msg": "fail", "success": "false"})

@users.route("/resetpassword", methods=["POST"])
@jwt_required
def reset_password():
    current_user = get_jwt_identity()
    user_id = current_user["user_id"]
    current_password = request.json["current_password"]
    new_password = request.json["new_password"]
    confirm_password = request.json["confirm_password"]

    # profile = db_read("""SELECT id, email, first_name, last_name, permission, createdAt, updatedAt FROM users WHERE id=%s""", (str(user_id),),)
    # if profile:
    #     return jsonify({"jwt_token": refresh_token(), "msg": "success", "success": "true", "profile": profile})
    # else:
    #     return jsonify({"jwt_token": refresh_token(), "msg": "fail", "success": "false"})
