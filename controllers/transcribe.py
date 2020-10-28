from flask import Blueprint, request, jsonify
from models.utils import *
from datetime import datetime
from flask_jwt_extended import (jwt_required)

transcribe = Blueprint("transcribe", __name__)

@transcribe.route("/<int:media_id>", methods=["POST"])
@jwt_required
def audio_transcribe(media_id):
    s3_url = request.json["s3_url"]
    index = request.json["index"]
    time.sleep(4)
    job_name = str(media_id) + '_' + str(time.time())
    transcribe_url = transcribe_file(job_name, s3_url)
    # transcribe_url = "https://transcribe-datas.s3.amazonaws.com/test1.json" // for testing on local
    file_name = db_read("""SELECT file_name FROM media_datas where id=%s""", (str(media_id),),)
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    if (db_write("""UPDATE media_datas SET transcribe_status=%s, transcribe_url=%s, updatedAt=%s WHERE id=%s""",
                ("1", transcribe_url, formatted_date, str(media_id)),
                )):
        return jsonify({"jwt_token": refresh_token(), "msg": "success", "success": "true", "transcribe_url": transcribe_url, "mediaId": media_id, "index": index, "file_name": file_name[0]['file_name']}), 201
    else:
        return jsonify({"jwt_token": refresh_token(), "msg": "failed transcribe", "success": "false"})

