from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from config import config
from flask_wtf.csrf import CsrfProtect

bootstrap = Bootstrap()
mail = Mail()
db = SQLAlchemy()
csrf = CsrfProtect()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    csrf.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # from .swift import swift as swift_blueprint
    # app.register_blueprint(swift_blueprint, url_prefix='/swift')

    from .instances import instances as instances_blueprint
    app.register_blueprint(instances_blueprint, url_prefix='/instances')

    from .images import images as images_blueprint
    app.register_blueprint(images_blueprint, url_prefix='/images')

    return app