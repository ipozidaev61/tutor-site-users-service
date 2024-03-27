import os
from flask import Flask, request, render_template, jsonify
from requests import get, post

app = Flask(__name__, static_folder='public', template_folder='views')

app.secret = os.environ.get('SECRET')

@app.route('/')
def homepage():
    """Displays the homepage."""
    return render_template('index.html')
  
@app.route('/postFeedback', methods=['POST'])
def postFeedback():
    req = get('https://api.telegram.org/bot7114465780:AAECltozhDbmqfebfryry2A4z0dL5xOF5y8/sendMessage?chat_id=468110974&parse_mode=Markdown&text=a',data=request.data)
    return req.content, req.status_code
    

if __name__ == '__main__':
    app.run()