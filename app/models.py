# -*- coding: utf-8 -*-
from flask import current_app, request, abort, session
from flask.ext.login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import requests
import json
import os
from datetime import datetime
from . import db,login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(64), primary_key=True)
    username = db.Column(db.String(32), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    confirmed = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)

    def authenticateUser(self,password):
        url = current_app.config['IDENTITY_URL'] + '/tokens'
        payload = {
                    "auth": {
                        "tenantName": self.username + "_project",
                        "passwordCredentials": {
                            "username": self.username,
                            "password": password
                        }                        
                    }
                }
        headers = {'Content-Type' : 'application/json', 'Accept' : 'application/json'}
        data = json.dumps(payload)
        r = requests.post(url, data=data, headers=headers)
        if r.status_code == 203 or r.status_code == 200:
            response_content = json.loads(r.content)
            #Saves the token generated for the user in session
            session['user_token'] = response_content.get('access').get('token').get('id')
            #Saves the login time
            session['login_time'] = datetime.utcnow()
            session['tenantid'] = self.getTenantId()
            return True
        else:
            session.clear()
            return False

    def getTenantId(self):
        url = current_app.config['ADMIN_IDENTITY_URL_V3'] + '/users/%s/projects' % (self.id)
        headers = {'X-Auth-Token': current_app.config['ADMIN_TOKEN'], 'Accept': 'application/json'}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            response_content = json.loads(r.content)
            return response_content['projects'][0]['id']
        return None

    def getUserDetails(self, userid):
        url = current_app.config['ADMIN_IDENTITY_URL_V3'] + '/users/' + userid
        headers = {'X-Auth-Token': current_app.config['ADMIN_TOKEN'], 'Accept': 'application/json'}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            response_content = json.loads(r.content)
            return response_content.get('user')
        return None

    def createProject(self):
        url = current_app.config['ADMIN_IDENTITY_URL_V3'] + '/projects'
        payload = {
                    "project": {
                        "domain_id": current_app.config['DEFAULT_DOMAIN_ID'],
                        "description": "Project for user " + self.username, 
                        "name": self.username + '_project',
                        "enabled": True,
                    }
                }
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                    'X-Auth-Token': current_app.config['ADMIN_TOKEN']}

        data = json.dumps(payload)
        r = requests.post(url, headers=headers, data=data)
        if r.status_code == 201:
            session['current_project_id'] = json.loads(r.content).get('project').get('id')
            return True
        return False
               
    def createUser(self, password):
        url = current_app.config['ADMIN_IDENTITY_URL_V3'] + '/users'
        payload = {
                    "user": {
                        "domain_id": current_app.config['DEFAULT_DOMAIN_ID'],
                        "email": self.email,
                        "name": self.username,
                        "enabled": True,
                        "password": password
                    }
        }
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 
                'X-Auth-Token': current_app.config['ADMIN_TOKEN']}
        data = json.dumps(payload)
        r = requests.post(url, data=data, headers=headers)
        if r.status_code == 201:
            response_content = json.loads(r.content)
            self.id = response_content.get('user').get('id')
            return True
        return False

    def addMemberRole(self):
        url = current_app.config['ADMIN_IDENTITY_URL_V3'] + '/projects/' + \
            session.get('current_project_id') + '/users/' + self.id + \
            '/roles/' + current_app.config['DEFAULT_MEMBER_ROLE']

        headers = {'X-Auth-Token': current_app.config['ADMIN_TOKEN']}
        r = requests.put(url, headers=headers)        
        if r.status_code == 204:
            db.session.add(self)
            db.session.commit()
            return True
        return False

    def invalidateToken(self):
        url = current_app.config['IDENTITY_URL'] + '/tokens/' + session.get('user_token')
        headers = {'X-Auth-Token': current_app.config['ADMIN_TOKEN']}
        r = requests.delete(url,headers=headers)
        if r.status_code == 204:
            return True
        return False

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()



class Images(object):
    images_list = None
    def getImages(self):
        url = current_app.config['IMAGE_URL_V2'] + '/images'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': session.get('user_token')}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            response_content = json.loads(r.content)
            self.images_list = response_content.get('images')
            return True
        return False

    def getImageDetails(self, id):
        url = current_app.config['IMAGE_URL_V2'] + '/images/%s' % (id)
        headers = {'X-Auth-Token': session.get('user_token'), 'Accept': 'application/json'}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            response_content = json.loads(r.content)
            return response_content
        return None

class Flavors(object):
    def getFlavors(self):
        url = current_app.config['COMPUTE_URL_V2'] + '/%s/flavors' % (session.get('tenantid'))
        headers = {'X-Auth-Token': session.get('user_token'), 'Accept': 'application/json'}
        r = requests.get(url, headers=headers)
        if r.status_code == 200 or 203:
            response_content = json.loads(r.content).get('flavors')
            return response_content
        return None

    def getFlavorDetails(self,id):
        url = current_app.config['COMPUTE_URL_V2'] + '/%s/flavors/%s' % (session.get('tenantid'),id)
        headers = {'X-Auth-Token': session.get('user_token'), 'Accept': 'application/json'}
        r = requests.get(url, headers=headers)
        if r.status_code == 200 or 203:
            response_content = json.loads(r.content).get('flavor')
            return response_content
        return None

