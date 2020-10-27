from flask import Blueprint, request, Response, jsonify
from models.utils import *
from datetime import datetime
from app import app
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
        return jsonify({"jwt_token": refresh_token(), "msg": "success", "success": "true", "price_data": price}), 201
    else:
        return jsonify({"jwt_token": refresh_token(), "msg": "failed transcribe", "success": "false"})

@price.route("/", methods=["GET"])
@jwt_required
def get_price():
    price = db_read("""SELECT * FROM transcribe_price""",
                            (), )
    if price:
        return jsonify({"jwt_token": refresh_token(), "msg": "success", "success": "true", "price_data": price})
    else:
        return jsonify({"jwt_token": refresh_token(), "msg": "fail", "success": "false"})

