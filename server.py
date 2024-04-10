import os
from flask import Flask, request, render_template, jsonify, abort, make_response
from requests import get, post
import json
import sqlite3
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

app = Flask(__name__, static_folder='public', template_folder='views')

@app.after_request 
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    # Other headers can be added here if needed
    return response
  

token = os.environ.get('TOKEN')
adm_pass = os.environ.get('ADMIN_SECRET')
auth_secret = os.environ.get('AUTH_SECRET')

@app.route('/v1/admin/getDB')
def get_db():
    if request.args['secret']!=adm_pass:
      abort(401)
    conn = sqlite3.connect('test_database') 
    c = conn.cursor()
    c.execute('''
          SELECT
          id,
          firstname,
          lastname,
          email,
          password
          FROM users
          ''')
    df = pd.DataFrame(c.fetchall(), columns=['id','firstname','lastname','email','password'])
    conn.commit()
    return df.to_string(index=False).replace('\n', '<br>')

@app.route('/v1/admin/createDB')
def create_db():
    if request.args['secret']!=adm_pass:
      abort(401)
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

@app.route('/v1/admin/deleteRecord')
def deleteRecord():
    if request.args['secret']!=adm_pass:
      abort(401)
    try:
        sqliteConnection = sqlite3.connect('test_database')
        cursor = sqliteConnection.cursor()
        sql_delete_query = '''DELETE from users where id = "''' + request.args['id'] + '''"'''
        cursor.execute(sql_delete_query)
        sqliteConnection.commit()
        print("Record deleted successfully ")
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to delete record from sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            return "the sqlite connection is closed"
        
@app.route('/')
def homepage():
    """Displays the homepage."""
    return render_template('index.html')
  
@app.route('/v1/feedback/postFeedback', methods=['POST'])
def postFeedback():
    data = json.loads(request.data)
    message = "Feedback from: " + data["name"] + "\n\n" + "E-mail: " + data["email"] + "\n\n" + data["feedback"]
    req = get('https://api.telegram.org/bot' + token + '/sendMessage?chat_id=468110974&parse_mode=Markdown&text=' + message)
    return req.content, req.status_code
  
@app.route('/v1/users/addUser', methods=['POST'])
def addUser():
    data = json.loads(request.data)
    conn = sqlite3.connect('test_database') 
    c = conn.cursor()
    pwd = generate_password_hash(data['password'], "sha256")
    try:
      c.execute('''
          INSERT INTO users (firstname, lastname, email, password)
                VALUES
                ("''' + data['name'] + '''","''' + data['lastname'] + '''"
                ,"''' + data['email'] + '''","''' + pwd + '''")
          ''')
      conn.commit()
    except:
      abort(403)
    return "ok"
  
@app.route('/v1/users/authorize', methods=['POST'])
def authorize():
    data = json.loads(request.data)
    conn = sqlite3.connect('test_database') 
    c = conn.cursor()
    c.execute('''
          SELECT password FROM users WHERE email = "''' + data['email'] + '''"
          ''')
    pwd_hash = c.fetchall()[0][0]
    isTrue = check_password_hash(pwd_hash, data['password'])
    if not isTrue:
      abort(401)
    c.execute('''
          SELECT firstname, lastname FROM users WHERE email = "''' + data['email'] + '''"
          ''')
    user_data = c.fetchall()
    firstname = user_data[0][0]
    lastname = user_data[0][1]
    encoded_jwt = jwt.encode({'firstname': firstname, 'lastname': lastname}, auth_secret, algorithm='HS256')
    conn.commit()
    return encoded_jwt
  
@app.route('/v1/users/getUser', methods=['GET'])
def getUser():
    auth = request.headers.get('Authorization')
    return jsonify(jwt.decode(auth, auth_secret, algorithms=["HS256"]))

if __name__ == '__main__':
    app.run()