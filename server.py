import os
from flask import Flask, request, render_template, jsonify, abort
from flask.ext.cors import CORS, cross_origin
from requests import get, post
import json
import sqlite3
import pandas as pd
from werkzeug.security import generate_password_hash

app = Flask(__name__, static_folder='public', template_folder='views')
cors = CORS(app, resources={r"/foo": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

token = os.environ.get('TOKEN')
adm_pass = os.environ.get('ADMIN_SECRET')

@app.route('/v1/admin/getDB')
def get_db():
    if request.args['secret']!=adm_pass:
      abort(401)
    conn = sqlite3.connect('test_database') 
    c = conn.cursor()
    c.execute('''
          SELECT
          a.id,
          a.firstname,
          a.lastname,
          a.email,
          a.password
          FROM users a
          ''')
    df = pd.DataFrame(c.fetchall(), columns=['id','firstname','lastname','email','password'])
    conn.commit()
    return df.to_string(index=False).replace('\n', '<br>')

@app.route('/v1/admin/createDB')
def create_db():
    conn = sqlite3.connect('test_database') 
    c = conn.cursor()
    c.execute('''
          CREATE TABLE users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          firstname TEXT NOT NULL,
          lastname TEXT NOT NULL,
          email TEXT UNIQUE NOT NULL,
          password TEXT NOT NULL
          );
          ''')
    conn.commit()
    return "ok"
        
@app.route('/')
def homepage():
    """Displays the homepage."""
    return render_template('index.html')
  
@app.route('/v1/postFeedback', methods=['POST'])
def postFeedback():
    data = json.loads(request.data)
    message = "Feedback from: " + data["name"] + "\n\n" + "E-mail: " + data["email"] + "\n\n" + data["feedback"]
    req = get('https://api.telegram.org/bot' + token + '/sendMessage?chat_id=468110974&parse_mode=Markdown&text=' + message)
    return req.content, req.status_code
  
@app.route('/v1/addUser', methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def addUser():
    data = json.loads(request.data)
    conn = sqlite3.connect('test_database') 
    c = conn.cursor()
    pwd = generate_password_hash(data['password'], "sha256")
    c.execute('''
          INSERT INTO users (firstname, lastname, email, password)
                VALUES
                ("''' + data['name'] + '''","''' + data['lastname'] + '''"
                ,"''' + data['email'] + '''","''' + pwd + '''")
          ''')
    conn.commit()
    return "ok"
    

if __name__ == '__main__':
    app.run()