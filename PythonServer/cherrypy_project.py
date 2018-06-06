#!/usr/bin/python
""" cherrypy_project.py

    COMPSYS302 - Software Design
    Author: Peter Joe (pjoe652@auckland.ac.nz)
    Last Edited: 7/06/2018

    This program uses the CherryPy web server (from www.cherrypy.org).
"""
# Requires:  CherryPy 3.2.2  (www.cherrypy.org)
#            Python  (We use 2.7)

import databaseControl
import socket
import cherrypy
from cherrypy.process.plugins import BackgroundTask
import hashlib
import urllib
import urllib2
import sqlite3
import json
import time
import os
import mimetypes
import time
import threading
import thread
import imghdr
import base64
import logging
import smtplib
import random
import string

# The address we listen for connections on
listen_ip = "0.0.0.0"
listen_port = 10002
ipv4 = socket.gethostbyname(socket.gethostname())

global logged_in
logged_in = False

class MainApp(object): 

    #CherryPy Configuration
    path = os.path.abspath(os.path.dirname(__file__))
    _cp_config = {'tools.encode.on': True, 
                  'tools.encode.encoding': 'utf-8',
                  'tools.sessions.on' : 'True',
                 }
    
    
    def log_error(self, error):
        ''' Logs errors into errorlog.txt '''
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        with open('errorlog.txt', 'a+') as log:
            log.write(timestamp + ":" + error + "\n")

    # If they try somewhere we don't know, catch it here and send them to the right place.
    @cherrypy.expose
    def default(self, *args, **kwargs): 
        '''The default page, given when we don't recognise where the request is for.'''
        Page = open("404.html")
        cherrypy.response.status = 404
        return Page

    # PAGES (which return HTML that can be viewed in browser)   
    @cherrypy.expose
    def index(self):
        ''' Returns main page, or if not logged in, the login page'''
        Page = ""
        try:
            Page = ""
            #Create profile box
            profile = ""
            profile_user = databaseControl.getProfile(cherrypy.session['username'])
            if (profile_user[6] == ""):
                profile_pic = "/img/unknown.png"
            else:
                profile_pic = profile_user[6]
                
            Page = open("index.html").read().format(profile_pic, profile_user[0], profile_user[2], profile_user[3], profile_user[4], profile_user[5])

        except KeyError: #There is no username
            self.log_error("KeyError within index")
            raise cherrypy.HTTPRedirect('/login')
        return Page

    
    @cherrypy.expose
    def ping(self, sender):
        '''Ping to show that server can be reached'''
        return "0"


    
    #---------------------Auto Updater Methods--------------------------
    
    @cherrypy.tools.json_out()
    @cherrypy.expose
    def storeUsers(self):
        ''' Updates online users via outputting details as JSON'''
        username = cherrypy.session['username']
        password = cherrypy.session['password']
        encrypt = hashlib.sha256(str(password) + str(username)) 
        encrypt = encrypt.hexdigest()
        databaseControl.updateOnlineUsers(username, encrypt)
        online_users = databaseControl.getOnlineUsers()
        offline_users = databaseControl.getOfflineUsers()
        
        online = ""
        online += "<form action='/getProfileInfo' method='post'>" 
        for user in online_users:
            online += "<div class='tabOnline'>"
            online += "<button class='Onlinebutton' name='destination' value='{}'> {} </button>".format(user, user)
            online += '<span class="Onlinedot"></span></div>'
        for user in offline_users:
            online += "<div class='tabOnline'>"
            online += "<button class='Onlinebutton' name='destination' value='{}'> {} </button>".format(user, user)
            online += '</div>'
        online += "</form>"

        online_dict = {"data" : online}
        online_dict = json.dumps(online_dict)
        
        return online_dict

    
    @cherrypy.tools.json_out()
    @cherrypy.expose
    def updateStatus(self, destination):
        ''' Updates user chat status via outputting details as JSON'''
        if (databaseControl.checkUserExists(destination) == 1):
            online_bar = "<center>"
            online_bar += '<div class="online_tag">{} is online <span class="tag_online_dot"></span></div>'.format(destination)
            online_bar += '</center>'
        else:
            online_bar = "<center>"
            online_bar += '<div class="online_tag">{} is offline <span class="tag_offline_dot"></span></div>'.format(destination)
            online_bar += '</center>'

        status_dict = {"data" : online_bar}
        status_dict = json.dumps(status_dict)

        return status_dict

    
    @cherrypy.tools.json_out()
    @cherrypy.expose
    def updateChat(self, destination):
        ''' Updates chat via outputting details as JSON'''
        sender = cherrypy.session['username']
        message_log = databaseControl.getMessage(sender, destination)
        sender_profile = databaseControl.getProfile(sender)
        destination_profile = databaseControl.getProfile(destination)

        sender_picture = sender_profile[6]
        destination_picture = destination_profile[6]

        message = ""

        #Returns HTML depending on the chat information (i.e. sender, file or message, content type, etc)
                                    
        for x in range(0, len(message_log)):
                    if (sender == message_log[x]['sender']):
                        if (message_log[x]['message'] != ""):
                                    stamp = message_log[x]['sender'] + " " + message_log[x]['timestamp']
                                    message += '<div class="chat self"><div class="user-photo"><img src="{}"></div>'.format(sender_picture)
                                    message += '<p class="chat-message"> {} </p>'.format(message_log[x]['message'])
                                    message += '<p class="time-log"> {} </p></div>'.format(stamp)
                        else:
                                    stamp = message_log[x]['sender'] + " " + message_log[x]['timestamp']
                                    local_path = "files/" + cherrypy.session['username'] + message_log[x]['filename']
                                    directory = "/img/" + cherrypy.session['username'] + message_log[x]['filename']
                                    filedata = base64.b64decode(message_log[x]['file'])
                                    with open(local_path, 'wb') as f:
                                        f.write(filedata)
                                    if ((message_log[x]['content_type'].split("/"))[0] == "image"):
                                        message += '<div class="chat self"><div class="user-photo"><img src="{}"></div>'.format(sender_picture)
                                        message += '<img class="chat-message" src="{}">'.format(directory)
                                        message += '<p class="time-log"> {} </p></div>'.format(stamp)
                                    elif ((message_log[x]['content_type'].split("/"))[0] == "audio"):
                                        message += '<div class="chat self"><div class="user-photo"><img src="{}"></div>'.format(sender_picture)
                                        message += '<div class="chat-message"><audio controls><source src="{}" type="{}">'.format(directory, message_log[x]['content_type'])
                                        message += '</audio></div><p class="time-log"> {} </p></div>'.format(stamp)
                                    elif ((message_log[x]['content_type'].split("/"))[0] == "video"):
                                        message += '<div class="chat self"><div class="user-photo"><img src="{}"></div>'.format(sender_picture)
                                        message += '<div class="chat-message"><video width="340px" controls><source src="{}" type="{}">'.format(directory, message_log[x]['content_type'])
                                        message += '</video></div><p class="time-log"> {} </p></div>'.format(stamp)
                                    else:
                                        message += '<div class="chat self"><div class="user-photo"><img src="{}"></div>'.format(sender_picture)
                                        message += '<div class="chat-message"><a href="{}" download>{}</a>'.format(directory, message_log[x]['filename'])
                                        message += '</div><p class="time-log"> {} </p></div>'.format(stamp)
                    else:
                        if (message_log[x]['message'] != ""):
                                    stamp = message_log[x]['sender'] + " " + message_log[x]['timestamp']
                                    message += '<div class="chat friend"><div class="user-photo"><img src="{}"></div>'.format(destination_picture)
                                    message += '<p class="chat-message"> {} </p>'.format(message_log[x]['message'])
                                    message += '<p class="time-log"> {} </p></div>'.format(stamp)
                        else:
                                    stamp = message_log[x]['sender'] + " " + message_log[x]['timestamp']
                                    local_path = "files/" + cherrypy.session['username'] + message_log[x]['filename']
                                    directory = "/img/" + cherrypy.session['username'] + message_log[x]['filename']
                                    filedata = base64.b64decode(message_log[x]['file'])
                                    with open(local_path, 'wb') as f:
                                        f.write(filedata)
                                    if ((message_log[x]['content_type'].split("/"))[0] == "image"):
                                        message += '<div class="chat friend"><div class="user-photo"><img src="{}"></div>'.format(destination_picture)
                                        message += '<img class="chat-message" src="{}">'.format(directory)
                                        message += '<p class="time-log"> {} </p></div>'.format(stamp)
                                    elif ((message_log[x]['content_type'].split("/"))[0] == "audio"):
                                        message += '<div class="chat friend"><div class="user-photo"><img src="{}"></div>'.format(destination_picture)
                                        message += '<div class="chat-message"><audio controls><source src="{}" type="{}">'.format(directory, message_log[x]['content_type'])
                                        message += '</audio></div><p class="time-log"> {} </p></div>'.format(stamp)
                                    elif ((message_log[x]['content_type'].split("/"))[0] == "video"):
                                        message += '<div class="chat friend"><div class="user-photo"><img src="{}"></div>'.format(destination_picture)
                                        message += '<div class="chat-message"><video width="340px" controls>'
                                        message += '<source src="{}" type="{}">'.format(directory, message_log[x]['content_type'])
                                        message += '</video></div><p class="time-log"> {} </p></div>'.format(stamp)
                                    else:
                                        message += '<div class="chat friend"><div class="user-photo"><img src="{}"></div>'.format(destination_picture)
                                        message += '<div class="chat-message"><a href="{}" download>{}</a>'.format(directory, message_log[x]['filename'])
                                        message += '</div><p class="time-log"> {} </p></div>'.format(stamp)
                                                    

        message_dict = {"data" : message}
        message_dict = json.dumps(message_dict)
        return message_dict

    #---------------------Profile Methods--------------------------

    
    @cherrypy.expose
    def profile(self, destination):
        ''' Displays destination's profile page'''
        try:
            username = cherrypy.session['username']
            profile_user = databaseControl.getProfile(destination)
            if (profile_user[6] == ""):
                profile_pic = "/img/unknown.png"
            else:
                profile_pic = profile_user[6]
            Page = open("Profile.html").read().format(profile_pic,profile_user[0], profile_user[2], profile_user[3], profile_user[4],
                                                      profile_user[5], destination, destination)
            return Page
        except KeyError:
            self.log_error("KeyError within profile")
            raise cherrypy.HTTPRedirect('/')
        except:
            self.log_error("Error within profile")
            raise cherrypy.HTTPRedirect('/')

    
    @cherrypy.expose
    def getProfileInfo(self, destination):
        '''Gets destination profile details'''
        try:
            databaseControl.updateUserProfile(destination, cherrypy.session['username'])
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except urllib2.URLError, e:
            self.log_error("URLError within getProfileInfo")
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except Exception as e:
            print e
            #self.log_error(e + "within prepMessages")
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        

    
    @cherrypy.expose
    def editProfilePage(self):
        '''Loads edit profile page'''
        try:
            profile_user = databaseControl.getProfile(cherrypy.session['username'])
            profile_details = [profile_user[0], profile_user[2], profile_user[3], profile_user[4], profile_user[5], profile_user[6]]
            #If no known profile picture
            if (profile_user[6] == ""):
                profile_pic = "/img/unknown.png"
            else:
                profile_pic = profile_user[6]
            Page = open("editProfile.html").read().format(profile_pic,profile_user[0], profile_user[2], profile_user[3], profile_user[4], profile_user[5])
            return Page
        except KeyError:
            self.log_error("Error within editProfilePage")
            raise cherrypy.HTTPRedirect('/')
        except:
            self.log_error("Error within editProfilePage")
            raise cherrypy.HTTPRedirect('/')
        

    
    @cherrypy.expose
    def editProfileDetails(self, name=None, position=None, description=None, location=None):
        '''Saves new profile details on database'''
        try:
            profile_user = databaseControl.getProfile(cherrypy.session['username'])
            last_updated = time.time()
            name = name.replace("<", "_")
            position = position.replace("<", "_")
            description = description.replace("<", "_")
            location = location.replace("<", "_")
            #cwd = os.getcwd()
            databaseControl.updateProfileDetails(cherrypy.session['username'], last_updated, name, position, description, location)
            raise cherrypy.HTTPRedirect('/')
        except KeyError:
            self.log_error("KeyError within editProfileDetails")
            raise cherrypy.HTTPRedirect('/')
        except:
            self.log_error("Error within editProfileDetails")
            raise cherrypy.HTTPRedirect('/')

    
    @cherrypy.expose
    def editProfilePicture(self, picture=None):
        '''Saves static image locally and saves path onto database'''
        try:
            username = cherrypy.session['username']
            local_path = "files/" + cherrypy.session['username'] + ".jpg"
            last_updated = time.time()
            with open(local_path, "wb") as f:
                try:
                    data = picture.file.read()
                except AttributeError:
                    raise cherrypy.HTTPRedirect('/editProfilePage')
                f.write(data)
                f.close()
                directory = "/img/" + cherrypy.session['username'] + ".jpg"
                databaseControl.updateProfilePicture(username, last_updated, directory)
                raise cherrypy.HTTPRedirect('/')
        except KeyError:
            self.log_error("KeyError within editProfilePicture")
            raise cherrypy.HTTPRedirect('/')
        except:
            self.log_error("Error within editProfilePicture")
            raise cherrypy.HTTPRedirect('/')
        

    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def getProfile(self):
        '''Returns JSON of requested user's profile '''
        try:
            request_profile = cherrypy.request.json
            profile_user = databaseControl.getProfile(request_profile['profile_username'])
            ip = databaseControl.getIPPort(request_profile['profile_username'])
            abso_pic = "http://{}:{}{}".format(ip[0], listen_port, profile_user[6])
            profile_dict = {'lastUpdated' : profile_user[1], 'fullname' : profile_user[2], 'position' : profile_user[3], 'description' : profile_user[4],
                            'location' : profile_user[5], 'picture' : abso_pic}
            profile_dict = json.dumps(profile_dict)
            return profile_dict
        except AttributeError:
            self.log_error("AttributeError within editProfilePage")
        except:
            self.log_error("Error within editProfilePage")
            raise cherrypy.HTTPRedirect('/')


    #---------------------Receivers and Senders--------------------------
            
    @cherrypy.expose
    def prepMessages(self, destination, message):
        '''Prepares messages to be sent as JSON'''

        message.replace("<", "_")
        Page = "Error: </br>"
        stamp = time.time()
        dict_output = {'sender': cherrypy.session['username'], 'destination': destination, 'message':message, 'stamp': str(stamp),
                       'encoding': None, 'encryption':None, 'hashing':None, 'hash':None, 'decryptionKey':None, 'groupID':None}
        
        #Should ping
        try:
            IPPort = databaseControl.getIPPort(destination)
            ping = "http://{}:{}/ping?sender={}".format(IPPort[0], IPPort[1], cherrypy.session['username'])
            response = urllib2.urlopen(ping, timeout = 1)
            url_message = "http://{}:{}/receiveMessage".format(IPPort[0], IPPort[1])
            req = urllib2.Request(url_message, json.dumps(dict_output), {'Content-Type':'application/json'})
            response = urllib2.urlopen(req, timeout = 1)
            databaseControl.updateNewMessages(cherrypy.session['username'], destination, message, stamp)
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except urllib2.URLError, e:
            print e
            self.log_error("urllib2.URLError within prepMessages")
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except urllib2.HTTPError, e:
            self.log_error("urllib2.HTTPError within prepMessages")
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except TypeError:
            self.log_error("TypeError within prepMessages")
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except KeyError:
            self.log_error("KeyError within prepMessages")
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except:
            self.log_error("Error within prepMessages")
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))

    
    @cherrypy.expose
    def prepFiles(self, destination, filename):
        ''' Prepares files to be sent as JSON'''
        Page = "Error: </br>"
        stamp = time.time()

        local_path = "files/" + cherrypy.session['username'] + "file"
        last_updated = time.time()

        file_name = str(filename.filename)
        content_type = str(filename.content_type)
        
        #Wrties file down
        with open(local_path, "wb") as f:
            data = filename.file.read()
            base64_file = base64.b64encode(data)
            f.write(data)
            f.close()
            
        dict_output = {'sender': cherrypy.session['username'], 'destination': destination, 'file': base64_file, 'filename': file_name, 'content_type': content_type, 'stamp': str(stamp),
                       'encoding': None, 'encryption':None, 'hashing':None, 'hash':None, 'decryptionKey':None, 'groupID':None}
        #Should ping
        try:
            IPPort = databaseControl.getIPPort(destination)
            ping = "http://{}:{}/ping?sender={}".format(IPPort[0], IPPort[1], cherrypy.session['username'])
            response = urllib2.urlopen(ping, timeout = 1)
            url_message = "http://{}:{}/receiveFile".format(IPPort[0], IPPort[1])
            req = urllib2.Request(url_message, json.dumps(dict_output), {'Content-Type':'application/json'})
            response = urllib2.urlopen(req, timeout = 1)
            databaseControl.updateNewFile(cherrypy.session['username'], destination, base64_file, file_name, content_type, stamp)
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except urllib2.URLError, e:
            self.log_error("urllib2.URLError within prepFiles")
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except urllib2.HTTPError, e:
            self.log_error("urllib2.HTTPError within prepFiles")
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except TypeError:
            self.log_error("TypeError within prepFiles")
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except KeyError:
            self.log_error("KeyError within prepFiles")
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except Exception as e:
            print e
            self.log_error("Error within prepFiles")
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))


    
    @cherrypy.expose
    @cherrypy.tools.json_in() 
    def receiveMessage(self):
        '''Receives message JSON and saves into database'''
        try:
            messages = cherrypy.request.json
            sender = messages['sender'].replace("<", "_")
            destination = messages['destination'].replace("<", "_")
            message = messages['message'].replace("<", "_")
            databaseControl.updateNewMessages(messages['sender'], messages['destination'], messages['message'], messages['stamp'])
            return "0"
        except AttributeError:
            self.log_error("AttributeError within receiveMessage")
            raise cherrypy.HTTPRedirect('/')
        except urllib2.HTTPError:
            self.log_error("HTTPError within receiveMessage")
            raise cherrypy.HTTPRedirect('/')
        except:
            self.log_error("Error within receiveMessage")
            raise cherrypy.HTTPRedirect('/')
            
    
    @cherrypy.expose
    @cherrypy.tools.json_in() 
    def receiveFile(self):
        ''' Receives file JSON and saves into database'''
        try:
            files = cherrypy.request.json 
            databaseControl.updateNewFile(files['sender'], files['destination'], files['file'], files['filename'], files['content_type'], files['stamp'])
            return "0"
        except AttributeError:
            self.log_error("AttributeError within receiveFile")
            raise cherrypy.HTTPRedirect('/')
        except urllib2.HTTPError:
            self.log_error("HTTPError within receiveFile")
            raise cherrypy.HTTPRedirect('/')
        except:
            self.log_error("Error within receiveFile")
            raise cherrypy.HTTPRedirect('/')

    #---------------------Serving item methods--------------------------

    
    @cherrypy.expose
    def css(self, fname):
        '''Returns CSS object'''
        try:
            #If media requested, set the content type of the response
            #read the file, and dump it out in the response
            cherrypy.response.headers['Content-Type'] = mimetypes.guess_type(fname)[0]
            f = open(fname,"r") #Note: text is r, binary is rb
            data = f.read()
            f.close()
            return data
        except IOError:
            self.log_error("IOError within css")
            raise cherrypy.HTTPRedirect('/')
        except:
            self.log_error("Error within css")
            raise cherrypy.HTTPRedirect('/')

    
    @cherrypy.expose
    def js(self, fname):
        '''Returns Javascript object'''
        try:
            #If media requested, set the content type of the response
            #read the file, and dump it out in the response
            cherrypy.response.headers['Content-Type'] = mimetypes.guess_type(fname)[0]
            f = open(fname,"r") #Note: text is r, binary is rb
            data = f.read()
            f.close()
            return data
        except IOError:
            self.log_error("IOError within js")
            raise cherrypy.HTTPRedirect('/')
        except:
            self.log_error("Error within js")
            raise cherrypy.HTTPRedirect('/')

    
    @cherrypy.expose
    def img(self, fname):
        '''Returns Image'''
        try:
            #If media requested, set the content type of the response
            #read the file, and dump it out in the response
            cherrypy.response.headers['Content-Type'] = mimetypes.guess_type(fname)[0]
            f = open("files/" + fname,"rb") #Note: text is r, binary is rb
            data = f.read()
            f.close()
            return data
        except IOError:
            self.log_error("IOError within img")
            raise cherrypy.HTTPRedirect('/')
        except:
            self.log_error("Error within img")
            raise cherrypy.HTTPRedirect('/')


    #---------------------Threading for continuous login--------------------------

     
    def continuousLogin(self, username, password, location, stop_event):
        '''Continuously runs login'''
        while not stop_event.is_set():
            try:
                print "-----------------------Relogging " + username + "-----------------------"
                self.successfulLogin(username, password, location)
            finally:
                time.sleep(60)
                
    
    def thread_start(self, param):
        '''Creates thread'''
        global stop_event
        stop_event = threading.Event()
        username = param[0]
        password = param[1]
        location = param[2]
        p = thread.start_new_thread(self.continuousLogin, (username, password, location, stop_event))

    
    def thread_stop(self):
        '''Stops threads on request'''
        stop_event.set()


    #---------------------Login Methods--------------------------
    
    @cherrypy.expose
    def login(self):
        ''' Opens login html page'''
        Page = open("login.html") 
        return Page

    
    def check_login(self):
        '''Check if another user is logged in'''
        if (logged_in == False):
            return False;
        else:
            return True;
        
    # LOGGING IN AND OUT
    @cherrypy.expose
    def signin(self, username=None, password=None, location=None):
        '''First check to see if they can login to the server'''
        if self.check_login() == True:
            raise cherrypy.HTTPRedirect('/login')
        else:
            #heck their name and password and send them either to the 2FA page, or back to the main login screen.
            username = username.replace("<", "_")
            password = password.replace("<", "_")
            cherrypy.session['temp_password'] = password
            cherrypy.session['temp_location'] = location
            cherrypy.session['sent_email'] = 0
            cherrypy.session['sent_email'] = False
            error = self.successfulLogin(username,password,location)
            if (error == "0"):
                self.logoff(username, password)
                databaseControl.createTable()
                self.authen_mail(username)
                raise cherrypy.HTTPRedirect('/authenticator?username={}'.format(username))
            else:
                raise cherrypy.HTTPRedirect('/login')

    @cherrypy.expose
    def signout(self):
        '''Signs out user and stops auto relogging'''
        try:
            username = cherrypy.session.get('username')
            if (username == None):
                pass
            else:
                self.logoff(cherrypy.session['username'], cherrypy.session['username'])
                cherrypy.lib.sessions.expire()
                logged_in = False
                self.thread_stop()
            raise cherrypy.HTTPRedirect('/')
        except:
            self.log_error("Error within receiveMessage")
            raise cherrypy.HTTPRedirect('/')

    
    def logoff(self, username, password):
        '''Signs user off login server'''
        url = "https://cs302.pythonanywhere.com/logoff"
        
        encrypt = hashlib.sha256(str(password) + str(username))
        param = {'username' : username,
                'password' : encrypt.hexdigest(),
                 'enc' : 0}
        
        encrypt = hashlib.sha256(str(password) + str(username))
        data = urllib.urlencode(param)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        return the_page[0]
        

    
    @cherrypy.expose
    def authenticator(self, username):
        '''Returns authenticator page after login'''
        Page = open("authenticator.html").read().format(username.replace("<", "_"))
        return Page
    
    
    def authen_mail(self, username):
        '''Sends authentication mail to user'''
        while cherrypy.session['sent_email'] == False:
            code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
            databaseControl.insertCode(username, code)
            user_mail = username + "@aucklanduni.ac.nz"
            mail = smtplib.SMTP('smtp.gmail.com', 587)
            mail.ehlo()
            mail.starttls()
            mail.login('pjoe652.2fa@gmail.com', 'testserver123')
            mail.sendmail('pjoe652.2fa@gmail.com', user_mail, code)
            mail.close()
            cherrypy.session['sent_email'] = True
        
    
    @cherrypy.expose
    def verify_code(self, username, code):
        '''Compares input code with code in database'''
        try:
            if databaseControl.verifyCode(username, code) == True:
                error = self.successfulLogin(username, cherrypy.session['temp_password'], cherrypy.session['temp_location'])
                if (error == "0"):
                    cherrypy.session['username'] = username.replace("<", "_");
                    cherrypy.session['password'] = cherrypy.session['temp_password'];
                    cherrypy.session['location'] = cherrypy.session['temp_location'];
                    params = [cherrypy.session['username'], cherrypy.session['password'], cherrypy.session['location']]
                    self.thread_start(params)
                    logged_in = True
                    raise cherrypy.HTTPRedirect('/')
                else:
                    raise cherrypy.HTTPRedirect('/login')

            else:
                raise cherrypy.HTTPRedirect('/authenticator?username={}'.format(username))
        except KeyError:
            self.log_error("KeyError within verify_code")
            raise cherrypy.HTTPRedirect('/login')
            
    
    def successfulLogin(self, username, password, location):
        '''Connects to the Login Server to report user has logged in'''
        
        url = "https://cs302.pythonanywhere.com/report"
        encrypt = hashlib.sha256(str(password) + str(username))
        param = {'username' : username,
                'password' : encrypt.hexdigest(),
                'location' : location,
                'ip' : ipv4,
                #If at home
                #'ip' : "203.173.216.225",
                'port' : listen_port,
                'enc' : 0}
        data = urllib.urlencode(param)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        return the_page[0]


            


