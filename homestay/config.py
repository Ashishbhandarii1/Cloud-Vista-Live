import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'artistrallyhomestay2024secretkey')
    _db_url = os.environ.get('FLASK_DATABASE_URL', 'sqlite:///homestay.db')
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
