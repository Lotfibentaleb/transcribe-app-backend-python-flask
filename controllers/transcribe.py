from flask import Blueprint, request, Response, jsonify
from models.utils import *
from datetime import datetime
from app import app
from flask_jwt_extended import (jwt_required, get_jwt_identity)

transcribe = Blueprint("transcribe", __name__)

@transcribe.route("/<int:media_id>", methods=["POST"])
@jwt_required
def audio_transcribe(media_id):
    s3_url = request.json["s3_url"]
    index = request.json["index"]
    app.logger.debug('888888888888888888888')
    app.logger.debug(media_id)
    app.logger.debug(s3_url)
    app.logger.debug('888888888888888888888')
    time.sleep(4)
    job_name = str(media_id) + '_' + str(time.time())
    # transcribe_url = transcribe_file(job_name, s3_url)
    transcribe_url = "https://transcribe-datas.s3.amazonaws.com/test1.json"
    file_name = db_read("""SELECT file_name FROM media_datas where id=%s""", (str(media_id),),)
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    if (db_write("""UPDATE media_datas SET transcribe_status=%s, transcribe_url=%s, updatedAt=%s WHERE id=%s""",
                ("1", transcribe_url, formatted_date, str(media_id)),
                )):
        return jsonify({"msg": "success", "success": "true", "transcribe_url": transcribe_url, "mediaId": media_id, "index": index, "file_name": file_name[0]['file_name']}), 201
    else:
        return jsonify({"msg": "failed transcribe", "success": "false"})

