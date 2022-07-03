import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # PER PAGE
    BOOK_DISPLAY_PER_PAGE = 10
    BOOK_TAG_PER_PAGE = 20
    COMMENT_NOTE_PER_PAGE = 5

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    WHOOSHEE_MIN_STRING_LEN = 1

    # SECRET KEY
    # os.urandom(24)会从0 - 9，a - z、A - Z中随机选中24个字符串用做秘钥。
    # SECRET_KEY = os.urandom(24)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A-VERY-LONG-SECRET-KEY'

    # RECAPTCHA PUBLIC KEY
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY') or 'A-VERY-LONG-SECRET-KEY'

    # RECAPTCHA PRIVATE KEY
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY') or 'A-VERY-LONG-SECRET-KEY'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'zhuojian.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask mail Config
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'MAIL_USERNAME'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'MAIL_PASSWORD'
