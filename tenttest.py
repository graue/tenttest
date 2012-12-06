from flask import Flask, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.db_uri
app.secret_key = config.secret_key
db = SQLAlchemy(app)
import models

from tentapp import TentApp

app_details = {
    'name': 'TentTest',
    'description': 'A test client by scott.mn',
    'url': 'https://scott.mn',
    'oauthCallbackURL': 'http://test.scott.mn:5000/oauth-callback',
    'postNotificationUrl': None,
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    tent = TentApp(request.form['entity'])
    real_entity = tent.entityUrl  # may differ from entity in form
    return 'If this were implemented you would be logging in as {0}'.format(real_entity)

if __name__ == '__main__':
    app.run(debug=True)
