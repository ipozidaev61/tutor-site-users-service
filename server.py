import os
from flask import Flask, request, render_template, jsonify
from requests import get, post
import json

app = Flask(__name__, static_folder='public', template_folder='views')

token = os.environ.get('TOKEN')

@app.route('/')
def homepage():
    """Displays the homepage."""
    return render_template('index.html')
  
@app.route('/postFeedback', methods=['POST'])
def postFeedback():
    data = json.loads(request.data)
    message = "Feedback from: " + data["name"] + "\n\n" + data["feedback"]
    req = get('https://api.telegram.org/bot' + token + '/sendMessage?chat_id=468110974&parse_mode=Markdown&text=' + message)
    return req.content, req.status_code
    

if __name__ == '__main__':
    app.run()