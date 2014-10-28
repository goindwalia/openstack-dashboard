from flask import Blueprint

instances = Blueprint('instances', __name__)

from . import views
