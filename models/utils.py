import os
from app import app, db
from hashlib import pbkdf2_hmac
import jwt
import MySQLdb
import boto3
from settings import JWT_SECRET_KEY, S3_KEY, S3_SECRET_ACCESS_KEY, JWT_EXPIRE_MINUTES
import time
import datetime
from flask_jwt_extended import create_access_token, get_jwt_identity

s3 = boto3.client(
   "s3",
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET_ACCESS_KEY
)
transcribe_client = boto3.client('transcribe', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET_ACCESS_KEY)
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'aac', 'mp4', 'avi', 'mpeg'}

def validate_user(email, password):
    current_user = db_read("""SELECT * FROM users WHERE email = %s""", (email,))
    if len(current_user) == 1:
        saved_password_hash = current_user[0]["password_hash"]
        saved_password_salt = current_user[0]["password_salt"]
        password_hash = generate_hash(password, saved_password_salt)

        if password_hash == saved_password_hash:
            user_id = current_user[0]["id"]
            permission = current_user[0]["permission"]
            user_email = current_user[0]["email"]
            expires = datetime.timedelta(minutes=int(JWT_EXPIRE_MINUTES))
            jwt_token = create_access_token({"user_id": user_id, "permission": permission, "email": user_email}, expires_delta=expires)
            return jwt_token
        else:
            return False
    else:
        return False

def refresh_token():
    current_user = get_jwt_identity()
    expires = datetime.timedelta(minutes=60)
    jwt_token = create_access_token(identity=current_user, expires_delta=expires)
    return jwt_token

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
                return job['TranscriptionJob']['Transcript']['TranscriptFileUri']
            break
        else:
            print(f"Waiting for {job_name}. Current status is {job_status}.")
        time.sleep(10)

def calc_total_price(duration):
    price = db_read("""SELECT * FROM transcribe_price""",
                    (), )
    price_per_minute = price[0]["price_per_minute"]
    price_per_half_minute = price[0]["price_per_half_minute"]
    minimum_price = price[0]["minimum_price"]
    div_mod = divmod(int(duration), 60)
    total_minute = div_mod[0]
    remain_seconds = div_mod[1]
    if (remain_seconds > 30):
        calc_remain_seconds = 0
        total_minute = total_minute + 1
    else:
        calc_remain_seconds = 1
    total_price = price_per_minute * total_minute + price_per_half_minute * calc_remain_seconds
    if(total_price < minimum_price):
        return minimum_price
    else:
        return round(total_price, 2)

def distinguish_audio_video(param_extension):
    param_extension_array = param_extension.split(",")
    abailable_audio_extension = app.config["AUDIO_EXTENSION"]
    abailable_video_extension = app.config["VIDEO_EXTENSION"]
    audio_extension_array = abailable_audio_extension.split(",")
    video_extension_array = abailable_video_extension.split(",")
    count = 0
    for param_extention in param_extension_array:
        for audio_extension in audio_extension_array:
            if audio_extension.strip() == param_extention.strip():
                count = count + 1
    if count !=0:
        return "audio"

    for param_extention in param_extension_array:
        for video_extension in video_extension_array:
            if video_extension.strip() == param_extention.strip():
                count = count + 1
    if count !=0:
        return "video"

    return "wrong"

if __name__ == '__main__':
    main()