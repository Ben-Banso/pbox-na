from flask import (
    Flask,
    jsonify,
    abort,
    request,
    render_template,
    g
)


import subprocess
import os
import sys
import sqlite3

import random
import string

import datetime
import configparser

import rsa
from base64 import b64encode, b64decode


# If we run as app
if(__name__ == "__main__"):
    config = configparser.RawConfigParser()
    config.read("/etc/pbox-na/settings.conf")
    PORT=config.get("Config", "PORT")
    DB_PATH = config.get("Config", "DB_PATH")
# For tests
else:
    PORT=5000
    DB_PATH="na.db"

db_conn = sqlite3.connect(DB_PATH)
db = db_conn.cursor()

db.execute('''CREATE TABLE IF NOT EXISTS users (username text, public_key text, memory int, storage int, cpu int)''')
db.execute('''CREATE TABLE IF NOT EXISTS challenges (remote_addr text, challenge text, creation_date timestamp)''')
db.execute('''CREATE TABLE IF NOT EXISTS tokens (username text, remote_addr text, token text, creation_date timestamp)''')

db_conn.close()





# Create the application instance
app = Flask(__name__, template_folder="templates")

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def check_token(request):
    """
    This take a request object, check the presence and the validity of the token

    :return:        the ID of the user logged in
    """
    if 'X-Api-Token' in request.headers:
        token = request.headers['X-Api-Token'].strip('\n')
        user_id = ""
        db_conn = get_db()
        db = db_conn.cursor()
        for row in db.execute('SELECT username FROM tokens WHERE token=?', [token]):
            user_id = row[0]
        if(user_id == ""):
            abort(401)

    else:
        abort(401)
    return user_id


# Create a URL route in our application for "/"
@app.route('/')
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    return "hi"

@app.route('/api/auth', methods=['POST'])
def auth_api():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    if not request.json:
        abort(400)

    if 'seed' in request.json:
    # Is the challen key is not here, it's the first step of authentication
        # Generate a challenge
        challenge = request.json['seed'] + ''.join(random.choice(string.ascii_letters + string.digits) for x in range(40))
        # Put it in database

        db_conn = get_db()
        db = db_conn.cursor()

        try:
            db.execute("INSERT INTO challenges (remote_addr, challenge, creation_date) VALUES (?,?,?)", [request.remote_addr, challenge, datetime.datetime.now()])
            db_conn.commit()
        except sqlite3.IntegrityError:
            abort(400)
        # Sned it back
        return jsonify({'challenge': challenge})
    # Is the challenge is prensent, check the validity
    else:
        challenge = request.json['challenge']
        response = request.json['response']
        remote_addr = request.remote_addr
        user_id = ""
        creation_date = 0

        db_conn = get_db()
        db = db_conn.cursor()

        try:
            for row in db.execute("SELECT creation_date FROM challenges WHERE remote_addr=? and challenge=?", [remote_addr, challenge]):
                creation_date =  row[0]
        except sqlite3.IntegrityError:
            abort(400)

        if creation_date == 0:
            abort(401)

        # For all the users, check if a key decrypt the challenge correctly
        for row in db.execute("SELECT username, public_key FROM users"):
            pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(row[1].replace('\\n', '\n'))
            try:
                check = rsa.verify(challenge.encode('utf-8'), b64decode(response), pub_key)
            except:
                #abort(400)
                print("Do nothing")
            if(check != None):
                user_id = row[0]
        # If one match
        if(user_id != ""):
            # Generate a token
            token = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(50))
            # Save it in database with a timestamp
            db.execute("INSERT INTO tokens (username, remote_addr, token, creation_date) VALUES (?,?,?,?)", [user_id, request.remote_addr, token, datetime.datetime.now()])
            db.execute("DELETE FROM challenges where remote_addr=? and challenge=?", [request.remote_addr, challenge])
            db_conn.commit()

            return jsonify({'status':'success', 'token':token})
        else:
            abort(401)
    abort(400)



@app.route('/api/version')
def get_version():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    user_id = check_token(request)
    f = open("version.txt", 'r')
    version = f.readline().strip('\n')
    f.close()
    return jsonify({"version": version})

@app.route('/api/containers')
def get_containers():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    user_id = check_token(request)
    containers=[]
    result = subprocess.check_output(["docker", "ps", "-q", '-f', 'label=user_uuid=' + user_id ]).decode().strip('\n').split('\n')
    for line in result:
        containers.append({"id":line})
    return jsonify({"containers":containers})

@app.route('/api/containers', methods=['POST'])
def run_container():
    """
    Run a new container for my user

    :return:        ??'
    """
    user_id = check_token(request)

    if(request.json == None or 'docker_image' not in request.json):
        abort(400)

    docker_image = request.json['docker_image']
    containers=[]
    result = subprocess.check_output(["docker", "run", "-d", '-l', 'user_uuid=' + user_id, docker_image ]).decode().strip('\n').split('\n')
    for line in result:
        print(line)
    return jsonify({"containers":containers})

@app.route('/api/containers/<string:container_id>')
def get_container(container_id):
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    user_id = check_token(request)
    container = subprocess.check_output(["docker", "inspect", container_id])
    return jsonify({"containers":{"id":container_id, "details":container}})

@app.route('/api/users')
def get_users():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    user_id = check_token(request)
    users = []

    db_conn = get_db()
    db = db_conn.cursor()
    try:
        for row in db.execute("SELECT username, public_key FROM users"):
            users.append({"username": row[0], "public_key": row[1]})
    except sqlite3.IntegrityError:
        abort(400)


    return jsonify({'users': users})


# If we're running in stand alone mode, run the application
if __name__ == '__main__':

    print("App start")

    app.run(host="0.0.0.0", port=PORT)
