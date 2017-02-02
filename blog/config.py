import os
class DevelopmentConfig(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://Jon:onegod@localhost:5432/blogful"
    DEBUG = True