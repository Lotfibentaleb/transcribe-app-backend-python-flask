from flask import Blueprint, request, Response, jsonify
from models.utils import *
from app import app

transcribe = Blueprint("transcribe", __name__)

@transcribe.route("/<int:user_id>/<filename>", methods=["POST"])

def audio_transcribe(user_id, filename):
    s3_url = request.json["s3_url"]

    app.logger.debug('888888888888888888888')
    app.logger.debug([user_id])
    app.logger.debug(filename)
    app.logger.debug(s3_url)
    app.logger.debug('888888888888888888888')

    transcribe_file('Example-job', s3_url)

    return jsonify({"result": "success"}), 201