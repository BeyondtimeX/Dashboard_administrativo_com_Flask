# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from sqlalchemy.orm import relationship
from config import app_active, app_config
from passlib.hash import pbkdf2_sha256
from flask_login import UserMixin

config = app_config[app_active]
manager = None

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_name)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    
    return app

db = SQLAlchemy()
migrate = Migrate()

app = create_app(config)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)

    def __repr__(self):
        return self.name

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    last_update = db.Column(db.DateTime, onupdate=db.func.current_timestamp(), nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = relationship('Role', backref='users')

    def __repr__(self):
        return '%s - %s' % (self.id, self.username)

    def set_password(self, password):
        self.password = pbkdf2_sha256.hash(password)

    def verify_password(self, password_no_hash):
        return pbkdf2_sha256.verify(password_no_hash, self.password)

class State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)

    def __repr__(self):
        return self.name

class DiseaseState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)

    def __repr__(self):
        return self.name

disease_patient = db.Table('disease_patient',
    db.Column('disease_id', db.Integer, db.ForeignKey('disease.id')),
    db.Column('patient_id', db.Integer, db.ForeignKey('patient.id'))
)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'), nullable=False)
    disease_state_id = db.Column(db.Integer, db.ForeignKey('disease_state.id'), nullable=False)
    last_state_update = db.Column(db.DateTime, onupdate=db.func.current_timestamp(), nullable=True)
    state = relationship('State', backref='patients')
    disease_state = relationship('DiseaseState', backref='patients')
    diseases = db.relationship('Disease', secondary=disease_patient, backref=db.backref('patients', lazy='dynamic'))

    def __repr__(self):
        return self.name

class Disease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)

    def __repr__(self):
        return self.name

if __name__ == '__main__':
    manager.run()
