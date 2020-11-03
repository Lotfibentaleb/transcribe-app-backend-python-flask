from flask import Blueprint, request, jsonify
from models.utils import *
from datetime import datetime
from werkzeug.utils import secure_filename
from settings import S3_MEDIA_BUCKET
from flask_jwt_extended import (jwt_required, get_jwt_identity)
import subprocess
import json
import math

medias = Blueprint("medias", __name__)
@medias.route("/", methods=["GET"])
@jwt_required
def media_list():
    current_user = get_jwt_identity()
    user_id = current_user["user_id"]
    user_permission = current_user["permission"]
    if user_permission == "admin":
        media_list = db_read("SELECT * FROM media_datas", (), )
    else:
        media_list = db_read("SELECT * FROM media_datas where id=%s", (str(user_id),), )
    if media_list:
        return jsonify({"jwt_token": refresh_token(), "msg": "media list success", "success": "true", "media_list": media_list})
    else:
        return jsonify({"jwt_token": refresh_token(), "msg": "no data", "success": "true"})

@medias.route("/search", methods=["POST"])
@jwt_required
def media_search_list():
    start_date = request.json["start_date"]
    end_date = request.json["end_date"]
    current_user = get_jwt_identity()
    user_id = current_user["user_id"]
    user_permission = current_user["permission"]
    if user_permission == "admin":
        media_list = db_read("SELECT * FROM media_datas WHERE createdAt >= date %s and createdAt <= date %s + 1", (start_date, end_date), )
    else:
        media_list = db_read("SELECT * FROM media_datas where id=%s and createdAt >= date %s and createdAt <= date %s", (str(user_id), start_date, end_date), )
    if media_list:
        return jsonify(
            {"jwt_token": refresh_token(), "msg": "media list success", "success": "true", "media_list": media_list})
    else:
        return jsonify({"jwt_token": refresh_token(), "msg": "no data", "success": "true"})

@medias.route("/delete/<int:media_id>", methods=["GET"])
@jwt_required
def media_delete(media_id):
    if db_write("""DELETE FROM media_datas WHERE id=%s""", [media_id]):
        media_datas = db_read("SELECT * FROM media_datas", (), )
        if media_datas:
            return jsonify({"jwt_token": refresh_token(), "media_list": media_datas, "msg": "deleted media successfully", "success": "true"})
        else:
            return jsonify({"jwt_token": refresh_token(), "msg": "no media datas", "success": "true", "media_list": []}), 201
    else:
        return jsonify({"jwt_token": refresh_token(), "msg": "delete media fail", "success": "false"}), 409

@medias.route("/<int:media_id>/url", methods=["GET"])
@jwt_required
def get_presigned_url(media_id):
    file_name = db_read("SELECT transcribe_s3_url FROM media_datas WHERE id=%s",
                         ([media_id],), )
    if (file_name):
        presigned_url = s3.generate_presigned_url('get_object',
                                                  Params={'Bucket': S3_TRANSCRIBE_BUCKET, 'Key': file_name[0]["transcribe_s3_url"]},
                                                  ExpiresIn=259200)  # expire 3 * 24 * 3600
        return jsonify({"jwt_token": refresh_token(), "msg": "success", "success": "true", "transcribe_url": presigned_url}), 201
    else:
        return jsonify(
            {"jwt_token": refresh_token(), "msg": "no media file like that", "success": "true"}), 201

@medias.route("/upload", methods=["POST"])
@jwt_required
def media_upload():
    current_user = get_jwt_identity()
    user_id = current_user["user_id"]
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
                                                        app.config["S3_MEDIA_LOCATION"], user_id)
                    elif (distinguish_result == "video"):
                        s3_full_url = upload_file_to_s3(file, S3_MEDIA_BUCKET, app.config["S3_VIDEO_SUB_FOLDER"],
                                                        app.config["S3_MEDIA_LOCATION"], user_id)
                    else:
                        return jsonify({"msg": "wrong file format", "success": "false"}), 201

                    if db_write(
                        """INSERT INTO media_datas (userId, file_name, s3_url, file_extension, transcribe_status, duration, price, aws_price, file_size, createdAt, updatedAt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (user_id, filename, s3_full_url, json_media_detail["format"]["format_name"], '0', json_media_detail["format"]["duration"], str(calc_total_price(math.ceil(float(json_media_detail["format"]["duration"])))), str(calc_aws_price(math.ceil(float(json_media_detail["format"]["duration"])))), json_media_detail["format"]["size"], formatted_date, formatted_date),):
                        media_data = db_read(
                            "SELECT id, duration FROM media_datas where userId=%s and file_name=%s and s3_url like %s",
                            (user_id, filename, s3_full_url),)
                        if (media_data):
                            return jsonify({"jwt_token": refresh_token(), "msg": "uploaded file successfully", "index": index, "s3_url": s3_full_url, "file_name": filename, "mediaId": media_data[0]["id"], "duration": media_data[0]["duration"], "price": calc_total_price(math.ceil(float(json_media_detail["format"]["duration"]))),
                                            "success": "true"}), 201
                        else: return jsonify({"jwt_token": refresh_token(), "msg": "failed saving db", "success": "false"}), 201
                    else: return jsonify({"jwt_token": refresh_token(), "msg": "failed saving db", "success": "false"}), 201
                else: return jsonify({"jwt_token": refresh_token(), "msg": "unavailable file format", "success": "false"})
