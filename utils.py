import os
from app import app, db
from hashlib import pbkdf2_hmac
import jwt
import MySQLdb
import boto3
from boto3.s3.transfer import S3Transfer
from settings import JWT_SECRET_KEY, S3_KEY, S3_SECRET_ACCESS_KEY

s3 = boto3.client(
   "s3",
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET_ACCESS_KEY
)

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
            jwt_token = generate_jwt_token({"id": user_id})
            return jwt_token
            # return user_id
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

    app.logger.debug(query)

    app.logger.debug(params)

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

def upload_file_to_s3(file, bucket_name, acl="public-read"):

    transfer = S3Transfer(s3)

    path_on_s3 = "audio-datas/test.txt"

    transfer.upload_file('/home/ubuntu/Documents/web_projects/transcribe-backend/static/test.txt',
                         bucket_name, path_on_s3, extra_args={'ACL': 'public-read'})

def allowed_file(filename):

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS