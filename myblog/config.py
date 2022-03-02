import os

basedir = os.path.abspath(os.path.dirname(__file__))


POST_MAX_LEN = 1000000
BODY_MIN_LEN = 10
FEEDBACK_FORM_PREFILL_LINK = os.environ.get("FORM_URL")

_admins = os.environ.get("ADMINS")
if _admins:
    _admins = _admins.split(',')

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "abc"
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI") or "/"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = _admins
