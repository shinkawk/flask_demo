from flask import Flask, jsonify, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from authlib.integrations.flask_client import OAuth
from functools import wraps

import logging

app = Flask(__name__)
app.secret_key = "super secret key"

ma = Marshmallow(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rootadmin@localhost:3306/testdb'
db = SQLAlchemy(app)

logging.basicConfig()
logging.getLogger(__name__).setLevel(logging.INFO)

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id='7IfE7HlHEqAYfgBBzNhMrwiEoVl9kTcY',
    client_secret='1PzZsweOre_cJPrrEC6k3IYyuW4ZvnsqSAahuL9ny51Q5s5r3WTUgJsKWdhaq-Uy',
    api_base_url='https://dev-wkynz3v4.auth0.com',
    access_token_url='https://dev-wkynz3v4.auth0.com/oauth/token',
    authorize_url='https://dev-wkynz3v4.auth0.com/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect("http://localhost:8080/")

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri='http://localhost:5000/callback')

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print(session)
        if 'profile' not in session:
        # Redirect to Login page here
            return redirect('/')
        return f(*args, **kwargs)

    return decorated

@app.route("/api/users", methods=['GET'])
@requires_auth
def users():
    users_schema = UserSchema(many=True)
    return jsonify(users_schema.dump(User.query.all()))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return 'name:'+self.username+', email:'+str(self.email)

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "email")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)