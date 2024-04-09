import os
from flask import Flask, request, render_template, jsonify
from requests import get, post
import json
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func

app = Flask(__name__, static_folder='public', template_folder='views')

token = os.environ.get('TOKEN')

@app.route('/admin/getDB')
def get_db_command():
    return get_db()

@app.route('/admin/initDB')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    return "ok"
        
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