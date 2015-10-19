#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, flash, session, redirect, url_for
from forms import SignupForm, SigninForm, GroupForm, WeightForm, EditForm, UserProgressForm, GroupChoiceForm, QuitGroup
from files import app
from models import db, User, Group, Weight, Achieved
from sqlalchemy import func
from datetime import datetime, date, timedelta
import pytz
import matplotlib.pyplot as plt
import os,os.path
import numpy as np
from operator import itemgetter
from collections import OrderedDict
import matplotlib
from matplotlib.font_manager import FontProperties
import matplotlib.font_manager as fm
prop = fm.FontProperties(fname='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'email' in session:
        return redirect(url_for('profile'))
    form = SignupForm()
        
    if request.method == 'POST':
        
        if form.validate() == False:
            return render_template('register.html', form=form)
        else:
            newuser = User(form.nickname.data, form.email.data, form.password.data, form.target.data)
            db.session.add(newuser)
            db.session.commit()
            session['email'] = newuser.email
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('register.html', form=form)

@app.route('/')
def homepage():
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET','POST'])
def profile():
    if 'email' not in session:
        return redirect(url_for('index'))
    groupnameList = []
    grouplist = []
    user = User.query.filter_by(email = session['email']).first()
    nickname = user.nickname
    if user is None:
        return redirect(url_for('index'))
    else:
        groupInfo = Group.query.filter_by(owner=session['email']).all()
        if groupInfo is not None:
            for ele in groupInfo:
                groupnameList.append(ele.groupname)
        if user.grouplist != "":
            grouplist = user.grouplist.split(",")

    number = [""]

    def makePicture(length):
        weight = Weight.query.filter_by(email = session['email']).first()
        if weight is not None:
            daysFromLast = (datetime.now(pytz.timezone(weight.timezone)).date() - weight.lastupdated).days
            weightarray = weight.weight.split(",")
            recordarray = []
            day = []
            labels = []
            reduce = (length / 30) + 1
            plt.figure(figsize=(12, 4))
            if length - daysFromLast > 1:
                for i in range(0, daysFromLast):
                    recordarray.append(None)
                for i in range(0, length - daysFromLast):
                    if len(weightarray) > 0:
                        recordarray.append(float(weightarray.pop()))
                    else:
                        recordarray.append(None)
                recordarray.reverse()
                
                def getfirst(array):
                    for ele in array:
                        if ele != None:
                            return ele
                def getlast(array):
                    array.reverse()
                    return getfirst(array)
                
                number[1] = getfirst(recordarray)
                number[2] = getlast(recordarray)
                recordarray.reverse()
                for i in range(0, length):
                    
                    day.append(i)
                    if reduce == 0 or i%reduce == 0:
                        labels.append(str(datetime.now(pytz.timezone(weight.timezone)).date() - timedelta(i)))
                labels.reverse()
                for i in range(0, length):
                    plt.plot(day[i],recordarray[i], linestyle="None",marker = "o", markersize = 8, color = "green")
                    #zhfont1 = matplotlib.font_manager.FontProperties(fname='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc')
	            plt.plot(day, recordarray, linestyle="solid",color="#2BCE48",linewidth=3,label=unicode(weight.nickname) if i ==0 else "")
                plt.legend(loc='best',prop=prop)
                file = "/var/www/weight_overflow/files/static/weightgram/users/" + nickname
                plt.xticks(day, labels, rotation=45)
                plt.subplots_adjust(bottom=0.30)
                if reduce != 0:
                    plt.xticks(np.arange(min(day), max(day)+1, reduce))
                if os.path.exists(file):
                    filenumber = int(os.listdir(file)[0].split(".")[0][1:])
                    filenumber += 1
                    number[0] = str(filenumber)
                    os.remove(file + "/w" + str(filenumber - 1) + ".png")
                    plt.savefig(file + "/w" + str(filenumber) + ".png")
                else:
                    os.mkdir(file)
                    plt.savefig(file + "/w0.png")
                    number[0] = "0"
                plt.clf()
                return True
            else:
                return False
        return False

    warn = ""
    form = EditForm(prefix = "form")
    form1 = WeightForm(prefix = "form1")
    form2 = UserProgressForm(prefix = "form2")
    newuser = False
    timezoneRecorded = False
    message = ""
    weight = Weight.query.filter_by(email = session['email']).first()
    if weight != None:
        if len(weight.weight.split(",")) == 1:
            newuser = True
    else:
        newuser = True
    if user.timezone != None:
        timezoneRecorded = True


    if request.method == 'POST':
                #for weight form

        if form1.submit.data and form1.validate():

            user = Weight.query.filter_by(email = session['email']).first()
            
            if user == None:
                currentUser = User.query.filter_by(email = session['email']).first()
                grouplist = User.query.filter_by(email = session['email']).first().grouplist
                newWeight = Weight(session['email'],form1.todaysweight.data,datetime.now(pytz.timezone(currentUser.timezone)).date(),datetime.now(pytz.timezone(currentUser.timezone)).date(),grouplist, nickname, currentUser.timezone, currentUser.target)
                db.session.add(newWeight)
                db.session.commit()
            
            if user != None:
                if (datetime.now(pytz.timezone(user.timezone)).date() - user.lastupdated).days == -1:
                    
                    weight = Weight.query.filter_by(email = session['email']).first()
                    if user.begindate == user.lastupdated:
                        weight.begindate = datetime.now(pytz.timezone(user.timezone)).date()
                        weight.weight = form1.todaysweight.data
                    else:
                        temp = weight.weight.split(",")
                        temp[-2] = form1.todaysweight.data
                        temp.pop()
                        weight.weight = ','.join(temp)
                        weight.daysAbsent = weight.daysAbsent - 1
                    
                    weight.lastupdated = datetime.now(pytz.timezone(user.timezone)).date()
                    db.session.commit()
                else:
                
                
                
                
                
                
                    #first day recording, if it's not the first day, go to else
                    temp = (datetime.now(pytz.timezone(user.timezone)).date() - user.lastupdated).days
                    if temp > 0:
                        user.daysAbsent = temp
                    if user.daysAbsent == 0:
                        user.weight = "%.2f"%(float(form1.todaysweight.data))
                    #after first day
                    else:
                        #days that this ppl is not recording the weight info, this will remain the same if
                        #ppl try to modify today's weight.
                        #check if user have already entered today's weight
                        exist = False
                        if user.lastupdated == datetime.now(pytz.timezone(user.timezone)).date():
                            exist = True
                        else:
                            user.lastupdated = datetime.now(pytz.timezone(user.timezone)).date()
                        #delete data back to last recorded time
                        if exist:
                            temp = user.weight.split(',')
                            for i in range(0,user.daysAbsent):
                                temp.pop()
                            user.weight = ','.join(temp)
                        #add data back to database
                        last = float(user.weight.split(",")[-1])
                        now = float(form1.todaysweight.data)
                        differenceEachDay = (now - last)/user.daysAbsent
                        for i in range(1,user.daysAbsent):
                            user.weight += "," + "%.2f"%(i * differenceEachDay + last)
                        user.weight += "," + "%.2f"%(float(form1.todaysweight.data))
                db.session.commit()
            #put user's information into achieve table if they achieve their target weight
            user = Weight.query.filter_by(email = session['email']).first()
            if user.target is not None:
                achieved = Achieved.query.filter_by(email = session['email']).first()
                begin = float(user.weight.split(",")[0])
                target = float(user.target)
                #requirement to be recorded: not in the least, reached the target, loss more than 10% of ur body weight
            if float(user.weight.split(",")[-1]) <= target and achieved == None and begin - target >= begin * 0.1:
                grats = Achieved(user.email, user.nickname, user.begindate,user.lastupdated,user.weight.split(",")[0],user.target)
                db.session.add(grats)
                db.session.commit()
            return redirect(url_for('profile'))

        #for edit form
        if form.submit.data and form.validate():
            weight = Weight.query.filter_by(email = session['email']).first()
            user = User.query.filter_by(email = session['email']).first()
            if form.nickname.data != '':
                if weight is not None:
                    weight.nickname = form.nickname.data
                user.nickname = form.nickname.data
            try:
                float(form.target.data)
                if weight is not None:
                    weight.target = form.target.data
                user.target = form.target.data
            except ValueError:
                pass
            if form.timezone.data != "default":
                user.timezone = form.timezone.data
                if weight is not None:
                    weight.timezone = form.timezone.data
            db.session.commit()
            return redirect(url_for('profile'))


        #for user process tracking form

        if form2.submit.data and form2.validate():
            
            number = ["filenumber","startweight","finishweight"]
            if form2.days.data in ["7","30"]:
                
                if makePicture(int(form2.days.data)) == True:

                    loss = number[1] - number[2]
                    if loss < 0:
                        message = "Seriously? are you really try to lose weight?"
                    else:
                        message = "You lose " + "%.2f"%(loss) + " Kg in " + form2.days.data + " days"

                    number = number[0]
                else:
                    number = [""]
                    warn = "Did you at least record twice during those days?"
            elif form2.days.data == "max":
                weight = Weight.query.filter_by(email = session['email']).first()
                days = (datetime.now(pytz.timezone(weight.timezone)).date() - weight.begindate).days + 1
                makePicture(days)
                
                loss = number[1] - number[2]
                if loss < 0:
                    message = "Seriously? are you really try to lose weight?"
                else:
                    
                    message = "You lose " + "%.2f"%(loss) + " Kg in " + str(len((Weight.query.filter_by(email = session['email']).first()).weight.split(","))) + " days"
                number = number[0]

    return render_template('profile.html',nickname = user.nickname,email = user.email,groupnameList = groupnameList, grouplist=grouplist, form = form, form1 = form1, form2 = form2, number = number, newuser = newuser, timezoneRecorded = timezoneRecorded, message = message, warn = warn)



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
            return render_template('creategroup.html', form=form, session = session)
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
        user = User.query.filter_by(email = session['email']).first()
        groups = Group.query.all()
        empty = False
        if len(groups) == 0:
            empty = True
        return render_template('joingroup.html',groups=groups, empty=empty,nickname=user.nickname)
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
    user = User.query.filter_by(email = session['email']).first()
    users = User.query
    nickname = user.nickname
    if len(groupname.split(',')) == 1:
        group = Group.query.filter_by(groupname=groupname).first()
        return render_template('modify.html',group=group,session=session, nickname = nickname,users = users)
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
#        #remove from weight gram
#        weight = Weight.query.filter_by(email = person).first()
#        temp = weight.groups.split(',')
#        temp.remove(groupname)
#        weight.groups = ','.join(temp)
        db.session.commit()
        return render_template('modify.html',group=group,session=session, nickname = nickname, users = users)


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
        return render_template('modify.html',group=group,session=session,users = users, nickname = nickname)

@app.route('/groupinfo/<groupname>', methods=['GET','POST'])
def groupinfo(groupname):
    
    number = ""
    group = Group.query.filter_by(groupname=groupname).first()
    members = group.members.split(',')
    user = User.query.filter_by(email = session['email']).first()
    nickname = user.nickname
    form = GroupChoiceForm()
    form1 = QuitGroup()



    groupTotalInfo = []
    groupPartalInfo = []
    graphic = []
    timeArray = []
    number = [""]
    achieve = []
    userInfo = User.query
    
    def makeForm(days):
        groupPartalInfo = []
        for ele in members:
            weight = Weight.query.filter_by(email=ele).first()
            if weight is not None:
                daysFromLast = (datetime.now(pytz.timezone(weight.timezone)).date() - weight.lastupdated).days
                weightarray = weight.weight.split(",")
                if days - daysFromLast <= len(weightarray) and daysFromLast <= days - 2:
                    firstday = weightarray[daysFromLast - days]
                    lastday = weightarray[-1]
                    info = []
                    info.append(weight.nickname)
                    info.append(firstday)
                    info.append(lastday)
                    lossPercentage = "%.2f"%((float(firstday) - float(lastday))/float(firstday)*100)
                    info.append(float(firstday) - float(lastday))
                    info.append(float(lossPercentage))
                    if weight.email == session['email']:
                        info.append("self")
                    else:
                        info.append("members")
                    groupPartalInfo.append(info)
                    

                    #get the matrix for weight information
                    graphicInfo = []
                    for i in range(0, days - daysFromLast):
                        graphicInfo.append(float(weightarray[daysFromLast - days + i])/float(weightarray[daysFromLast - days]))
                    for i in range(0, daysFromLast):
                        graphicInfo.append(None)
                    
                    graphicInfo = [weight.nickname] + graphicInfo
                    graphic.append(graphicInfo)
    
        groupPartalInfo.sort(key=(itemgetter(-2)),reverse=True)
        for i in xrange (len(groupPartalInfo)):
            groupPartalInfo[i] = [i + 1] + groupPartalInfo[i]

        return groupPartalInfo



    def makePicture(days):
        colorPool = ["#F0A3FF","#0075DC","#2BCE48","#FFCC99","#FFA405","#FFA8BB","#5EF1F2","#740AFF","#FFFF80","#FF5005"]
        weight = Weight.query.filter_by(email = session["email"]).first()
        if weight is None:
            weight =Weight.query.first()
        day = []
        dates = []
        reduce = (days / 30) + 1
        plt.figure(figsize = (18,5))
        for i in xrange(days):
            day.append(i)
            if reduce == 0 or i%reduce == 0:
                dates.append(str(datetime.now(pytz.timezone(weight.timezone)).date() - timedelta(i)))
        dates.reverse()
    
        for i in xrange(days):
            j = 0
            for ele in graphic:
                if j < 10:
                    #plt.plot(day[i],ele[i + 1],linestyle="None",marker = "o", markersize = 4, color = colorPool[j])
		    #zhfont1 = matplotlib.font_manager.FontProperties(fname='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc')
                    plt.plot(day,ele[1:],linestyle="solid",color=colorPool[j],linewidth=3,label=unicode(ele[0]))
                    j += 1

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(),loc="center left", bbox_to_anchor=(1, 0.5),prop=prop)
        file = "/var/www/weight_overflow/files/static/weightgram/groups/" + groupname
        plt.xticks(day, dates, rotation=45)
        plt.subplots_adjust(bottom=0.30)
        if reduce != 0:
            plt.xticks(np.arange(min(day), max(day)+1, reduce))
        if os.path.exists(file):
            filenumber = int(os.listdir(file)[0].split(".")[0][1:])
            filenumber += 1
            number[0] = str(filenumber)
            os.remove(file + "/w" + str(filenumber - 1) + ".png")
            plt.savefig(file + "/w" + str(filenumber) + ".png")
        else:
            os.mkdir(file)
            plt.savefig(file + "/w0.png")
            number[0] = "0"
        plt.clf()
        
    for ele in Achieved.query.all():
        info = []
        info.append(ele.nickname)
        info.append(ele.begindate)
        info.append(ele.enddate)
        info.append(ele.beginweight)
        info.append(ele.target)
        info.append(float(ele.beginweight) - float(ele.target))
        info.append("%.2f"%((float(ele.beginweight) - float(ele.target)) * 100 / float(ele.beginweight)))
        info.append(ele.email)
        achieve.append(info)
    achieve.sort(key=(itemgetter(-1)), reverse = True)

                    
                    
                    





    if request.method == "POST":
        if form.select.data in ["7","14","30","60"]:
            groupPartalInfo = makeForm(int(form.select.data))
            makePicture(int(form.select.data))
            number = number[0]
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        if form.select.data == "max":
            weight = Weight.query.filter_by(email = session['email']).first()
            daysFromStart = (datetime.now(pytz.timezone(weight.timezone)).date() - weight.begindate).days + 1
            groupPartalInfo = makeForm(daysFromStart)
            makePicture(daysFromStart)
            number = number[0]

        if form.select.data == "all":
            #table infornation gathered from here
            for ele in members:
                weight = Weight.query.filter_by(email=ele).first()
                if weight is not None:
                    info = []
                    info.append(weight.nickname)
                    info.append(weight.begindate)
                    info.append(weight.weight.split(",")[0])
                    info.append(weight.lastupdated)
                    info.append(weight.weight.split(",")[-1])
                    lossPercentage = "%.2f"%((float(weight.weight.split(",")[0]) - float(weight.weight.split(",")[-1]))/float(weight.weight.split(",")[0])*100)
                    info.append(float(lossPercentage))
                    info.append(weight.target)
                    groupTotalInfo.append(info)
            groupTotalInfo.sort(key=(itemgetter(-2)), reverse = True)





    if form1.groupname.data == groupname:
        person = session['email']
        #remove from group's member list
        group = Group.query.filter_by(groupname=groupname).first()
        temp = group.members.split(',')
        temp.remove(person)
        group.members = ','.join(temp)
        ##remvoe from grouplist##
        user = User.query.filter_by(email = person).first()
        temp = user.grouplist.split(',')
        temp.remove(groupname)
        user.grouplist = ','.join(temp)
#        #remove from weight gram
#        weight = Weight.query.filter_by(email = person).first()
#        temp = weight.groups.split(',')
#        temp.remove(groupname)
#        user.groups = ','.join(temp)
        db.session.commit()
        return redirect(url_for('profile'))








    return render_template('groupinfo.html',groupname = groupname, groupTotalInfo = groupTotalInfo, groupPartalInfo = groupPartalInfo, nickname = nickname, number = number, form = form,achieve = achieve, userInfo = userInfo,form1 = form1)


































