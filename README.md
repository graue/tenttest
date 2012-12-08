Minimal web app that implements the [Tent protocol](https://tent.io)'s auth flow, relying on [python-tent-client](https://github.com/longears/python-tent-client). Written in [Flask](http://flask.pocoo.org) with [Flask-SQLAlchemy](http://packages.python.org/Flask-SQLAlchemy/).

What does it do?
---------------------

Not much. You can log in, see an ugly unstyled list of recent status posts in your feed, and log out.

I wrote this for practice understanding the auth process; it will only be of interest to developers.

Install notes
---------------

This is basically installed the same way as any other Flask app, so see its docs, but you will need to create the database. In Python's interactive shell:

```python
from tenttest import db
db.create_all()
```

Also, you need to make sure `oauthCallbackURL` in the code points to the right place (hopefully localhost, as you wouldn't be deploying a test app publicly, right?). The trick I used was to reference `test.scott.mn` which doesn't actually exist, and then add that to my hosts file as 127.0.0.1.

Finally, copy config_sample.py to config.py and replace the secret key.

How does it work?
-----------------------

When someone goes to the web app, puts in `http://entity.tld` and clicks Sign In, the app:

1. Checks its local database to see if it already has app registration details for `http://entity.tld`.

2. If not, it registers itself with the server for `http://entity.tld` and gets a client ID (6 alphanumeric characters in tentd's implementation), MAC key ID (of the form `a:` followed by 8 hex digits in tentd's implementation), and MAC key. This happens without the owner of `http://entity.tld` needing to approve the registration or even be signed in.

3. The app builds a URL for an auth request (which, to identify the app, contains the Tent-server-provided client ID), and redirects the user trying to sign in to that URL.

4. The user is required to sign in to the Tent server for `http://entity.tld`, if not already signed in.

5. If the user has not used this app before, or if the app is requesting new permissions since last time the app is used, the user is shown a list of permissions the app wants and asked whether to grant or decline. 

6. The user is redirected to the app's callback with a `code` parameter
(32 hex digits in tentd's implementation).

7. The app posts this code at `/apps/:id/authorizations` on the server for
`http://entity.tld`. In return, the server provides a MAC key ID (of the
form `u:` followed by 8 hex digits in tentd's implementation) and MAC
key. The app can now use this key and ID to interact with the Tent
server on the user's behalf.

While a client running as a native app could use the credentials granted in step 7 indefinitely, a web app must repeat steps 3-7 for every session, because only the successful completion of step 7 proves that the user signing in owns the entity.

Therefore, this app uses an SQLite database that stores only the following information:

1. the entity of each user who has signed in,
2. `app_id` for the app registration on that user's server (step 2),
3. the registration MAC key (step 2),
4. the registration MAC key ID (step 2).

The following is stored per-session (which Flask implements as a cryptographically signed cookie on the user's browser):

1. the user's entity, to remind the web app which user we are dealing with in subsequent requests,
2. `state`, set in step 3 and cleared in step 6, to prevent cross-site request forgery (see [the docs](https://tent.io/docs/app-auth#auth-request)),
3. the MAC key returned in step 7 (`mac_key`),
4. the MAC key ID returned in step 7 (`access_token`).

To implement logging out, the entity, key and key ID are cleared from the browser's cookies.

Contact
----------

I'm [scott.mn](https://scott.mn) on Tent.