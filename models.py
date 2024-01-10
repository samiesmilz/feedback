from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# create a database instance
db = SQLAlchemy()
bcrypt = Bcrypt()

# connect method


def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, autoincrement=True)
    username = db.Column(db.String(20), primary_key=True,
                         nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """ Register new user with a hashed password and return user """
        hashed = bcrypt.generate_password_hash(password)

        # a hashed pwd is a returned in a byte string - to save it, we turn it into a normal unicode string
        hashed_utf8 = hashed.decode("utf8")
        # return instace of user with username and hashed password.
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, password):
        """ Validate that the user exists and that the password is correct
         Return user if valid, else return false

        """
        # return zero or the first found user.
        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, password):
            # return user instance
            return u
        else:
            return False


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey(
        'users.username'), nullable=False)

    user = db.relationship('User', backref='feedback')
