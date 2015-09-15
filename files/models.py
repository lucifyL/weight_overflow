from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
from sqlalchemy import Column, DateTime
from datetime import date
import time

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    pwdhash = db.Column(db.String(100))
    grouplist = db.Column(db.String(150))
    target = db.Column(db.String(10))
    timezone = db.Column(db.String(50))
    
    def __init__(self, nickname, email, password, target):
        self.nickname = nickname
        self.email = email.lower()
        self.set_password(password)
        self.grouplist = ""
        self.target = target
    
    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)


class Group(db.Model):
    __tablename__ = 'groups'
    gid = db.Column(db.Integer, primary_key = True)
    groupname = db.Column(db.String(50),unique = True)
    owner = db.Column(db.String(50),unique = True)
    members = db.Column(db.String(5000))
    waitlist = db.Column(db.String(1000))
    
    def __init__(self, groupname, owner, members):
        self.groupname = groupname
        self.owner = owner
        self.members = members
        self.waitlist = None


class Weight(db.Model):
    __tablename__ = 'weight'

    email = db.Column(db.String(50),primary_key = True, unique = True)
    weight = db.Column(db.String(10000),unique = True)
    begindate = db.Column(db.Date())
    lastupdated = db.Column(db.Date())
    groups = db.Column(db.String(1000))
    timezone = db.Column(db.String(50))
    nickname = db.Column(db.String(50))
    daysAbsent = db.Column(db.Integer)
    target = db.Column(db.String(10))
    
    def __init__(self, email,weight, begindate, lastupdated, groups, nickname, timezone, target):
        self.email = email
        self.weight = weight
        self.begindate = begindate
        self.lastupdated = lastupdated
        self.groups = groups
        self.nickname = nickname
        self.timezone = timezone
        self.daysAbsent = 0
        self.target = target


class Achieved(db.Model):
    __tablename__ = 'achieved'

    email = db.Column(db.String(50), primary_key = True)
    nickname = db.Column(db.String(100))
    begindate = db.Column(db.Date())
    enddate = db.Column(db.Date())
    beginweight = db.Column(db.String(10))
    target = db.Column(db.String(10))

    def __init__(self, email, nickname, begindate, enddate, beginweight,target):
        self.email = email
        self.nickname = nickname
        self.begindate = begindate
        self.enddate = enddate
        self.beginweight = beginweight
        self.target = target
