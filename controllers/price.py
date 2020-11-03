from flask import Blueprint, request, jsonify
from models.utils import *
from datetime import datetime
from flask_jwt_extended import (jwt_required)

price = Blueprint("price", __name__)

@price.route("/edit", methods=["POST"])
@jwt_required
def price_edit():
    minimum_price = request.json["minimum_price"]
    price_per_minute = request.json["price_per_minute"]
    price_per_half_minute = request.json["price_per_half_minute"]
    print("minimum_price", minimum_price)
    print("price_per_minute", price_per_minute)
    print("price_per_half_minute", price_per_half_minute)
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    if (db_write("""UPDATE transcribe_price SET price_per_minute=%s, price_per_half_minute=%s, minimum_price=%s, updatedAt=%s WHERE id=%s""",
                (price_per_minute, price_per_half_minute, minimum_price, formatted_date, "1"),
                )):
        price = db_read("""SELECT * FROM transcribe_price""",
                            (), )
        return jsonify({"jwt_token": refresh_token(), "msg": "success", "success": "true", "price": price[0]}), 201
    else:
        return jsonify({"jwt_token": refresh_token(), "msg": "failed transcribe", "success": "false"})

@price.route("/", methods=["GET"])
@jwt_required
def get_price():
    price = db_read("""SELECT * FROM transcribe_price""",
                            (), )
    if price:
        return jsonify({"jwt_token": refresh_token(), "msg": "success", "success": "true", "price": price[0]})
    else:
        return jsonify({"jwt_token": refresh_token(), "msg": "fail", "success": "false"})

@price.route("/dashboard", methods=["GET"])
@jwt_required
def get_dashboard_data():
    all_visitors = db_read("""SELECT count(*) as all_visitors FROM users""",
                            (), )
    all_users = db_read("""SELECT count(*) as all_users FROM users WHERE activate=%s""",
                            ('1',), )

    today_visitors = db_read("""SELECT count(*) as today_visitors FROM users WHERE updatedAt >= CURDATE()""",
                            (), )

    all_price = db_read("""SELECT SUM(price) as all_price FROM media_datas""",
                            (), )
    all_aws_price = db_read("""SELECT SUM(aws_price) as all_aws_price FROM media_datas""",
                 (),)
    if price:
        return jsonify({"jwt_token": refresh_token(), "msg": "success", "success": "true", "all_price": all_price[0]["all_price"]
                           , "all_aws_price": all_aws_price[0]["all_aws_price"], "all_visitors": all_visitors[0]["all_visitors"], "all_users": all_users[0]["all_users"], "today_visitors": today_visitors[0]["today_visitors"]})
    else:
        return jsonify({"jwt_token": refresh_token(), "msg": "fail", "success": "false"})

