import sqlite3
import urllib
import json
import urllib2
import time


""" databaseControl.py

    COMPSYS302 - Software Design
    Author: Peter Joe (pjoe652@auckland.ac.nz)
    Last Edited: 7/06/2018

    This controls all interactions with the database, if a certain command is needed it
    is called here
"""

def createTable():
    '''Creates a database if one doesn't exist'''
    conn = sqlite3.connect('userDatabase.db')
    c = conn.cursor()

    #Online User table
    c.execute("""CREATE TABLE IF NOT EXISTS online_users (
                username TEXT,
                ip TEXT,
                location TEXT,
                lastLogin TEXT,
                port TEXT
                )""")

    #Online User table
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                username TEXT,
                code TEXT DEFAULT '',
                UNIQUE(username)
                )""")
        
    #User Profile table
    c.execute("""CREATE TABLE IF NOT EXISTS user_profile (
                username TEXT,
                last_updated TEXT DEFAULT '',
                full_name TEXT DEFAULT '',
                position TEXT DEFAULT '',
                description TEXT DEFAULT '',
                location TEXT DEFAULT '',
                picture TEXT DEFAULT '',
                UNIQUE(username)
                )""")

    #Messages table
    c.execute("""CREATE TABLE IF NOT EXISTS messages (
                destination TEXT,
                messages TEXT DEFAULT '',
                file TEXT DEFAULT '',
                filename TEXT DEFAULT '',
                content_type TEXT DEFAULT '',
                sender TEXT,
                time TEXT
                )""")

    #Gets all users from Login server
    link = "http://cs302.pythonanywhere.com/listUsers"
    f = urllib.urlopen(link)
    myfile = f.read()
    users = myfile.split(',')
    for user in users:
        c.execute("INSERT OR IGNORE INTO user_profile (username) VALUES (?)", (user,))
        c.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (user,))
    conn.commit()
    conn.close()


def insertCode(username, code):
    '''Inserts authenticator code into database'''
    conn = sqlite3.connect('userDatabase.db')
    c = conn.cursor()

    c.execute("UPDATE users SET code=? WHERE username=?", (code, username))

    conn.commit()
    conn.close()


def verifyCode(username, code):
    '''Verifies input code to stored code'''
    conn = sqlite3.connect('userDatabase.db')
    c = conn.cursor()

    c.execute("SELECT code FROM users WHERE username=?", (username,))
    value = c.fetchone()
    if (code == value[0]):
        return True
    else:
        return False


def updateOnlineUsers(username, password):
    '''Automatically updates users'''
    conn = sqlite3.connect('userDatabase.db')
    c = conn.cursor()
    
    param = {'username' : username,
            'password' : password,
            'json' : 1}

    url = "http://cs302.pythonanywhere.com/getList"
    
    data = urllib.urlencode(param)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    the_page = response.read()
    extracted = json.loads(the_page)

    #Clear records
    c.execute("DELETE FROM online_users")

    #Input data into database
    for i in range(0, len(extracted)):
            
        #Extracts User details
        if (extracted[str(i)]['username'] != username):
            username = str(extracted[str(i)]["username"])
            ip = str(extracted[str(i)]["ip"])
            location = str(extracted[str(i)]["location"])
            lastLogin = float(extracted[str(i)]["lastLogin"])
            port = str(extracted[str(i)]["port"])

            lastLogin = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(lastLogin))
                    
            userDetails = [username, ip, location, lastLogin, port]

            #Insert values into database
            c.execute("REPLACE INTO online_users VALUES (?,?,?,?,?)", userDetails) 
                
            conn.commit()
    conn.close()


def updateNewMessages(sender, destination, message, stamp_time):
    '''Inserts new message into database'''
    conn = sqlite3.connect('userDatabase.db')
    c = conn.cursor()

    stamp_time = float(stamp_time)
    
    stamp_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stamp_time))

    messageDetails = [destination, message, sender, stamp_time]

    #Insert message into database
    c.execute("INSERT INTO messages ('destination', 'messages', 'sender', 'time') VALUES (?,?,?,?)", messageDetails)

    conn.commit()
    conn.close()


def updateNewFile(sender, destination, base64_file, filename, content_type, stamp_time):
    '''Inserts new file into database'''
    conn = sqlite3.connect('userDatabase.db')
    c = conn.cursor()

    stamp_time = float(stamp_time)
    
    stamp_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stamp_time))

    fileDetails = [destination, base64_file, filename, content_type, sender, stamp_time]

    #Insert file into database
    c.execute("INSERT INTO messages ('destination', 'file', 'filename', 'content_type', 'sender', 'time') VALUES (?,?,?,?,?,?)", fileDetails)

    conn.commit()
    conn.close()


def updateProfileDetails(profile_username, last_updated, fullname, position, description, location):
    '''Updates profile in database'''
    conn = sqlite3.connect("userDatabase.db")
    c = conn.cursor()

    c.execute("""UPDATE user_profile SET last_updated = ?, full_name = ?,
                position = ?, description = ?, location = ?
                WHERE username =? """, (last_updated, fullname, position, description, location, profile_username))

    conn.commit()
    conn.close()


def updateProfilePicture(profile_username, last_updated, picture):
    '''Updates profile picture in database'''
    conn = sqlite3.connect("userDatabase.db")
    c = conn.cursor()

    c.execute("""UPDATE user_profile SET last_updated = ?, picture = ?
                WHERE username =?""", (last_updated, picture, profile_username))

    conn.commit()
    conn.close()


def checkUserExists(user):
    '''Returns 0 if not online, return 1 if online'''
    conn = sqlite3.connect("userDatabase.db")
    c = conn.cursor()

    c.execute("SELECT EXISTS(SELECT 1 FROM online_users WHERE username = ? LIMIT 1)", (user,))

    values = c.fetchone()
    conn.close()
    return values[0]
    

def getIPPort(user):
    '''Get IP and Port of select user'''
    conn = sqlite3.connect("userDatabase.db")
    c = conn.cursor()
    
    c.execute("SELECT * FROM online_users WHERE username = ?", (user,))
    values = c.fetchone()

    ipport = [values[1], values[4]]
    return ipport


def getMessage(sender, destination):
    '''Returns messages between sender and destination'''
    conn = sqlite3.connect("userDatabase.db")
    c = conn.cursor()

    c.execute("SELECT * FROM messages WHERE (destination = ? AND sender = ?) OR (destination = ? AND sender = ?)", (destination, sender, sender, destination))
    values = c.fetchall()
    message_log = []
    for message in values:
        message_send = {'sender': message[5], 'message':message[1], 'timestamp':message[6], 'file':message[2], 'filename':message[3], 'content_type':message[4]}
        message_log.append(message_send)


    return message_log


def getAllUsers():
    '''Returns all users from database'''
    conn = sqlite3.connect("userDatabase.db")
    c = conn.cursor()

    c.execute("SELECT username FROM users ORDER BY LOWER(username)")
    values = c.fetchall()
    all_users = []
    for users in values:
        all_users.append(str(users[0]))
    return all_users


def getOnlineUsers():
    '''Return all online users'''
    conn = sqlite3.connect("userDatabase.db")
    c = conn.cursor()

    c.execute("SELECT username FROM online_users ORDER BY LOWER(username)")
    values = c.fetchall()
    online_users = []
    for users in values:
        online_users.append(str(users[0]))
    return online_users


def getOfflineUsers():
    '''Returns all offline users'''

    offline_users = getAllUsers()

    online_users = getOnlineUsers()
    for online in online_users:
        if online in offline_users:
            offline_users.remove(online)

    return offline_users


def getProfile(username):
    '''Return profile of user in local database'''
    conn = sqlite3.connect("userDatabase.db")
    c = conn.cursor()

    c.execute("SELECT * FROM  user_profile WHERE username = ?", (username,))
    value = c.fetchone()


    return value


def updateUserProfile(username, sender):
    '''Returns profile of user from another database'''
    conn = sqlite3.connect("userDatabase.db")
    c = conn.cursor()

    try:
        connect_info = getIPPort(username)
        
        param = {'profile_username' : username,
            'sender' : sender }

        #url = "http://cs302.pythonanywhere.com/getList"
        url = "http://{}:{}/getProfile".format(connect_info[0], connect_info[1])
        
        req = urllib2.Request(url, json.dumps(param), {'Content-Type':'application/json'})
    
        response = urllib2.urlopen(req, timeout = 1)
        the_page = response.read()
        extracted = json.loads(the_page)

        #Extracts information
        last_updated = str(extracted["lastUpdated"])
        fullname = str(extracted["fullname"])
        position = str(extracted["position"])
        description = str(extracted["description"])
        location = str(extracted["location"])
        picture = str(extracted["picture"])

        #Updates user profile
        c.execute("""UPDATE user_profile SET last_updated = ?, full_name = ?,
                position = ?, description = ?, location = ?, picture = ?
                WHERE username =? """, (last_updated, fullname, position, description,
                                                location, picture, username))
        conn.commit()
        conn.close()
    except urllib2.URLError, e:
        print "Could not connect to the User's profile"
    except urllib2.HTTPError, e:
        raise "A HTTP Error has occured"
    except TypeError:
        print "Could not connect to the User's profile"
    except Exception:
        print "An error has occuered"




