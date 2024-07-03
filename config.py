import os


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    BASE_PATH = os.path.dirname(__file__)
    SECRET_KEY = os.getenv("SECRET_KEY")
    UPLOADED_PHOTOS_DEST = os.getenv("UPLOADED_PHOTOS_DEST")
    SERVER_URL = os.getenv("SERVER_URL")
    VIDEO_SERVER_URL = os.getenv("VIDEO_SERVER_URL")
    TEMP_UPLOADS_FILE = os.getenv("TEMP_UPLOADS_FILE")
    CONFIG_MODE = os.getenv("CONFIG_MODE")
    ADS_RECOGNITION_API_ROUTE = os.getenv("ADS_RECOGNITION_API_ROUTE")
    FACIAL_RECOGNITION_API_ROUTE = os.getenv("FACIAL_RECOGNITION_API_ROUTE")
    RECOGNITION_JOBS_API_ROUTE = os.getenv("RECOGNITION_JOBS_API_ROUTE")
    CHANNELS_API_ROUTE = os.getenv("CHANNELS_API_ROUTE")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DEVELOPMENT_DATABASE_URL")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL")


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("STAGING_DATABASE_URL")


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("PRODUCTION_DATABASE_URL")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
}
