from flask import Flask, render_template, request, flash, session, redirect, url_for
from forms import SignupForm, SigninForm, GroupForm, WeightForm
from files import app
from models import db, User, Group, Weight
from sqlalchemy import func
from datetime import datetime, date, timedelta
import pytz
import matplotlib.pyplot as plt
import random


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'email' in session:
        return redirect(url_for('profile'))
    form = SignupForm()
        
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('register.html', form=form)
        else:
            newuser = User(form.nickname.data, form.email.data, form.password.data)
            db.session.add(newuser)
            db.session.commit()
            session['email'] = newuser.email
            return redirect(url_for('profile'))
    elif request.method == 'GET':
        return render_template('register.html', form=form)

@app.route('/profile', methods=['GET','POST'])
def profile():
    if 'email' not in session:
        return redirect(url_for('signin'))
    if request.method == 'GET':
        user = User.query.filter_by(email = session['email']).first()
        if user is None:
            return redirect(url_for('signin'))
        else:
            groupnameList = []
            groupInfo = Group.query.filter_by(owner=session['email']).all()
            if groupInfo is not None:
                for ele in groupInfo:
                    groupnameList.append(ele.groupname)
            if user.grouplist != "":
                grouplist = user.grouplist.split(",")
            else:
                grouplist = ""
    return render_template('profile.html',nickname = user.nickname,email = user.email,groupnameList = groupnameList, grouplist=grouplist)

@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'email' in session:
        return redirect(url_for('profile'))
    form = SigninForm()
        
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('index.html', form=form)
        else:
            session['email'] = form.email.data
            return redirect(url_for('profile'))
                
    elif request.method == 'GET':
        return render_template('index.html', form=form)

@app.route('/signout')
def signout():
    
    if 'email' not in session:
        return redirect(url_for('signin'))
        
    session.pop('email', None)
    return redirect(url_for('index'))


@app.route('/creategroup', methods=['GET', 'POST'])
def creategroup():
    form = GroupForm()
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('creategroup.html', form=form)
        else:
            newgroup = Group(form.groupname.data, session['email'],session['email'])
            db.session.add(newgroup)
            db.session.commit()
            user = User.query.filter_by(email = session['email']).first()
            if user.grouplist == None or user.grouplist == "":
                user.grouplist = form.groupname.data
            else:
                user.grouplist += "," + form.groupname.data
            db.session.commit()
            return redirect(url_for('index'))


    elif request.method == 'GET':
        return render_template('creategroup.html', form=form)


@app.route('/joingroup', methods=['GET','POST'])
def joingroup():
    if request.method == "GET":
        choice = ""
        user = User.query.filter_by(email = session['email']).first()
        groups = Group.query.all()
        empty = False
        if len(groups) == 0:
            empty = True
        return render_template('joingroup.html',groups=groups, empty=empty,nickname=user.nickname,choice=choice)
    elif request.method == "POST":
        return str(len(request.form.keys()))

@app.route('/joined/<groupname>')
def joined(groupname):
    user = session['email']
    group = Group.query.filter_by(groupname=groupname).first()
    members = group.members
    inlist = False
    namelist = members.split(",")
    waitlist = ""
    if group.waitlist != None:
        waitlist = group.waitlist.split(",")
    if user in namelist or user in waitlist:
        inlist = True
    elif group.waitlist != None:
        group.waitlist = group.waitlist + "," + session['email']
        db.session.commit()
    else:
        group.waitlist = session['email']
        db.session.commit()
    
    return render_template('joined.html',groupname=groupname,members = members,inlist=inlist)


@app.route('/modify/<groupname>')
def modify(groupname):
    if len(groupname.split(',')) == 1:
        group = Group.query.filter_by(groupname=groupname).first()
        return render_template('modify.html',group=group,session=session)
    ##kick##
    elif len(groupname.split(',')) == 2:
        person = groupname.split(',')[0]
        groupname = groupname.split(',')[1]
        ##remove from members list##
        group = Group.query.filter_by(groupname=groupname).first()
        temp = group.members.split(',')
        temp.remove(person)
        group.members = ','.join(temp)
        ##remvoe from grouplist##
        user = User.query.filter_by(email = person).first()
        temp = user.grouplist.split(',')
        temp.remove(groupname)
        user.grouplist = ','.join(temp)
        db.session.commit()
        return render_template('modify.html',group=group,session=session)


    ##approve or deny##
    elif len(groupname.split(',')) == 3:
        person = groupname.split(',')[0]
        result = groupname.split(',')[1]
        groupname = groupname.split(',')[2]
        group = Group.query.filter_by(groupname=groupname).first()
        temp = group.waitlist.split(',')
        temp.remove(person)
        if temp != None and temp != []:
            group.waitlist = ','.join(temp)
        else:
            group.waitlist = None
        db.session.commit()
        if result == "approved":
            group.members = group.members + "," + person
            user = User.query.filter_by(email = person).first()
            if user.grouplist == None or user.grouplist == "":
                user.grouplist = groupname
            else:
                user.grouplist += "," + groupname
            db.session.commit()
        return render_template('modify.html',group=group,session=session)

