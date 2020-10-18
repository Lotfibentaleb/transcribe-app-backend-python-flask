from flask import Blueprint, request, Response, jsonify
from models.utils import *
from datetime import datetime
from werkzeug.utils import secure_filename
from settings import S3_MEDIA_BUCKET, S3_TRANSCRIBE_BUCKET

medias = Blueprint("medias", __name__)

app.config["S3_MEDIA_LOCATION"] = 'https://{}.s3.amazonaws.com/'.format(S3_MEDIA_BUCKET)
app.config["S3_TRANSCRIBE_LOCATION"] = 'https://{}.s3.amazonaws.com/'.format(S3_TRANSCRIBE_BUCKET)
app.config["S3_AUDIO_SUB_FOLDER"] = 'audio-datas'
app.config["S3_VIDEO_SUB_FOLDER"] = 'video-datas'

@medias.route("/", methods=["GET"])
def media_list():
    media_list = db_read("SELECT * FROM media_datas", (), )
    if media_list:
        return jsonify({"media_datas": media_list})

@medias.route("/delete/<int:media_id>", methods=["GET"])
def media_delete(media_id):
    if db_write("""DELETE FROM media_datas WHERE mediaId=%s""", [media_id]):
        media_datas = db_read("SELECT * FROM media_datas", (), )
        if media_datas:
            return jsonify({"media_list": media_datas, "message": "success"})
        else:
            return jsonify({"message": "fail"}), 409
    else:
        return jsonify({"message": "fail"}), 409


@medias.route("/upload", methods=["POST"])
def media_upload():
    if 'file' not in request.files:
        app.logger.debug('No file part')
        return jsonify({"result": "No file part"}), 401
    files = request.files.getlist('file')
    if len(files) == 0:
        return jsonify({"result": "No selected file"})
    else:
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        for file in files:
            if file.filename == '':
                app.logger.debug('No selected file')
            else:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    s3_full_url = upload_file_to_s3(file, S3_MEDIA_BUCKET, app.config["S3_AUDIO_SUB_FOLDER"],
                                                    app.config["S3_MEDIA_LOCATION"], 17)
                    db_write(
                        """INSERT INTO media_datas (userId, file_name, s3_url, file_extension, transcribe_status, createdAt, updatedAt) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (17, filename, s3_full_url, 'mp3', '0', formatted_date, formatted_date),
                    )
    return jsonify({"result": "success"}), 201
