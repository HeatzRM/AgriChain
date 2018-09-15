import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('heatz') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:myhome@localhost/theology_library'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
