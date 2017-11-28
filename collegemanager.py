import os

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import flash
from flask import url_for

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "collegedatabase.db"))

app = Flask(__name__)
app.secret_key = 'QWERTY'
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

"""
if college is (already in the database):
    flash("This college is already in the database")
"""

class College(db.Model):
    schoolname = db.Column(db.String(80, collation='NOCASE'), unique=True, nullable=False, primary_key=True)
    def __repr__(self):
        return "<schoolname: {}>".format(self.schoolname)



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
    app.run(debug=True)
