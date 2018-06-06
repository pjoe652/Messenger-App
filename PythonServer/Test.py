import sqlite3
import urllib2
import urllib
import json
import databaseControl
import os
import time
import base64
import hashlib
import threading
import thread
import time
import random
import string

cwd = os.getcwd()
cwd += "\files"

dir_path = os.path.dirname(os.path.realpath(__file__))

def getOnlineUsers():
    conn = sqlite3.connect("userDatabase.db")
    c = conn.cursor()

    c.execute("SELECT username FROM online_users")
    values = c.fetchall()
    online_users = []
    for users in values:
        online_users.append(str(users[0]))
    return online_users


#print getOnlineUsers()

link = "http://cs302.pythonanywhere.com/listUsers"
f = urllib.urlopen(link)
myfile = f.read()
users = myfile.split(',')



names = ["peter", "josh", "heya"]
#print json.dumps(names)
online = {}
online_users = databaseControl.getOnlineUsers()
#for x in range(0, len(online_users)):
#     online = {'id' : x, 'username': online_users[x][0]}
    
#print online

"""param = {'profile_username' : "dcho415",
         'sender' : "anyone" }
url = "http://121.98.194.183:80/getProfile"
    
req = urllib2.Request(url, json.dumps(param), {'Content-Type':'application/json'})
response = urllib2.urlopen(req)
the_page = response.read()
extracted = json.loads(the_page)
    
print type(str(extracted['picture']))"""

"""#Return profile of user in local database
def getProfile(username):
    conn = sqlite3.connect("userDatabase.db")
    c = conn.cursor()

    c.execute("SELECT * FROM  user_profile WHERE username = '{}'".format(username))
    value = c.fetchone()

    return value

value = getProfile("pjoe652")
print value[0]
print value[1]
print value[2]
print value[3]
print value[4]
print value[5]
print value[6]"""


'''class ThreadingExample(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, interval=1):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        """ Method that runs forever """
        while True:
            # Do something
            print('Doing something imporant in the background')

            time.sleep(self.interval)

example = ThreadingExample()
time.sleep(3)
print('Checkpoint')
time.sleep(2)
print('Bye')'''
test="f"

def successfulLogin(username, password, location):
    url = "https://cs302.pythonanywhere.com/report"
    encrypt = hashlib.sha256(str(password) + str(username))
    param = {'username' : username,
            'password' : encrypt.hexdigest(),
            'location' : location,
            #'ip' : ipv4,
            #If at home
            'ip' : "203.173.216.225",
            'port' : "10002",
            'enc' : 0}
    data = urllib.urlencode(param)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    the_page = response.read()
    print the_page[0]

'''def relogger():
    # Check if stop or set next timer
    #username = cherrypy.session.get('username')
    param = ["pjoe652", "fictionpack", "2"]
    username = "pjoe652"
    password = 'fictionpack'
    location = '2'
    successfulLogin(username, password, location)
    threading.Timer(2, relogger).start()'''

'''
t = threading.Timer(4, relogger)
t.start()
time.sleep(50)
t.cancel()'''

'''def verifyCode(username, code):
    
    conn = sqlite3.connect('userDatabase.db')
    c = conn.cursor()

    c.execute("SELECT code FROM users WHERE username='{}'".format(username))
    value = c.fetchone()
    if (code == value[0]):
        return True
    else:
        return False

verify = verifyCode("pjoe652", "testtest")
print verify'''

'''code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
print code'''

def log_error(error):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    with open('errorlog.txt', 'a+') as log:
        log.write(timestamp + ":" + error + "\n")

log_error("hello")
log_error("test")
