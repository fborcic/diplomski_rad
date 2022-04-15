import os

basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    WTF_CSRF_ENABLED = True
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test_database.db')
    SQLALCHEMY_DATABASE_URI= 'mysql+pymysql://preapps:preapplicationformbananko@localhost:3306/preapplications'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    REVERSE_PROXY_PATH = "/pre-applications"
    CV_UPLOAD_FOLDER = "/cv_uploads"
