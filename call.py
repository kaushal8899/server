from flask import Flask,send_file,render_template,url_for,request,redirect,abort,session
import erail as train
import requests
import db_connect
from user import User
import files_panda as pd
import pickle
from flask_cors import CORS
from flask_mail import Mail, Message
import aws_mail as mail_server
from security import Crypt

crypt = Crypt()

app  = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.secret_key = "$%ERGddfgfsdggdsfEDAGDGdEDSG%T$#%FDG"
mail_settings = {
    "MAIL_SERVER": 'email-smtp.ap-south-1.amazonaws.com',
    "MAIL_PORT": 25,
    "MAIL_USE_TLS": True,
    "MAIL_USERNAME": "AKIAURE7KOL7OZD77PW2",
    "MAIL_PASSWORD": "BKvGqC062vvkLOgvc6ArdRglEqM+GCSiPhV3CBBSJJSM"
}
# key = "BF7MEVG9zVXac/GCqOrjxF4VgAFN3P5KIEFvffkJ2OJJ"
# password = mail_server.calculateKey("BF7MEVG9zVXac/GCqOrjxF4VgAFN3P5KIEFvffkJ2OJJ","ap-south-1")

app.config.update(mail_settings)
mail = Mail(app)

@app.route("/admin")
def admin():
    session['user_id'] = ""

    try:
        data = request.args.get('data')
    except:
        pass
    return render_template("index.html",data=data)

@app.route("/favicon.ico")
def icon():
    return url_for("static",filename="favicon.ico")


@app.route("/admin/login/")
def admin_login():
    email = request.args.get('name')
    password = request.args.get('password')
    password = crypt.encrypt(password)
    user  = db_connect.getUser(email,password)
    data = ""
    if(user==-1 ):
        data = "User Not Found"
    elif( user['type']=="user" or user['isvalid'] == False):
        data = "Invalid User"
    else:
        session['user_id'] = str(user['_id'])
        return redirect(url_for("home"))
    return render_template("index.html",data=data)

@app.route("/admin/logout")
def admin_logout():
    session['user_id'] = ""
    return redirect(url_for("admin"))


@app.route("/changepassword/<email>/<oldpass>/<newpass>")
def changepassword(oldpass,newpass):
    oldpass = crypt.decrypt(oldpass)
    user  = str(db_connect.getUser(email))
    res = ""
    if user.password==oldpass :
        db_connect.deleteUser(email)
        user['password'] = crypt.encrypt(newpass)
        db_connect.add_user(User.fromdict(user))
        res = "Password Changed..!!"
    else:
        res = "Wrong Password"
    return res

@app.route("/login/<email>/<password>")
def login(email,password):
    password = crypt.encrypt(password)
    user  = str(db_connect.getUser(email,password))
    user = user.replace('\'',"\"")
    user = user.replace('ObjectId',"")
    user = user.replace("(","")
    user = user.replace(")","")
    return user

@app.route("/signup/",methods=['POST','GET'])
def signup():
    jsonData = request.get_json()
    print(jsonData)
    password = jsonData['password']
    password = crypt.encrypt(password)
    us = User(jsonData['name'],jsonData['email'],jsonData['mobile'],password)
    status = db_connect.add_user(us)
    return str(status)

@app.route("/admin/register/",methods=['POST','GET'])
def admin_reg():
    data = request.form
    password = crypt.encrypt(data['password'])
    u  = User(data['name'],data['email'],data['mobile'],password,type="admin")
    if(db_connect.add_user(u)==1):
        return redirect(url_for("admin"))
    else:
        abort(406)

@app.route("/getalllocations")
def getalllocations():
    locs = pd.getLocs()
    ans = ""
    for l in locs:
        ans += l+" "
    return ans


@app.route("/locdetails/<name>")
def locdetails(name):
    details = str(pd.getLocDetails(name))
    details = details.replace('\'',"\"")
    details = details.replace('nan','null')
    return details

@app.route("/getImg/<name>")
def getImg(name):
    try:
        file = send_file("imgs\\"+name+".png",mimetype='image/png')
    except:
        file = send_file("imgs\\default.png",mimetype='image/png')
    return file


