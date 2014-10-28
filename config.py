from datetime import timedelta
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.urandom(32)
    
    #Clears the session after 30 seconds of inactivity
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=3000)

    IDENTITY_URL = 'http://112.196.38.243:5000/v2.0'
    ADMIN_IDENTITY_URL = 'http://112.196.38.243:35357/v2.0'
    ADMIN_TOKEN = 'openstack'
    ADMIN_IDENTITY_URL_V3 = 'http://112.196.38.243:35357/v3'
    IMAGE_URL_V2 = 'http://112.196.38.243:9292/v2'
    COMPUTE_URL_V2 = 'http://112.196.38.243:8774/v2'
    COMPUTE_URL_V2_1 = 'http://112.196.38.243:8774/v2.1'
    NETWORK_URL_V2 = 'http://112.196.38.243:9696/v2.0'
    #ID for 'users' tenant
    DEFAULT_DOMAIN_ID = "default"
    #ID for _member_ role
    DEFAULT_MEMBER_ROLE = "9fe2ff9ee4384b1894a90878d3e92bab"

    #Email id used to send emails for confirmation
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'karan.dewgun@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'Pass$123'
    MAIL_SUBJECT_PREFIX = '[OpenStack]'
    MAIL_SENDER = 'OpenStack Admin <test@example.com>'
    ADMIN = os.environ.get('OPENSTACK_ADMIN') or 'karan.dewgun@gmail.com'
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

config = {
    'development': DevelopmentConfig,

    'default': DevelopmentConfig
}

class ProductionConfig(Config):
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)
