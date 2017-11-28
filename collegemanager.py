import os
import unicodedata
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import flash
from flask import jsonify
from flask import url_for
#from datetime import datetime
from _datetime import datetime
#from _datetime import now

from flask_login import LoginManager, login_user, logout_user , current_user , login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from forms import SignupForm

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "collegedatabase.db"))

app = Flask(__name__)
app.secret_key = 'QWERTY'
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

def init_db():
    db.init_app(app)
    db.app = app
    db.create_all()

class College(db.Model):
    schoolname = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    def __repr__(self):
        return "<schoolname: {}>".format(self.schoolname)

class User(db.Model):
    #__tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)
    registered_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __init__(self, email, password):
        self.password = password
        self.email = email
        self.registered_on = datetime.now()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicodedata(self.id)

    @classmethod
    def is_email_taken(cls, email):
        return db.session.query(db.exists().where(User.email == email)).scalar()

    def __repr__(self):
        return '<User %r>' % (self.email)

# User Signup Api
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm(request.form)
    print("The request.json value is")
    print(request.json)
    if request.method == 'GET':
        return render_template('signup.html', form=form)
    if request.method == 'POST':
        if 'email' not in request.json:
            return jsonify({'email': 'must include email'})
        if 'password' not in request.json:
            return jsonify({'password': 'must include password'})
        if User.is_email_taken(request.json['email']):
            return jsonify({'email': 'This email is already taken!'}), 409
        if request.json:
            hashed_password = generate_password_hash(request.json['password'], method='sha256')
            #new_user = User(email=request.json['email'], password=hashed_password)
            new_user = User(email=form.user, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'user': 'user created successfully'}), 201
        return jsonify({'password': 'must include password',
                        'email': 'must include email'})


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        try:
            user = User(request.form['email'], request.form['password'])
            db.session.add(user)
            db.session.commit()
            flash('User successfully registered')
            return redirect(url_for('login'))
        except IntegrityError:
            flash('User not registered. Perhaps this email address has already been used')
            return redirect(url_for('register'))


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        registered_user = User.query.filter_by(email=email,password=password).first()
        if registered_user is None:
            flash('Username or Password is invalid' , 'error')
            return redirect(url_for('login'))
        login_user(registered_user)
        flash('Logged in successfully')
        return redirect(request.args.get('next') or url_for('index'))

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
