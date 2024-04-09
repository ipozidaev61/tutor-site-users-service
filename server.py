import os
from flask import Flask, request, render_template, jsonify, abort
from requests import get, post
import json
import sqlite3
import pandas as pd

#conn = sqlite3.connect('test_database') 
                     
#conn.commit()

app = Flask(__name__, static_folder='public', template_folder='views')

token = os.environ.get('TOKEN')
adm_pass = os.environ.get('ADMIN_SECRET')

@app.route('/v1/admin/getDB')
def get_db():
    if request.args['secret']!=adm_pass:
      abort(401)
    conn = sqlite3.connect('test_database') 
    c = conn.cursor()
    df = pd.DataFrame(c.fetchall(), columns=['id','username','password'])
    conn.commit()
    return str(df)

@app.route('/v1/admin/createDB')
def create_db():
    conn = sqlite3.connect('test_database') 
    c = conn.cursor()
    c.execute('''
          CREATE TABLE user (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT UNIQUE NOT NULL,
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
    

if __name__ == '__main__':
    app.run()