import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_DB = os.environ.get('POSTGRES_DB')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
SECRET = os.environ.get('SECRET')
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_FROM = os.environ.get('MAIL_FROM')
MAIL_PORT = os.environ.get('MAIL_PORT')
MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
RESET_PASSWORD_REDIRECT_URL = os.environ.get('RESET_PASSWORD_REDIRECT_URL')
RESET_PASSWORD_EXPIRY_MINUTES = os.environ.get('RESET_PASSWORD_EXPIRY_MINUTES')
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET_KEY = os.environ.get('GOOGLE_CLIENT_SECRET_KEY')
GOOGLE_REDIRECT_URL = os.environ.get('GOOGLE_REDIRECT_URL')