@app.route('/groupinfo/<groupname>', methods=['GET','POST'])
def groupinfo(groupname):
    
    group = Group.query.filter_by(groupname=groupname).first()
    members = group.members.split(',')
    user = User.query.filter_by(email = session['email']).first()
    nickname = user.nickname
    groupWeightInfo = []
    form = WeightForm(request.form)
    
    if request.method == "POST":
        if form.validate():
            user = Weight.query.filter_by(email = session['email']).first()
            if user == None:
                grouplist = User.query.filter_by(email = session['email']).first().grouplist
                newWeight = Weight(session['email'],form.todaysweight.data,datetime.now(pytz.timezone(form.timezone.data)).date(),datetime.now(pytz.timezone(form.timezone.data)).date(),grouplist, nickname, form.timezone.data)
                db.session.add(newWeight)
                db.session.commit()
            if user != None:
                #days that this ppl is not recording the weight info
                dateDifference = (datetime.now(pytz.timezone(user.timezone)).date() - user.lastupdated).days
                
                #check if user have already entered today's weight
                exist = False
                if user.lastupdated == datetime.now(pytz.timezone(user.timezone)).date():
                    exist = True
                #check if user want to change their time zone info
                if form.timezone.data == 'default':
                    user.lastupdated = datetime.now(pytz.timezone(user.timezone)).date()
                else:
                    user.lastupdated = datetime.now(pytz.timezone(form.timezone.data)).date()
                    user.timezone = form.timezone.data
                
                if exist:
                    temp = user.weight.split(',')
                    temp.pop()
                    temp.append(form.todaysweight.data)
                    user.weight = ','.join(temp)
                else:
                    last = int(user.weight.split(",")[-1])
                    now = int(form.todaysweight.data)
                    differenceEachDay = (now - last)/dateDifference
                    for i in range(1,dateDifference):
                        user.weight += "," + str(i * differenceEachDay + last)
                    user.weight += "," + form.todaysweight.data
                db.session.commit()

                lasttime = user.lastupdated
                today = datetime.now(pytz.timezone(user.timezone)).date()




    for ele in members:
        weight = Weight.query.filter_by(email=ele).first()
        if weight is not None:
            info = []
            info.append(weight.nickname)
            info.append(weight.begindate)
            info.append(weight.weight.split(",")[0])
            info.append(weight.lastupdated)
            info.append(weight.weight.split(",")[-1])
            lossPercentage = (float(weight.weight.split(",")[0]) - float(weight.weight.split(",")[-1]))/float(weight.weight.split(",")[0])*100
            info.append(lossPercentage)
            groupWeightInfo.append(info)





    def rn():
        return random.random() * 2
    base = 0

    ppl1 = []
    ppl2 = []
    ppl3 = []
    ppl4 = []
    ppl5 = []
    x = []
    for i in range(1,10):
    
        base += rn()
        ppl1.append(base)

    base = 0
    for i in range(1,10):
    
        base += rn()
        ppl2.append(base)

    base = 0
    for i in range(1,10):
    
        base += rn()
        ppl3.append(base)

    base = 0
    for i in range(1,10):
    
        base += rn()
        ppl4.append(base)

    base = 0
    for i in range(1,10):
    
        base += rn()
        ppl5.append(base)

    for i in range(1,10):
       x.append(i)

    for i in range (0, len(ppl1)):
        plt.plot(x[i], ppl1[i], linestyle="None", marker="o", markersize=10, color="red")
        plt.plot(x[i], ppl2[i], linestyle="None", marker="o", markersize=8, color="blue")
        plt.plot(x[i], ppl3[i], linestyle="None", marker="o", markersize=8, color="green")
        plt.plot(x[i], ppl4[i], linestyle="None", marker="o", markersize=8, color="brown")
        plt.plot(x[i], ppl5[i], linestyle="None", marker="o", markersize=8, color="purple")

    plt.plot(x, ppl1, linestyle="-", color="red", linewidth = 3 , label = 'ppl1')
    plt.plot(x, ppl2, linestyle="solid", color="blue", linewidth = 3 , label = 'ppl2')
    plt.plot(x, ppl3, linestyle="solid", color="green", linewidth = 3 , label = 'ppl3')
    plt.plot(x, ppl4, linestyle="solid", color="brown", linewidth = 3 , label = 'ppl4')
    plt.plot(x, ppl5, linestyle="solid", color="purple", linewidth = 3 , label = 'ppl5')
    plt.legend(loc='best')

    picture = plt.figure()


    return render_template('groupinfo.html',groupname = groupname, groupWeightInfo = groupWeightInfo, nickname = nickname,form=form, picture = picture)


































