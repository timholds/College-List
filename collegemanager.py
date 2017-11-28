import os

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import flash
from flask import jsonify
from flask import url_for

from forms import SignupForm
#from models import db

#from flask_restful import resource

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

from werkzeug.security import generate_password_hash, check_password_hash

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "collegedatabase.db"))

app = Flask(__name__)
app.secret_key = 'QWERTY'
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

def init_db():
    db.init_app(app)
    db.app = app
    db.create_all()

class College(db.Model):
    schoolname = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    def __repr__(self):
        return "<schoolname: {}>".format(self.schoolname)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    #tasks = db.relationship('Task', backref='author', lazy='dynamic')

    @classmethod
    def is_user_name_taken(cls, username):
        return db.session.query(db.exists().where(User.username == username)).scalar()

    @classmethod
    def is_email_taken(cls, email):
        return db.session.query(db.exists().where(User.email == email)).scalar()

    def __repr__(self):
        return '<User %r>' % (self.username)


"""
# User Signup Api
@app.route('/api/v1/signup', methods=['POST'])
def signup():
    if 'username' not in request.json:
        return jsonify({'username': 'must include username'})
    if 'email' not in request.json:
        return jsonify({'email': 'must include email'})
    if 'password' not in request.json:
        return jsonify({'password': 'must include password'})

    if User.is_user_name_taken(request.json['username']):
        return jsonify({'username': 'This username is already taken!'}), 409
    if User.is_email_taken(request.json['email']):
        return jsonify({'email': 'This email is already taken!'}), 409

    if request.json:
        hashed_password = generate_password_hash(request.json['password'], method='sha256')
        new_user = User(username=request.json['username'], email=request.json['email'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'user': 'user created successfully'}), 201
    return jsonify({'username': 'must include username',
                    'password': 'must include password',
                    'email': 'must include email'})
"""

# User Signup Api try #2
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm(request.form)
    if request.method == 'GET':
        return render_template('signup.html', form = form)
    elif request.method == 'POST':
        try:
            email = User(email=request.form.get("email"))
            password = User(password=request.form.get("password"))
            hashed_password = generate_password_hash(password, method='sha256')
            new_user = User(email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
        except (TypeError, SQLAlchemyError):
            flash("Failed to sign up user")
            print("Failed")
            return redirect(url_for('signup'))
        """
        if form.validate_on_submit():
            if User.query.filter_by(email = email) != None:
                print('User Exists')
            else:
                return "will create user here"
        else:
            return "Form didn't validate"
        """

"""
# User Signup API try #3
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.email.data,
                    form.hased_password.data)
        db.add(user)
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
"""

@app.route('/', methods=["GET", "POST"])
@app.route('/home', methods=["GET", "POST"])
def home():
    colleges = None
    if request.form:
        try:
            #db.session.query(College).delete()
            college = College(schoolname=request.form.get("schoolname"))
            db.session.add(college)
            db.session.commit()
        except SQLAlchemyError:
            flash("Failed to add college, as it might be a duplicate")
            return redirect(url_for('home'))

    colleges = College.query.all()
    return render_template("home.html", colleges=colleges)

@app.route("/update", methods=["POST"])
def update():
    try:
        newschoolname = request.form.get("newschoolname")
        oldschoolname = request.form.get("oldschoolname")
        college = College.query.filter_by(schoolname=oldschoolname).first()
        college.schoolname = newschoolname
        db.session.commit()
    except Exception as e:
        print("Couldn't update college schoolname")
        print(e)
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    schoolname = request.form.get("schoolname")
    college = College.query.filter_by(schoolname=schoolname).first()
    db.session.delete(college)
    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    #app.init_db()
    app.run(port=5000, host='localhost', debug=True)
