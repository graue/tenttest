import time
from flask import Flask, render_template, request, redirect, session, url_for
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
    'icon': None,
}

class MyTentApp(TentApp):
    def populate_keys_from_db(self):
        user = models.User.query.filter_by(entity=self.entityUrl).first()
        if user is not None:
            self.keys['appID'] = user.app_id
            self.keys['registration_mac_key'] = user.registration_mac_key
            self.keys['registration_mac_key_id'] = user.registration_mac_key_id
        else:
            self.keys['appID'] = None
        self.user = user

    def __init__(self, entity_url):
        TentApp.__init__(self, entity_url)
        self.appDetails = app_details
        self.populate_keys_from_db()

    def register(self):
        TentApp.register(self)

        # update old registration details, if they exist in the DB
        if self.user is not None:
            self.user.app_id = self.keys['appID']
            self.user.registration_mac_key = self.keys['registration_mac_key']
            self.user.registration_mac_key_id = \
                self.keys['registration_mac_key_id']
        else:
            self.user = models.User(self.entityUrl, self.keys['appID'],
                                    self.keys['registration_mac_key'],
                                    self.keys['registration_mac_key_id'])
            db.session.add(self.user)
        db.session.commit()


@app.route('/')
def index():
    if 'key' in session:  # logged in
        return redirect(url_for('dashboard'), 303)

    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    tent = MyTentApp(request.form['entity'])

    # register app if not already registered
    if tent.keys['appID'] is None:
        tent.register()

    # registered with server, now do oauth
    approve_url = tent.getUserApprovalURL()  # sets tent.keys['state']
    session['entity'] = tent.entityUrl
    session['state'] = tent.keys['state']
    return redirect(approve_url, 303)


@app.route('/oauth-callback', methods=['GET'])
def callback():
    if 'error' in request.args:
        # XXX: may need more protection against XSRF attacks here
        if 'state' not in session or 'entity' not in session:
            return "Something weird happened. Login failed, but you " +\
                   "weren't trying to log in.", 403

        # assume the app registration credentials have been revoked,
        # so re-register
        # XXX: if this doesn't fix the error, it could cause a redirect loop
        tent = MyTentApp(session['entity'])
        tent.register()  # re-register with new app ID, etc.
        approve_url = tent.getUserApprovalURL()  # sets tent.keys['state']
        session['state'] = tent.keys['state']
        return redirect(approve_url, 303)

    if session['state'] != request.args['state']:
        return "Error: State doesn't match", 403
    tent = MyTentApp(session['entity'])
    tent.getPermanentKeys(request.args['code'])
    session['key'] = tent.keys['permanent_mac_key']
    session['key_id'] = tent.keys['permanent_mac_key_id']
    session.pop('state', None)  # state no longer needed
    return redirect(url_for('dashboard'), 303)


@app.route('/dashboard')
def dashboard():
    if 'key' not in session:  # logged out, why are you here?
        return redirect(url_for('index'), 303)

    tent = MyTentApp(session['entity'])
    tent.keys['permanent_mac_key'] = session['key']
    tent.keys['permanent_mac_key_id'] = session['key_id']

    posts = tent.getPosts(post_types='https://tent.io/types/post/status/v0.1.0')
    for post in posts:
        post['timestamp'] = time.asctime(time.localtime(post['published_at']))
    return render_template('dashboard.html', entity=tent.entityUrl,
                           posts=posts)


@app.route('/logout')
def logout():
    session.pop('entity', None)
    session.pop('key', None)
    session.pop('key_id', None)
    return redirect(url_for('index'), 303)


if __name__ == '__main__':
    app.run(debug=True)
