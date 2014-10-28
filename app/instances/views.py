from flask import render_template, redirect, \
    url_for, abort, session, flash, request, current_app
from flask.ext.login import login_user, current_user, \
    logout_user, login_required
from . import instances
from .forms import CreateServerForm
from ..models import Instances, Images, User, Flavors
from .. import db
import requests
import json

frmt= "%b %d, %Y at %H:%M"
instance = Instances()

@instances.route('/')
@login_required
def instanceslist():
    instance.getInstances()
    return render_template('instances/index.html', instances=instance.serverslist, instance = Instances())

@instances.route('/<serverid>')
@login_required
def instancedetails(serverid):
    instancedetails = instance.getInstanceDetails(serverid)
    createdate = instance.date_time(instancedetails.get('created')).strftime(frmt)
    updatedate = instance.date_time(instancedetails.get('updated')).strftime(frmt)
    return render_template('instances/details.html',flavor=Flavors(), user = User(), image=Images(), instance=instancedetails,updatedate=updatedate,createdate=createdate)

@instances.route('/start/<serverid>')
@login_required
def start(serverid):
    if instance.startInstance(serverid):
        msg = "%s start inititated..." % (instance.getInstanceDetails(serverid).get('name'))
        flash(msg)
        return redirect(url_for('instances.instanceslist')) 
    msg = "%s unable to start..." % (instance.getInstanceDetails(serverid).get('name'))
    flash(msg)

@instances.route('/stop/<serverid>')
@login_required
def stop(serverid):
    if instance.stopInstance(serverid):
        msg = "%s stop inititated..." % (instance.getInstanceDetails(serverid).get('name'))
        flash(msg)
        return redirect(url_for('instances.instanceslist')) 
    msg = "%s unable to stop..." % (instance.getInstanceDetails(serverid).get('name'))
    flash(msg)
    return redirect(url_for('instances.instanceslist')) 


@instances.route('/delete/<serverid>')
@login_required
def delete(serverid):
    if instance.deleteInstance(serverid):
        flash("Instance deleted.")
        return redirect(url_for('instances.instanceslist')) 
    msg = "%s unable to delete..." % (instance.getInstanceDetails(serverid).get('name'))
    flash(msg)
    return redirect(url_for('instances.instanceslist')) 

@instances.route('/reboot/<serverid>')
@login_required
def reboot(serverid):
    if instance.rebootInstance(serverid):
        msg = "%s reboot inititated..." % (instance.getInstanceDetails(serverid).get('name'))
        flash(msg)
        return redirect(url_for('instances.instanceslist')) 
    msg = "%s unable to reboot..." % (instance.getInstanceDetails(serverid).get('name'))
    flash(msg)
    return redirect(url_for('instances.instanceslist'))

@instances.route('/log/<serverid>')
@login_required
def log(serverid):
    return render_template('instances/log.html', log=instance.logInstance(serverid, 50))


@instances.route('/create', methods=['GET', 'POST'])
@login_required
def create():


    form = CreateServerForm()
    image = Images()
    image.getImages()
    querystring = request.args


    
    form.imageselected.choices = []
    for img in image.images_list:
        form.imageselected.choices.append((img.get('id'),img.get('name')))
    form.flavorselected.choices = []
    for flavor in instance.getFlavors():
        form.flavorselected.choices.append((flavor.get('id'),flavor.get('name')))
    form.networkselected.choices = []
    for network in instance.getNetworks():
        form.networkselected.choices.append((network.get('id'),network.get('name')))

    if querystring!={}:
        form.imageselected.data = querystring.get('image')

    if form.validate_on_submit():
        if instance.createInstance(form.servername.data,form.imageselected.data,form.flavorselected.data,form.networkselected.data):
            flash("True")
        else:
            flash("False")
    return render_template('instances/create.html', form=form, method='get', qstring=querystring)





