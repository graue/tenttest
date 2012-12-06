from tenttest import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entity = db.Column(db.String(256), unique=True)
    app_id = db.Column(db.String(16))  # 6 chars on tentd
    registration_mac_key = db.Column(db.String(32))
    registration_mac_key_id = db.Column(db.String(16))  # 10 chars on tentd
