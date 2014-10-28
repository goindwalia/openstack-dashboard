from flask import render_template, redirect, \
    url_for, abort, session, flash, request, current_app
from flask.ext.login import login_user, current_user, \
    logout_user, login_required
from . import images
from ..models import Images
from .. import db
import requests
import json

@images.route('/')
@login_required
def imageslist():
    image = Images()
    image.getImages()
    return render_template('images/index.html', images=image.images_list)

@images.route('/add')
def add():
    pass
