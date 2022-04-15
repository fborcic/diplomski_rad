from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

from . import db

student_choices = db.Table('choices',
        db.Column('student_application_id', db.Integer, db.ForeignKey('student_application.id'), primary_key=True),
        db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
        )


class Credentials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    limit_to_institution = db.Column(db.Integer, db.ForeignKey('institution.id'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

class StudentApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, server_default=func.now())
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    cell_number = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    pin = db.Column(db.String(128), nullable=False)

    street = db.Column(db.String(256), nullable=False)
    city = db.Column(db.String(64), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(64), nullable=False)

    dob = db.Column(db.DateTime, nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    t_shirt_size = db.Column(db.String(4), nullable=False)

    comment = db.Column(db.String(1024), nullable=True)

    institution_id = db.Column(db.Integer,
                               db.ForeignKey('institution.id'), nullable=False)
    categories = db.relationship('Category', secondary=student_choices,
            lazy='subquery', backref=db.backref('students', lazy=True))


class Representative(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)

    institution_id = db.Column(db.Integer,
                               db.ForeignKey('institution.id'), nullable=False)


institution_preferences = db.Table('preferences',
        db.Column('institution_id', db.Integer, db.ForeignKey('institution.id'), primary_key=True),
        db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
        )


class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1024), nullable=False)

    student_applications = db.relationship('StudentApplication', backref='institution', lazy=True)
    representatives = db.relationship('Representative', backref='institution', lazy=True)
    categories = db.relationship('Category', secondary=institution_preferences,
            lazy='subquery', backref=db.backref('institutions', lazy=True))


class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    choice_limit = db.Column(db.Integer, nullable=False)
    cv_required = db.Column(db.Boolean, default=False, nullable=False)
    categories = db.relationship('Category', backref='component', lazy=True)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    gender_constraint = db.Column(db.String(1), nullable=True)
    component_id = db.Column(db.Integer,
                             db.ForeignKey('component.id'), nullable=False)


db.create_all()
db.session.commit()