class Instances (object):
    serverslist = None
    serverdetails = None
    serverid = None
    code = None

    def date_time(self,datentime):
        Y = int(datentime[0:4])
        M = int(datentime[5:7])
        D = int(datentime[8:10])
        h = int(datentime[11:13])
        m = int(datentime[14:16])
        s = int(datentime[17:19])
        return datetime(Y,M,D,h,m,s)


    def createInstance(self,name,imageid,flavorid,networkid):
        url = current_app.config['COMPUTE_URL_V2'] + '/%s/servers' % (session.get('tenantid'))
        payload = {
                        "server": {
                                "name": name,
                                "imageRef": imageid,
                                "flavorRef": flavorid,
                                "networks": [
                                {
                                    "uuid": networkid
                                } ]
                        }
                    }
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json','X-Auth-Token': session.get('user_token')}
        data = json.dumps(payload)
        r = requests.post(url, data=data, headers=headers)
        if r.status_code == 202:
            return True
        return r.status_code

    def getNetworks(self):
        url = current_app.config['NETWORK_URL_V2'] + '/networks'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': session.get('user_token')}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            response_content = json.loads(r.content)
            return response_content.get('networks')
        return False

    def getInstances(self):
        url = current_app.config['COMPUTE_URL_V2'] + '/%s/servers/detail' % (session.get('tenantid'))
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': session.get('user_token')}
        r = requests.get(url, headers=headers)
        if r.status_code == 200 or 203:
            response_content = json.loads(r.content)
            self.serverslist = response_content.get('servers')
            return True
        return False


    def getInstanceDetails(self, serverid):
        url = current_app.config['COMPUTE_URL_V2'] + '/%s/servers/%s' % (session.get('tenantid'), serverid)
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': session.get('user_token')}
        r = requests.get(url, headers=headers)
        if r.status_code == 200 or 203:
            response_content = json.loads(r.content)
            return response_content.get('server')
        return False

    def getLimits(self):
        url = current_app.config['COMPUTE_URL_V2'] + '/%s/limits' % (session.get('tenantid'))
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': session.get('user_token')}
        r = requests.get(url, headers=headers)
        if r.status_code == 200 or 203:
            response_content = json.loads(r.content)
            return response_content.get('limits')
        return False

    def getFlavors(self):
        url = current_app.config['COMPUTE_URL_V2'] + '/%s/flavors' % (session.get('tenantid'))
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': session.get('user_token')}
        r = requests.get(url, headers=headers)
        if r.status_code == 200 or 203:
            response_content = json.loads(r.content)
            return response_content.get('flavors')
        return False


    def rebootInstance(self, serverid):
        url = current_app.config['COMPUTE_URL_V2'] + '/%s/servers/%s/action' % (session.get('tenantid'), serverid)
        payload = {"reboot":{"type": "SOFT"}}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json','X-Auth-Token': session.get('user_token')}
        data = json.dumps(payload)
        r = requests.post(url, data=data, headers=headers)
        if r.status_code == 202:
            return True
        return False

    def startInstance(self, serverid):
        url = current_app.config['COMPUTE_URL_V2'] + '/%s/servers/%s/action' % (session.get('tenantid'), serverid)
        payload = {"os-start": "null"}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json','X-Auth-Token': session.get('user_token')}
        data = json.dumps(payload)
        r = requests.post(url, data=data, headers=headers)
        if r.status_code == 202:
            return True
        return False

    def stopInstance(self, serverid):
        url = current_app.config['COMPUTE_URL_V2'] + '/%s/servers/%s/action' % (session.get('tenantid'), serverid)
        payload = {"os-stop": "null"}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json','X-Auth-Token': session.get('user_token')}
        data = json.dumps(payload)
        r = requests.post(url, data=data, headers=headers)
        if r.status_code == 202:
            return True
        return False

    def deleteInstance(self, serverid):
        url = current_app.config['COMPUTE_URL_V2'] + '/%s/servers/%s' % (session.get('tenantid'), serverid)
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json','X-Auth-Token': session.get('user_token')}
        r = requests.delete(url, headers= headers)
        if r.status_code == 204:
            return True
        return False

    def logInstance(self, serverid, length):
        url = current_app.config['COMPUTE_URL_V2'] + '/%s/servers/%s/action' % (session.get('tenantid'), serverid)
        payload = {"os-getConsoleOutput": {"length": int(length)}}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json','X-Auth-Token': session.get('user_token')}
        data = json.dumps(payload)
        r = requests.post(url, data=data, headers=headers)
        if r.status_code == 200:
            response_content = json.loads(r.content)
            return response_content.get('output')
        return False

    def consoleInstance(self, serverid):
        url = current_app.config['COMPUTE_URL_V2'] + '/%s/servers/%s/action' % (session.get('tenantid'), serverid)
        payload = {"os-getVNCConsole": {"type": "novnc"}}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json','X-Auth-Token': session.get('user_token')}
        data = json.dumps(payload)
        r = requests.post(url, data=data, headers=headers)
        if r.status_code == 200:
            response_content = json.loads(r.content)
            return response_content.get('console').get('url')
        return False



