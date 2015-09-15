from flask import Flask, render_template, request, flash, session, redirect, url_for
from forms import SignupForm, SigninForm, GroupForm, WeightForm, EditForm, UserProgressForm
from files import app
from models import db, User, Group, Weight, Achieved
from sqlalchemy import func
from datetime import datetime, date, timedelta
import pytz
import matplotlib.pyplot as plt
import os,os.path
import numpy as np

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



@app.route('/profile', methods=['GET','POST'])
def profile():
    if 'email' not in session:
        return redirect(url_for('index'))

    user = User.query.filter_by(email = session['email']).first()
    nickname = user.nickname
    if user is None:
        return redirect(url_for('index'))
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
            plt.figure(figsize=(11.4, 4))
            if length - daysFromLast > 1:
                for i in range(0, daysFromLast):
                    recordarray.append(None)
                for i in range(0, length - daysFromLast):
                    if len(weightarray) > 0:
                        recordarray.append(float(weightarray.pop()))
                    else:
                        recordarray.append(None)
                recordarray.reverse()
                for i in range(0, length):
                    
                    day.append(i)
                    if reduce == 0 or i%reduce == 0:
                        labels.append(str(datetime.now(pytz.timezone(weight.timezone)).date() - timedelta(i)))
                labels.reverse()
                for i in range(0, length):
                    plt.plot(day[i],recordarray[i], linestyle="None",marker = "o", markersize = 8, color = "red")
                    plt.plot(day, recordarray, linestyle="solid",color="green",linewidth=3,label=session['email'] if i ==0 else "")
                plt.legend(loc='best')
                file = "/Users/Lucify/Documents/git_repo/weight_overflow/files/static/weightgram/users/" + nickname
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


    form = EditForm()
    form1 = WeightForm()
    form2 = UserProgressForm()
    
    if request.method == 'POST':
        #for weight form
  
        if form1.validate_on_submit() and form1.validate():
            user = Weight.query.filter_by(email = session['email']).first()

            if user == None:
                currentUser = User.query.filter_by(email = session['email']).first()
                grouplist = User.query.filter_by(email = session['email']).first().grouplist
                newWeight = Weight(session['email'],form1.todaysweight.data,datetime.now(pytz.timezone(form1.timezone.data)).date(),datetime.now(pytz.timezone(form1.timezone.data)).date(),grouplist, nickname, form1.timezone.data, currentUser.target)
                db.session.add(newWeight)
                db.session.commit()
            
            if user != None:
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
        if form.validate_on_submit() and form.validate():
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
            db.session.commit()
            return redirect(url_for('profile'))


        #for user process tracking form
        if form2.validate_on_submit() and form2.validate():
            if form2.days.data in ["7","30"]:
                makePicture(int(form2.days.data))
                number = number[0]
            elif form2.days.data == "max":
                weight = Weight.query.filter_by(email = session['email']).first()
                days = (datetime.now(pytz.timezone(weight.timezone)).date() - weight.begindate).days + 1
                makePicture(days)
                number = number[0]
        



    return render_template('profile.html',nickname = user.nickname,email = user.email,groupnameList = groupnameList, grouplist=grouplist, form = form, form1 = form1, form2 = form2, number = number)



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
    
    number = ""
    group = Group.query.filter_by(groupname=groupname).first()
    members = group.members.split(',')
    user = User.query.filter_by(email = session['email']).first()
    nickname = user.nickname
    groupWeightInfo = []
#    form = WeightForm(request.form)

