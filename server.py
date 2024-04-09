import os
from flask import Flask, request, render_template, jsonify
from requests import get, post
import json
import sqlite3
import click
from flask import current_app, g

app = Flask(__name__, static_folder='public', template_folder='views')

token = os.environ.get('TOKEN')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
        
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@app.route('/')
def homepage():
    """Displays the homepage."""
    return render_template('index.html')
  
@app.route('/postFeedback', methods=['POST'])
def postFeedback():
    data = json.loads(request.data)
    message = "Feedback from: " + data["name"] + "\n\n" + "E-mail: " + data["email"] + "\n\n" + data["feedback"]
    req = get('https://api.telegram.org/bot' + token + '/sendMessage?chat_id=468110974&parse_mode=Markdown&text=' + message)
    return req.content, req.status_code
    

if __name__ == '__main__':
    app.run()