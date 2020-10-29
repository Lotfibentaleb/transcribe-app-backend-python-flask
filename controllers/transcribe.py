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
    job_name = str(media_id) + '_' + str(time.time())
    transcribe_url = transcribe_file(job_name, s3_url)
    s3_job_name = job_name + ".json"
    # transcribe_url = "https://transcribe-datas.s3.amazonaws.com/test1.json" // for testing on local
    file_name = db_read("""SELECT file_name FROM media_datas where id=%s""", (str(media_id),),)
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    if (db_write("""UPDATE media_datas SET transcribe_status=%s, transcribe_url=%s, transcribe_s3_url=%s, updatedAt=%s WHERE id=%s""",
                ("1", transcribe_url, s3_job_name, formatted_date, str(media_id)),
                )):
        uri = s3.generate_presigned_url('get_object', Params={'Bucket': S3_TRANSCRIBE_BUCKET, 'Key': s3_job_name},
                                              ExpiresIn=259200) # expire 3 * 24 * 3600
        print("presigned_url", uri)
        return jsonify({"jwt_token": refresh_token(), "msg": "success", "success": "true", "transcribe_url": uri, "mediaId": media_id, "index": index, "file_name": file_name[0]['file_name']}), 201
    else:
        return jsonify({"jwt_token": refresh_token(), "msg": "failed transcribe", "success": "false"})