@app.route("/getImgOld/old/<name>")
def getImgOld(name):
    try:
        file = send_file("imgs_old\\"+name+"_old.png",mimetype='image/png')
    except:
        file = send_file("imgs_old\\default_old.png",mimetype='image/png')
    return file

@app.route("/getDisc/<name>")
def getDisc(name):
    file = open("disc\\"+name+".txt","rb")
    return file.read().decode('utf-8')

@app.route("/admin/home")
def home():
    return render_template("home.html")

@app.route("/admin/users")
def users():
    if session['user_id'] =="":
        return redirect(url_for("admin",data="Session Expired Login Again."))
    data = db_connect.getallUsers()
    return render_template("users.html",data=data)

@app.route("/admin/invalidate/<email>/")
def invalidate(email):
    user = db_connect.getUser(email,"")
    db_connect.deleteUser(email)
    User.fromdict(user).invalidateUser()
    return redirect(url_for("users"))

@app.route("/admin/Validate/<email>/")
def validate(email):
    user = db_connect.getUser(email,"")
    db_connect.deleteUser(email)
    db_connect.add_user(User.fromdict(user))
    return redirect(url_for("users"))

@app.route("/admin/resetlink/<email>/<password>/")
def resetlink(email,password):
    user = db_connect.getUser(email,password)
    # print(crypt.decrypt(password))
    data = '''
    Name     : '''+user['name']+'''
    Email    : '''+user['email']+'''
    Password : '''+crypt.decrypt(password)+'''
    Mobile   : '''+str(user['mobile'])+'''
    '''
    print(data)
    with app.app_context():
            msg = Message(subject="User Details",
                          sender="travelguruadmin@zohomail.in",
                          recipients=['chaudhrani.kaushal@gmail.com'],
                          body="<h2>User Details<h2>: \n"+data)
            # mail.send(msg)
    return redirect(url_for("users"))

@app.route("/admin/locations")
def locations():
    if session['user_id'] =="":
        return redirect(url_for("admin",data="Session Expired Login Again."))
    data = pd.getallLocations()

    return render_template("locations.html",data=data)

@app.route("/findtrain/<source>/<dest>/<date>")
def findtrain(source,dest,date):
    '''url = 'https://api.railwayapi.com/v2/between/source/'+source+'/dest/'+dest+'/date/'+date+'/apikey/hd9nhw90fq/'
    return getFromurl(url)'''
    return str(pd.getTrain(source,dest,date)).replace('\'','\"')


@app.route("/findflight/<source>/<dest>/<date>")
def findflights(source,dest,date):
    return str(pd.getFlight(source,dest,date)).replace('\'','\"')

@app.route("/trainrunningdays/<train_n>")
def trainrunningdays(train_n):
    url = 'https://api.railwayapi.com/v2/route/train/'+train_n+'/apikey/hd9nhw90fq/'
    return getFromurl(url)


@app.route("/getfair/<train_n>/<source>/<dest>/<date>/<t_class>/<quota>/<age>")
def getfair(train_n,source,dest,date,t_class,quota,age):
    url = "https://api.railwayapi.com/v2/fare/train/"+train_n+"/source/"+source+"/dest/"+dest+"/age/"+age+"/pref/"+t_class+"/quota/"+quota+"/date/"+date+"/apikey/hd9nhw90fq/"
    req = requests.get(url=url)
    try:
        res = req.json()
        res = dict(res)
        return str(res['fare'])
    except:
        return "0"


@app.route("/seatavailble/<stn_from>/<to>/<date>/<t_class>/<quota>/<train_n>")
def seatavailble(stn_from,to,date,t_class,quota,train_n):
    dd = str(date[:2])
    mm = str(date[3:5])
    yy = str(date[7:11])
    args={'stn_from':stn_from,'stn_to':to,'day':dd,'month':mm,'year':yy,'class':t_class,'quota':quota,'train_n':train_n}
    return train.find_availablity(args)

def getFromurl(url):
    request=requests.get(url=url)
    response=request.json()
    return str(response).replace('\'','\"')

if __name__ == '__main__':

    app.run(host='0.0.0.0',debug=True)
