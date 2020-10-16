from flask import Blueprint, request, Response, jsonify
from utils import *
from werkzeug.utils import secure_filename
import os
from app import app
from datetime import datetime
from settings import S3_MEDIA_BUCKET, APP_STATIC, S3_TRANSCRIBE_BUCKET
from werkzeug.datastructures import FileStorage

transcribe = Blueprint("transcribe", __name__)

UPLOAD_FOLDER = './static'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@transcribe.route("/upload", methods=["POST"])

def media_upload():

    # file = None

    # with open(os.path.join(APP_STATIC, 'test.txt')) as fp:
    #     file = FileStorage(fp)
    #     upload_file_to_s3(file, S3_MEDIA_BUCKET)

    # return request

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

                    db_write(
                        """INSERT INTO media_datas (userId, file_name, s3_url, file_extension, createdAt, updatedAt) VALUES (%s, %s, %s, %s, %s, %s)""",
                        (12, filename, 'test', 'mp3', formatted_date, formatted_date),
                    )

                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                    upload_file_to_s3(file, S3_MEDIA_BUCKET)

    return jsonify({"result": "success"}), 201

@transcribe.route("/transcribe", methods=["POST"])

def audio_transcribe():

    app.logger.debug("transcribe test")