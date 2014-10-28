from flask import render_template, redirect, url_for, session
from . import main
from ..models import Instances

@main.route('/')
def index():
    return render_template('index.html', instance=Instances())