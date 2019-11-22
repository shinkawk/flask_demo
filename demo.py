from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rootadmin@localhost:3306/testdb'
db = SQLAlchemy(app)

logging.basicConfig()
logging.getLogger(__name__).setLevel(logging.DEBUG)


@app.route("/")
def hello():
    return str(User.query.all())

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return 'name:'+self.username+', email:'+str(self.email)

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)