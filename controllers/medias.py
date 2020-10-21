from flask import Blueprint, request, Response, jsonify
from models.utils import *
from datetime import datetime
from werkzeug.utils import secure_filename
from settings import S3_MEDIA_BUCKET
from flask_jwt_extended import (jwt_required, get_jwt_identity)
from flask_cors import CORS
import subprocess
import json

medias = Blueprint("medias", __name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})

@medias.route("/", methods=["GET"])
# @jwt_required
def media_list():
    current_user = get_jwt_identity()
    print('666666666666666666666666666666666666')
    print(current_user)
    print('666666666666666666666666666666666666')
    media_list = db_read("SELECT * FROM media_datas", (), )
    if media_list:
        return jsonify({"msg": "media list success", "success": "true", "media_list": media_list})
    else:
        return jsonify({"msg": "no data", "success": "true"})

@medias.route("/delete/<int:media_id>", methods=["GET"])
# @jwt_required
def media_delete(media_id):
    if db_write("""DELETE FROM media_datas WHERE id=%s""", [media_id]):
        media_datas = db_read("SELECT * FROM media_datas", (), )
        if media_datas:
            return jsonify({"media_list": media_datas, "msg": "deleted media successfully", "success": "true"})
        else:
            return jsonify({"msg": "delete media fail"}), 409
    else:
        return jsonify({"msg": "delete media fail"}), 409


@medias.route("/upload", methods=["POST"])
# @jwt_required
def media_upload():
    if 'file' not in request.files:
        app.logger.debug('No file part')
        return jsonify({"msg": "No file part", "success": "false"}), 401
    files = request.files.getlist('file')
    if len(files) == 0:
        return jsonify({"msg": "No selected file", "success": "false"})
    else:
        index = request.values['index']
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        for file in files:
            if file.filename == '':
                app.logger.debug('No selected file')
            else:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    file_detail_info_command = "ffprobe -i " + app.config["UPLOAD_FOLDER"] + "/" + filename + " -v quiet -print_format json -show_format"
                    media_file_detail = subprocess.check_output([file_detail_info_command], shell=True)
                    json_media_detail = json.loads(media_file_detail)
                    file_remove_command = "rm -rf " + app.config["UPLOAD_FOLDER"] + "/" + filename
                    subprocess.check_output([file_remove_command], shell=True)
                    file.seek(0) # setting the file interpreter into the header
                    distinguish_result = distinguish_audio_video(json_media_detail["format"]["format_name"])
                    if (distinguish_result == "audio"):
                        s3_full_url = upload_file_to_s3(file, S3_MEDIA_BUCKET, app.config["S3_AUDIO_SUB_FOLDER"],
                                                        app.config["S3_MEDIA_LOCATION"], 17)
                    elif (distinguish_result == "video"):
                        s3_full_url = upload_file_to_s3(file, S3_MEDIA_BUCKET, app.config["S3_VIDEO_SUB_FOLDER"],
                                                        app.config["S3_MEDIA_LOCATION"], 17)
                    else:
                        return jsonify({"msg": "wrong file format", "success": "false"}), 201
                    if db_write(
                        """INSERT INTO media_datas (userId, file_name, s3_url, file_extension, transcribe_status, duration, file_size, createdAt, updatedAt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (17, filename, s3_full_url, json_media_detail["format"]["format_name"], '0', json_media_detail["format"]["duration"], json_media_detail["format"]["size"], formatted_date, formatted_date),):
                        media_data = db_read(
                            "SELECT id, duration FROM media_datas where userId=%s and file_name=%s and s3_url like %s",
                            ("17", filename, s3_full_url),)
                        if (media_data):
                            return jsonify({"msg": "uploaded file successfully", "index": index, "s3_url": s3_full_url, "mediaId": media_data[0]["id"], "playTime": media_data[0]["duration"],
                                            "success": "true"}), 201
                        else: return jsonify({"msg": "failed saving db", "success": "false"}), 201
                    else: return jsonify({"msg": "failed saving db", "success": "false"}), 201
                else: return jsonify({"msg": "unavailable file format", "success": "false"})
