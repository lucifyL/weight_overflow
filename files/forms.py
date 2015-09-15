from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, SubmitField, validators, DateTimeField, ValidationError, PasswordField, SelectField
from wtforms.validators import Required, AnyOf, NoneOf
from models import db, User, Group, Weight, Achieved
from countries import countries
from flask import session
from files import app

class SignupForm(Form):
    nickname = TextField("Nickname", [validators.Required("Please enter the user name.")])
    target = TextField("Target", [validators.Required("Please enter the target weight.")])
    
    timezoneinfo = []
    for ele in countries:
        timezoneinfo.append((ele['timezones'][0],ele['timezones'][0]))
    timezone = SelectField('timezone',choices=sorted(timezoneinfo))

    email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
    password = PasswordField('New Password', [validators.Required("please enter your password"),validators.EqualTo('confirm', message='Passwords must match')
                                              ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField("Create account")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
    
    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()

        if user:
            self.email.errors.append("That email is already taken")
            return False
        else:
            return True

class SigninForm(Form):
    email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
    password = PasswordField('Password', [validators.Required("Please enter a password.")])
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
            self.password.errors.append("Invalid e-mail or password")
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
    todaysweight = TextField("TodaysWeight")
    submit = SubmitField("submit")
    
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)




    def validate(self):
        if not Form.validate(self):
            return False

        user = Weight.query.filter_by(email = session['email'].lower()).first()

        if not user and self.timezone.data == "default":
            self.todaysweight.errors.append("please pick your timezone before enter your weight")
            return False
        try:
            float(self.todaysweight.data)
        except ValueError:
            self.todaysweight.errors.append("please enter the weight correctly")
            return False
        
        return True

class EditForm(Form):
    nickname = TextField("Nickname")
    target = TextField("Target")
    submit = SubmitField("edit")
    timezoneinfo = []
    for ele in countries:
        timezoneinfo.append((ele['timezones'][0],ele['timezones'][0]))
    result = [(('default'),('default'))]+sorted(timezoneinfo)

    timezone = SelectField('timezone',choices=result)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
    
    def validate(self):
        if not Form.validate(self):
            return False
        try:
            float(self.target.data)
        except ValueError:
            self.target.errors.append("please enter the targer weight correctly")
            return False

        return True

class UserProgressForm(Form):

    submit = SubmitField("submit")
    with app.app_context():
        Weight.query.filter_by(email = session['email'].lower()).first()

    
    
    
    daysUsing = 9
    result = []
    for i in range(2, daysUsing):
        
        result.append((str(i),str(i)))

    
    
    days = SelectField('days',choices = result)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
       
        weight = Weight.query.filter_by(email = session['email'].lower()).first()

        if not Form.validate(self):
            return False
        return True


