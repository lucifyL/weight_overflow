#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, SubmitField, validators, DateTimeField, ValidationError, PasswordField, SelectField
from wtforms.validators import Required, AnyOf, NoneOf
from models import db, User, Group, Weight, Achieved
from countries import countries
from flask import session
from files import app

class SignupForm(Form):
    nickname = TextField("Nickname", [validators.Required(u"Please enter the user name.（请填写用户名）")])
    target = TextField("Target", [validators.Required(u"Please enter the target weight.（请填写目标体重）")])
    email = TextField("Email",  [validators.Required(u"Please enter your email address（请填写email）."), validators.Email(u"Please enter your email address（请填写email）.")])
    password = PasswordField('New Password', [validators.Required(u"please enter your password（请填写密码）"),validators.EqualTo('confirm', message='Passwords must match（密码必须一致）')
                                              ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField("Create account")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
    
    def validate(self):
        if not Form.validate(self):
            return False
        
        try:
            float(self.target.data)
        except ValueError:
            self.target.errors.append(u"please enter the targer weight correctly（请正确填写体重）")
            return False
        
        user = User.query.filter_by(email = self.email.data.lower()).first()

        if user:
            self.email.errors.append(u"That email is already taken（该email已被注册）")
            return False
        else:
            return True

class SigninForm(Form):
    email = TextField("Email",  [validators.Required(u"Please enter your email address（请输入email）."), validators.Email(u"Please enter your email address（请输入email).")])
    password = PasswordField('Password', [validators.Required(u"Please enter a password（请输入密码）.")])
    submit = SubmitField("Sign In")
                
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
    
    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user and user.check_password(self.password.data):
            return True
        else:
            self.password.errors.append(u"Invalid e-mail or password（密码或账号错误）")
            return False

class GroupForm(Form):
    groupname = TextField("Groupname",  [validators.Required("Please enter the group name.")])
    owner = TextField("Owner")
    members = TextField("MemberList")
    submit = SubmitField("Create Group")
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        
        user = Group.query.filter_by(groupname = self.groupname.data.lower()).first()
  
        if user:
            self.groupname.errors.append("That group name is already taken")
            return False
        else:
            return True

class WeightForm(Form):
    todaysweight = TextField("TodaysWeight",[validators.Required(u"Please enter your weight today（请输入今日体重）.")])
    submit = SubmitField("submit")
    
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)




    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email = session['email'].lower()).first()

        if user.timezone == None:
            self.todaysweight.errors.append(u"please pick your timezone before enter your weight（请先修改时区，再记录体重）")
            return False
        try:
            float(self.todaysweight.data)
        except ValueError:
            self.todaysweight.errors.append(u"please enter the weight correctly（请正确填写体重）")
            return False
        
        return True

class EditForm(Form):
    nickname = TextField("Nickname")
    target = TextField("Target")
    submit = SubmitField("edit")
    timezoneinfo = []
    for ele in countries:
        timezoneinfo.append((ele['timezones'][0],ele['timezones'][0]))
    result = [(('default'),('default'))]+ [(('Asia/Shanghai'),('北京时间'))]+sorted(timezoneinfo)

    timezone = SelectField('timezone',choices=result)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
    
    def validate(self):
        if not Form.validate(self):
            return False
        if self.target.data != "":
            try:
                float(self.target.data)
            except ValueError:
                self.target.errors.append(u"please enter the targer weight correctly（请正确填写体重）")
                return False

        return True

class UserProgressForm(Form):

    submit = SubmitField("submit")
    
    result = [((7),(u"week（一周）")),((30),(u"month（一个月）")),(("max"),(u"max（最大时间）"))]


    days = SelectField('days',choices = result)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):

        return True

class GroupChoiceForm(Form):
    submit = SubmitField("submit")
    choose = [((7),(u"week（一周）")),((14),(u"2 weeks（2周）")),((30),(u"month（一月）")),((60),(u"2 month（2月）")),(("max"),(u"after you started（你加入之后）")),(("all"),(u"all（查看所有）"))]
    select  = SelectField('choice',choices = choose)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
    
    def validate(self):
        
        return True

class QuitGroup(Form):
    submit = SubmitField("submit")
    groupname = TextField("groupname")


    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

