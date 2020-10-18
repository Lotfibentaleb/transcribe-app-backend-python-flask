from flask import Blueprint, request, Response, jsonify
from models.utils import *
from datetime import datetime

users = Blueprint("users", __name__)

@users.route("/", methods=["GET"])
def user_list():
    user_list = db_read("""SELECT id, email, first_name, last_name, permission, createdAt, updatedAt FROM users""", (),)
    if user_list:
        return jsonify({"users": user_list})

@users.route("/add", methods=["POST"])
def user_add():
    user_email = request.json["email"]
    user_password = "123456"
    user_first_name = request.json["first_name"]
    user_last_name = request.json["last_name"]

    current_user = db_read("""SELECT * FROM users WHERE email = %s""", (user_email,))
    if len(current_user) != 0:
        return jsonify({"message": "existing the same user"})

    password_salt = generate_salt()
    password_hash = generate_hash(user_password, password_salt)
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    if db_write(
            """INSERT INTO users (email, password_salt, password_hash, first_name, last_name, permission, createdAt, updatedAt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (user_email, password_salt, password_hash, user_first_name, user_last_name, "user", formatted_date, formatted_date),
    ):
        user_list = db_read("""SELECT id, email, first_name, last_name, createdAt, updatedAt FROM users""", (),)
        if user_list:
            return jsonify({"users": user_list, "message": "success"})
        else:
            return jsonify({"message": "fail"}), 409
    else:
        return jsonify({"message": "fail"}), 409


@users.route("/edit/<int:user_id>", methods=["POST"])
def user_edit(user_id):
    # user_id = request.json["id"]
    user_email = request.json["email"]
    user_first_name = request.json["first_name"]
    user_last_name = request.json["last_name"]

    if db_write("""UPDATE users SET email=%s, first_name=%s, last_name=%s WHERE id=%s""", (user_email, user_first_name, user_last_name, [user_id]),
    ):
        user_list = db_read("""SELECT id, email, first_name, last_name, createdAt, updatedAt FROM users""", (), )
        if user_list:
            return jsonify({"users": user_list, "message": "success"})
        else:
            return jsonify({"message": "fail"}), 409
    else:
        return jsonify({"message": "fail"}), 409

@users.route("/delete/<int:user_id>", methods=["GET"])
def user_delete(user_id):
    if db_write("""DELETE FROM users WHERE id=%s""", [user_id]):

        user_list = db_read("""SELECT id, email, first_name, last_name, createdAt, updatedAt FROM users""", (), )
        if user_list:
            return jsonify({"users": user_list, "message": "success"})
        else:
            return jsonify({"message": "fail"}), 409
    else:
        return jsonify({"message": "fail"}), 409
