#!/usr/bin/python
""" cherrypy_example.py

    COMPSYS302 - Software Design
    Author: Andrew Chen (andrew.chen@auckland.ac.nz)
    Last Edited: 19/02/2018

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


# The address we listen for connections on
listen_ip = "0.0.0.0"
listen_port = 10002
ipv4 = socket.gethostbyname(socket.gethostname()) 

class MainApp(object): 

    #CherryPy Configuration
    path = os.path.abspath(os.path.dirname(__file__))
    _cp_config = {'tools.encode.on': True, 
                  'tools.encode.encoding': 'utf-8',
                  'tools.sessions.on' : 'True',
                 }                 

    # If they try somewhere we don't know, catch it here and send them to the right place.
    @cherrypy.expose
    def default(self, *args, **kwargs): 
        """The default page, given when we don't recognise where the request is for."""
        Page = "I don't know where you're trying to go, so have a 404 Error."
        cherrypy.response.status = 404
        return Page

    # PAGES (which return HTML that can be viewed in browser)   
    @cherrypy.expose
    def index(self):
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
            Page = "Welcome! This is a test website for COMPSYS302!<br/>"
            Page += "Click here to <a href='login'>login</a>."
        return Page

    #Ping
    @cherrypy.expose
    def ping(self, sender):
        return "0"

    # Updates online users 
    @cherrypy.tools.json_out()
    @cherrypy.expose
    def storeUsers(self):
        #store information
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

    # Updates chat
    @cherrypy.tools.json_out()
    @cherrypy.expose
    def updateChat(self, destination):
        sender = cherrypy.session['username']
        message_log = databaseControl.getMessage(sender, destination)
        sender_profile = databaseControl.getProfile(sender)
        destination_profile = databaseControl.getProfile(destination)

        sender_picture = sender_profile[6]
        destination_picture = destination_profile[6]

        message = ""
                                    
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
                                        message += '<p class="time-log"> {} </p></div></div>'.format(stamp)
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
                                        message += '<div class="chat friend"><div class="user-photo"><img src="{}"></div>'.format(sender_picture)
                                        message += '<img class="chat-message" src="{}">'.format(directory)
                                        message += '<p class="time-log"> {} </p></div>'.format(stamp)
                                    elif ((message_log[x]['content_type'].split("/"))[0] == "audio"):
                                        message += '<div class="chat friend"><div class="user-photo"><img src="{}"></div>'.format(sender_picture)
                                        message += '<div class="chat-message"><audio controls><source src="{}" type="{}">'.format(directory, message_log[x]['content_type'])
                                        message += '</audio></div><p class="time-log"> {} </p></div>'.format(stamp)
                                    elif ((message_log[x]['content_type'].split("/"))[0] == "video"):
                                        message += '<div class="chat friend"><div class="user-photo"><img src="{}"></div>'.format(sender_picture)
                                        message += '<div class="chat-message"><video width="340px" controls>'
                                        message += '<source src="{}" type="{}">'.format(directory, message_log[x]['content_type'])
                                        message += '</video></div><p class="time-log"> {} </p></div>'.format(stamp)
                                    else:
                                        message += '<div class="chat friend"><div class="user-photo"><img src="{}"></div>'.format(sender_picture)
                                        message += '<div class="chat-message"><a href="{}" download>{}</a>'.format(directory, message_log[x]['filename'])
                                        message += '<p class="time-log"> {} </p></div>'.format(stamp)
                                                    

        message_dict = {"data" : message}
        message_dict = json.dumps(message_dict)
        return message_dict

    # This section will allow the user to view other profiles and the
    # edit profile page. The user will also be able to update their
    # profile details such as information displayed or profile picture

    @cherrypy.expose
    def profile(self, destination):

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
            logging.exception("Must be logged in to view profiles")
            raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    def getProfileInfo(self, destination):
        try:
            databaseControl.updateUserProfile(destination, cherrypy.session['username'])
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except urllib2.URLError, e:
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        

    #Loads edit profile page
    @cherrypy.expose
    def editProfilePage(self):
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
            logging.exception("Must be logged in to edit your profile")
            raise cherrypy.HTTPRedirect('/')

    #Saves new profile details on database
    @cherrypy.expose
    def editProfileDetails(self, name=None, position=None, description=None, location=None):
        try:
            profile_user = databaseControl.getProfile(cherrypy.session['username'])
            last_updated = time.time()
            #cwd = os.getcwd()
            databaseControl.updateProfileDetails(cherrypy.session['username'], last_updated, name, position, description, location)
            raise cherrypy.HTTPRedirect('/')
        except KeyError:
            logging.exception("Must be logged in to edit your profile")
            raise cherrypy.HTTPRedirect('/')

    #Saves static image locally and saves path onto database
    @cherrypy.expose
    def editProfilePicture(self, picture=None):
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
            logging.exception("Must be logged in to edit your profile")
            raise cherrypy.HTTPRedirect('/')
        

    #Returns JSON of requested user's profile 
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def getProfile(self):
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
            logging.exception("Request requires a JSON")
            raise cherrypy.HTTPRedirect('/')

        
            
    # Prepares messages to be sent as JSON
    @cherrypy.expose
    def prepMessages(self, destination, message):
        Page = "Error: </br>"
        stamp = time.time()
        dict_output = {'sender': cherrypy.session['username'], 'destination': destination, 'message':message, 'stamp': str(stamp),
                       'encoding': None, 'encryption':None, 'hashing':None, 'hash':None, 'decryptionKey':None, 'groupID':None}
        
        #Should ping
        try:
            IPPort = databaseControl.getIPPort(destination)
            ping = "http://{}:{}/ping?sender={}".format(IPPort[0], IPPort[1], sender)
            response = urllib2.urlopen(ping, timeout = 1)
            url_message = "http://{}:{}/receiveMessage".format(IPPort[0], IPPort[1])
            req = urllib2.Request(url_message, json.dumps(dict_output), {'Content-Type':'application/json'})
            response = urllib2.urlopen(req, timeout = 1)
            databaseControl.updateNewMessages(sender, destination, message, stamp)
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except urllib2.URLError, e:
            checksLogger.error('URLError = ' + str(e.reason))
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except urllib2.HTTPError, e:
            checksLogger.error('HTTPError = ' + str(e.code))
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except httplib.HTTPexception, e:
            checksLogger.error('HTTPException')
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except TypeError:
            logging.exception("A TypeError has occured")
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except KeyError:
            logging.exception("User must be logged into access this page")
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))

    # Prepares files to be sent as JSON
    @cherrypy.expose
    def prepFiles(self, destination, filename):
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
            ping = "http://{}:{}/ping?sender={}".format(IPPort[0], IPPort[1], sender)
            response = urllib2.urlopen(ping, timeout = 1)
            url_message = "http://{}:{}/receiveFile".format(IPPort[0], IPPort[1])
            req = urllib2.Request(url_message, json.dumps(dict_output), {'Content-Type':'application/json'})
            response = urllib2.urlopen(req, timeout = 1)
            databaseControl.updateNewFile(sender, destination, base64_file, file_name, content_type, stamp)
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except urllib2.URLError, e:
            checksLogger.error('URLError = ' + str(e.reason))
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except urllib2.HTTPError, e:
            checksLogger.error('HTTPError = ' + str(e.code))
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except httplib.HTTPexception, e:
            checksLogger.error('HTTPException')
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except TypeError:
            logging.exception("A TypeError has occured")
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        except KeyError:
            logging.exception("User must be logged into access this page")
            raise cherrypy.HTTPRedirect('/profile?destination={}'.format(destination))
        
    @cherrypy.expose
    @cherrypy.tools.json_in() 
    def receiveMessage(self):
        
        try:
            messages = cherrypy.request.json 
            databaseControl.updateNewMessages(messages['sender'], messages['destination'], messages['message'], messages['stamp'])
            return "0"
        except AttributeError:
            logging.exception("Request requires a JSON")
            raise cherrypy.HTTPRedirect('/')
        except urllib2.HTTPError:
            logging.exception("HTTP Error has occured")
            raise cherrypy.HTTPRedirect('/')
        except Exception:
            logging.exception("Could not reach page")
            raise cherrypy.HTTPRedirect('/')
            
    
    @cherrypy.expose
    @cherrypy.tools.json_in() 
    def receiveFile(self):
        try:
            files = cherrypy.request.json 
            databaseControl.updateNewFile(files['sender'], files['destination'], files['file'], files['filename'], files['content_type'], files['stamp'])
            return "0"
        except AttributeError:
            logging.exception("Request requires a JSON")
            raise cherrypy.HTTPRedirect('/')
        except Exception:
            logging.exception("Could not reach page")
            raise cherrypy.HTTPRedirect('/')
    
    @cherrypy.expose
    def login(self):
        Page = open("login.html") 
        return Page

    #Returns CSS object
    @cherrypy.expose
    def css(self, fname):
        try:
            #If media requested, set the content type of the response
            #read the file, and dump it out in the response
            cherrypy.response.headers['Content-Type'] = mimetypes.guess_type(fname)[0]
            f = open(fname,"r") #Note: text is r, binary is rb
            data = f.read()
            f.close()
            return data
        except IOError:
            logging.exception("There such item or direction")
            raise cherrypy.HTTPRedirect('/')

    #Returns Javascript object
    @cherrypy.expose
    def js(self, fname):
        try:
            #If media requested, set the content type of the response
            #read the file, and dump it out in the response
            cherrypy.response.headers['Content-Type'] = mimetypes.guess_type(fname)[0]
            f = open(fname,"r") #Note: text is r, binary is rb
            data = f.read()
            f.close()
            return data
        except IOError:
            logging.exception("There such item or direction")
            raise cherrypy.HTTPRedirect('/')

    #Returns Image
    @cherrypy.expose
    def img(self, fname):
        try:
            #If media requested, set the content type of the response
            #read the file, and dump it out in the response
            cherrypy.response.headers['Content-Type'] = mimetypes.guess_type(fname)[0]
            f = open("files/" + fname,"rb") #Note: text is r, binary is rb
            data = f.read()
            f.close()
            return data
        except IOError:
            logging.exception("There such item or direction")
            raise cherrypy.HTTPRedirect('/')

    '''This section operates the continuous login'''

    def continuousLogin(self, username, password, location, stop_event):
        while not stop_event.is_set():
            try:
                print "-----------------------Relogging " + username + "-----------------------"
                self.successfulLogin(username, password, location)
            finally:
                time.sleep(20)

    def thread_start(self, param):
        global stop_event
        stop_event = threading.Event()
        username = param[0]
        password = param[1]
        location = param[2]
        p = thread.start_new_thread(self.continuousLogin, (username, password, location, stop_event))

    def thread_stop(self):
        stop_event.set()
        
    # LOGGING IN AND OUT
    @cherrypy.expose
    def signin(self, username=None, password=None, location=None):
        """Check their name and password and send them either to the main page, or back to the main login screen."""
        error = self.successfulLogin(username,password,location)
        if (error == "0"):
            cherrypy.session['username'] = username;
            cherrypy.session['password'] = password;
            cherrypy.session['location'] = location;
            params = [cherrypy.session['username'], cherrypy.session['password'], cherrypy.session['location']]
            self.thread_start(params)
            print "Successful Login!"
            databaseControl.createTable()
            raise cherrypy.HTTPRedirect('/')
        else:
            raise cherrypy.HTTPRedirect('/login')

    @cherrypy.expose
    def signout(self):
        """Logs the current user out, expires their session"""
        username = cherrypy.session.get('username')
        if (username == None):
            pass
        
        else:
            cherrypy.lib.sessions.expire()
            self.thread_stop()
        raise cherrypy.HTTPRedirect('/')

    def successfulLogin(self, username, password, location): 
        url = "https://cs302.pythonanywhere.com/report"
        encrypt = hashlib.sha256(str(password) + str(username))
        param = {'username' : username,
                'password' : encrypt.hexdigest(),
                'location' : location,
                #'ip' : ipv4,
                #If at home
                'ip' : "203.173.216.225",
                'port' : listen_port,
                'enc' : 0}
        data = urllib.urlencode(param)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        return the_page[0]

    
def error_page_404(status, message, traceback, version):
    logging.exception("Could not access requested page")
    return "Error 404 - The page you're looking for doesn't exist"




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
