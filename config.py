class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class Development(Config):
    DEBUG = True
    PORT = 4555
    SQLALCHEMY_DATABASE_URI = 'sqlite:///storage.db'
    URL_LAMBDA_ML = 'https://5md75t1y4a.execute-api.us-east-1.amazonaws.com/PROD'
    S3_USER_DATA_BUCKET_INPUT = 'user-data-upload'
    S3_USER_DATA_BUCKET_OUTPUT = 'user-data-upload-output'

class Testing(Config):
    TESTING = True

class Production(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///storage.db'
    URL_LAMBDA_ML = 'https://5md75t1y4a.execute-api.us-east-1.amazonaws.com/PROD'
    S3_USER_DATA_BUCKET_INPUT = 'user-data-upload'
    S3_USER_DATA_BUCKET_OUTPUT = 'user-data-upload-output'