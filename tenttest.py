from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.db_uri
app.secret_key = config.secret_key
db = SQLAlchemy(app)
import models

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    return 'Congratulations! You successfully tried to login, but nothing happened.'

if __name__ == '__main__':
    app.run(debug=True)
