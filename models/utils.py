import os
from app import app, db
from hashlib import pbkdf2_hmac
import jwt
import MySQLdb
import boto3
from settings import JWT_SECRET_KEY, S3_KEY, S3_SECRET_ACCESS_KEY
import time

s3 = boto3.client(
   "s3",
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET_ACCESS_KEY
)

transcribe_client = boto3.client('transcribe', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET_ACCESS_KEY)

ALLOWED_EXTENSIONS = {'mp3', 'mp4', 'png', 'jpg', 'jpeg', 'gif'}

def validate_user(email, password):
    current_user = db_read("""SELECT * FROM users WHERE email = %s""", (email,))
    app.logger.debug(current_user)
    if len(current_user) == 1:
        saved_password_hash = current_user[0]["password_hash"]
        saved_password_salt = current_user[0]["password_salt"]
        password_hash = generate_hash(password, saved_password_salt)

        if password_hash == saved_password_hash:
            user_id = current_user[0]["id"]
            permission = current_user[0]["permission"]
            jwt_token = generate_jwt_token({"user_id": user_id, "permission": permission})
            return jwt_token
        else:
            return False
    else:
        return False

def generate_jwt_token(content):
    encoded_content = jwt.encode(content, JWT_SECRET_KEY, algorithm="HS256")
    token = str(encoded_content).split("'")[1]
    return token

def generate_salt():
    salt = os.urandom(16)
    return salt.hex()

def generate_hash(plain_password, password_salt):
    password_hash = pbkdf2_hmac(
        "sha256",
        b"%b" % bytes(plain_password, "utf-8"),
        b"%b" % bytes(password_salt, "utf-8"),
        10000,
    )
    return password_hash.hex()

def validate_user_input(input_type, **kwargs):
    if input_type == "authentication":
        if len(kwargs["email"]) <= 255 and len(kwargs["password"]) <= 255:
            return True
        else:
            return False

def db_write(query, params):
    cursor = db.connection.cursor()
    try:
        cursor.execute(query, params)
        db.connection.commit()
        cursor.close()
        return True
    except MySQLdb._exceptions.IntegrityError:
        cursor.close()
        return False

def db_read(query, params=None):
    cursor = db.connection.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    entries = cursor.fetchall()
    cursor.close()
    content = []
    for entry in entries:
        content.append(entry)
    return content

def upload_file_to_s3(file, bucket_name, s3_SUB_FOLDER, S3_LOCATION, userId, acl="public-read"):
    ts = time.time()
    full_filename = s3_SUB_FOLDER + '/' + str(userId) + '_' + str(ts) + '_' + file.filename
    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            full_filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        print("Something Happened: ", e)
        return e
    return "{}{}".format(S3_LOCATION, full_filename)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def transcribe_file(job_name, file_uri):
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': file_uri},
        MediaFormat='mp3',
        LanguageCode='en-US'
    )

    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        job_status = job['TranscriptionJob']['TranscriptionJobStatus']
        if job_status in ['COMPLETED', 'FAILED']:
            print(f"Job {job_name} is {job_status}.")
            if job_status == 'COMPLETED':
                print(
                    f"Download the transcript from\n"
                    f"\t{job['TranscriptionJob']['Transcript']['TranscriptFileUri']}.")
            break
        else:
            print(f"Waiting for {job_name}. Current status is {job_status}.")
        time.sleep(10)


# def main():
#     file_uri = 's3://test-transcribe/answer2.wav'
#     transcribe_file('Example-job', file_uri, transcribe_client)


if __name__ == '__main__':
    main()