def error_page_404(status, message, traceback, version):
    '''Returns a 404 page when a function with unknown parameters is called'''
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    with open('errorlog.txt', 'a+') as log:
        log.write(timestamp + ":" + "404 Error has occured" + "\n")
    Page = open('404.html')
    return Page

def runMainApp():
    # Create an instance of MainApp and tell Cherrypy to send all requests under / to it. (ie all of them)
    path   = os.path.abspath(os.path.dirname(__file__)) 
    conf = {
        '/': {
            'tools.session.on': True,
            'tools.staticdir.root':os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : './public'
        },
        '/css' : {
        'tools.staticdir.on'  : True,
        'tools.staticdir.dir' : os.path.join(path, 'css')
        }
    }
    cherrypy.tree.mount(MainApp(), "/")

    # Tell Cherrypy to listen for connections on the configured address and port.
    cherrypy.config.update({'server.socket_host': listen_ip,
                            'server.socket_port': listen_port,
                            'engine.autoreload.on': True,
                            'error_page.404': error_page_404,
                           })

    print "========================="
    print "University of Auckland"
    print "COMPSYS302 - Software Design Application"
    print "========================================"                       
    
    # Start the web server
    cherrypy.engine.start()

    # And stop doing anything else. Let the web server take over.
    cherrypy.engine.block() 
 
#Run the function to start everything
runMainApp()