#    if request.method == "POST":
#        if form.validate():
#            user = Weight.query.filter_by(email = session['email']).first()
#            
#            if user == None:
#                currentUser = User.query.filter_by(email = session['email']).first()
#                grouplist = User.query.filter_by(email = session['email']).first().grouplist
#                newWeight = Weight(session['email'],form.todaysweight.data,datetime.now(pytz.timezone(form.timezone.data)).date(),datetime.now(pytz.timezone(form.timezone.data)).date(),grouplist, nickname, form.timezone.data, currentUser.target)
#                db.session.add(newWeight)
#                db.session.commit()
#            
#            if user != None:
#                #first day recording, if it's not the first day, go to else
#                temp = (datetime.now(pytz.timezone(user.timezone)).date() - user.lastupdated).days
#                if temp > 0:
#                    user.daysAbsent = temp
#                if user.daysAbsent == 0:
#                    user.weight = "%.2f"%(float(form.todaysweight.data))
#                #after first day
#                else:
#                    #days that this ppl is not recording the weight info, this will remain the same if
#                    #ppl try to modify today's weight.
#                    #check if user have already entered today's weight
#                    exist = False
#                    if user.lastupdated == datetime.now(pytz.timezone(user.timezone)).date():
#                        exist = True
##                    #check if user want to change their time zone info
##                    if form.timezone.data == 'default':
##                        user.lastupdated = datetime.now(pytz.timezone(user.timezone)).date()
##                    else:
##                        user.lastupdated = datetime.now(pytz.timezone(form.timezone.data)).date()
##                        user.timezone = form.timezone.data
#                    #delete data back to last recorded time
#                    if exist:
#                        temp = user.weight.split(',')
#                        for i in range(0,user.daysAbsent):
#                            temp.pop()
#                        user.weight = ','.join(temp)
#                    #add data back to database
#                    last = float(user.weight.split(",")[-1])
#                    now = float(form.todaysweight.data)
#                    differenceEachDay = (now - last)/user.daysAbsent
#                    for i in range(1,user.daysAbsent):
#                        user.weight += "," + "%.2f"%(i * differenceEachDay + last)
#                    user.weight += "," + "%.2f"%(form.todaysweight.data)
#                db.session.commit()
#            #put user's information into achieve table if they achieve their target weight
#            user = Weight.query.filter_by(email = session['email']).first()
#            if user.target is not None:
#                achieved = Achieved.query.filter_by(email = session['email']).first()
#                begin = float(user.weight.split(",")[0])
#                target = float(user.target)
#                #requirement to be recorded: not in the least, reached the target, loss more than 10% of ur body weight
#            if float(user.weight.split(",")[-1]) <= target and achieved == None and begin - target >= begin * 0.1:
#                    grats = Achieved(user.email, user.nickname, user.begindate,user.lastupdated,user.weight.split(",")[0],user.target)
#                    db.session.add(grats)
#                    db.session.commit()






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
            info.append(lossPercentage)
            info.append(weight.target)
            groupWeightInfo.append(info)

    week = False
    month = False
    #picture information gathered from bere
    currentUser = Weight.query.filter_by(email=session['email']).first()
    if currentUser is not None:
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        activeDays = (currentUser.lastupdated - currentUser.begindate).days
        

        matrixInfo = []
        weightInfo = []
        for ele in members:
            weight = Weight.query.filter_by(email=ele).first()
            if weight is not None:
                weightInfo.append(weight.email)
                temp = weight.weight.split(",")
                daysDifferent = (currentUser.lastupdated - weight.lastupdated).days
                for i in range (0,daysDifferent):
                    temp.pop()
                weightInfo += temp
                matrixInfo.append(weightInfo)
                weightInfo = []

        def weekInfo():
            result = []
            for ele in matrixInfo:
                if len(ele) > 7:
                    temp = []
                    temp.append(ele[0])
                    for i in range(1,8):
                        temp.append(ele[i-8])
                    result.append(temp)
            return result


        def monthInfo():
            result = []
            for ele in matrixInfo:
                if len(ele) > 30:
                    temp = []
                    temp.append(ele[0])
                    for i in range(1,31):
                        temp.append(ele[i-31])
                    result.append(temp)
            return result

        colorPool = ["red","green","yellow","blue","black"]
        if activeDays >= 6:
            week = weekInfo()
            x = []
            for i in range(1,8):
                x.append(i)
            for i in range(0,7):
                j = 0
                for ele in week:
                    plt.plot(x[i],float(ele[i+1]), linestyle="None",marker = "o", markersize = 8, color = colorPool[j])
                    j+=1
            for i in range(0,7):
                j = 0
                for ele in week:
                    plt.plot(x,ele[1:], linestyle="solid",color=colorPool[j],linewidth=3,label=ele[0] if i ==0 else "")
                    j+=1
            plt.legend(loc='best')
            #check if file exist, if so delete this file and rename
            file = "/Users/Lucify/Documents/git_repo/weight_overflow/files/static/weightgram/" + nickname
            if os.path.exists(file):
                filenumber = int(os.listdir(file)[0].split(".")[0][1:])
                filenumber += 1
                number = str(filenumber)
                os.remove(file + "/w" + str(filenumber - 1) + ".png")
                plt.savefig(file + "/w" + str(filenumber) + ".png")
            else:
                os.mkdir(file)
                plt.savefig(file + "/w0.png")
            plt.clf()
                             
        if activeDays >= 29:
            month= monthInfo()
            x = []
            for i in range(1,31):
                x.append(i)
            for i in range(0,30):
                for ele in month:
                    plt.plot(x[i],float(ele[i+1]), linestyle="None",marker = "o", markersize = 8, color = "red")
            for i in range(0,30):
                for ele in month:
                    plt.plot(x,ele[1:], linestyle="solid",color="red",linewidth=3,label=ele[0] if i ==0 else "")
            plt.legend(loc='best')
            file = "/Users/Lucify/Documents/git_repo/weight_overflow/files/static/weightgram/" + nickname
            if os.path.exists(file) and len(os.listdir(file)) > 1:
                filenumber = int(os.listdir(file)[0].split(".")[0][1:])
                filenumber += 1
                os.remove(file + "/m" + str(filenumber - 1) + ".png")
                plt.savefig(file + "/m" + str(filenumber) + ".png")
            else:
                plt.savefig(file + "/m0.png")
            plt.clf()







    return render_template('groupinfo.html',groupname = groupname, groupWeightInfo = groupWeightInfo, nickname = nickname, week=week, month = month, number = number)


































