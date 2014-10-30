from datetime import timedelta
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.urandom(32)
    
    #Clears the session after 30 seconds of inactivity
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=3000)

    # Set the following vars here (not recommended) or set it in your host as env variables (revommended)
    
    IDENTITY_URL = os.environ.get('IDENTITY_URL')
    ADMIN_IDENTITY_URL = os.environ.get('ADMIN_IDENTITY_URL')
    ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN')
    ADMIN_IDENTITY_URL_V3 = os.environ.get('ADMIN_IDENTITY_URL_V3')
    IMAGE_URL_V2 = os.environ.get('IMAGE_URL_V2')
    COMPUTE_URL_V2 = os.environ.get('COMPUTE_URL_V2')
    COMPUTE_URL_V2_1 = os.environ.get('COMPUTE_URL_V2_1')
    NETWORK_URL_V2 = os.environ.get('NETWORK_URL_V2')
    # ID for 'users' tenant
    DEFAULT_DOMAIN_ID = os.environ.get('DEFAULT_DOMAIN_ID')
    # ID for _member_ role
    DEFAULT_MEMBER_ROLE = os.environ.get('DEFAULT_MEMBER_ROLE')



    # Email id used to send emails for confirmation
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
