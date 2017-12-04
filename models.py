from collegemanager import db
from flask_sqlalchemy import SQLAlchemy
import os

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __init__(self, email, password):
        self.password = password
        self.email = email
        self.created_on = datetime.now()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return (self.id)

    @classmethod
    def is_email_taken(cls, email):
        return db.session.query(db.exists().where(User.email == email)).scalar()

    def __repr__(self):
        return '<User %r>' % (self.email)

class College(db.Model):
    __tablename__ = 'college'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    schoolname = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    student_ids = db.Column(db.Integer, unique=True,)

    def __repr__(self):
        return "<schoolname: {}>".format(self.schoolname)
    # How can I make each college gave its own set of traits?


class Traits(db.Model):
    __tablename__ = 'traits'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trait_name = db.Column(db.String, unique=True)

    def __repr__(self):
        return '<User %r>' % (self.id)


class Votes(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # TODO figure out how to get the trait id
    trait_id = db.Column(db.Integer)
    # TODO figure out how to get the user id
    user_id = db.Column(db.Integer)
    # TODO get college id
    college_id = db.Column(relationship)
    # TODO make this an integer between 1 and 5
    vote = db.Column(db.Integer)

    def __repr__(self):
        return '<User %r>' % (self.id)


class College(Base):
    __tablename__ = 'college'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    users = relationship(
        'User',
        secondary='college_user_link'
    )


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    college = relationship(
        College,
        secondary='college_employee_link'
    )


class CollegeUserLink(Base):
    __tablename__ = 'college_user_link'
    college_id = Column(Integer, ForeignKey('college.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)

