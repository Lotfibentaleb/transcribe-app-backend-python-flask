from dotenv import load_dotenv
import os

load_dotenv()
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_HOST = os.getenv("MYSQL_HOST")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

S3_KEY = os.getenv("S3_KEY")
S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY")

S3_MEDIA_BUCKET = os.getenv("S3_MEDIA_BUCKET")
S3_TRANSCRIBE_BUCKET = os.getenv("S3_TRANSCRIBE_BUCKET")

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')

UPLOAD_FOLDER = "./static"

AUDIO_EXTENSION = os.getenv("AUDIO_EXTENSION")
VIDEO_EXTENSION = os.getenv("VIDEO_EXTENSION")