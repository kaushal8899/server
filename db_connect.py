import pymongo
client = pymongo.MongoClient("mongodb://localhost:27017")

mydb = client['travel_guru']
def add_user(user):
    try:
        collec = mydb['users']
        collec.insert_one(user.getUser())
        status = 1
    except:
        status = -1
    return status

def deleteUser(email):
    try:
        collec = mydb['users']
        collec.remove({'email':email})
    except:
        return -1
    return 1

def getUser(email,password):
    try:
        collec = mydb['users']
        if(password != ""):
            print(email,password)
            user = collec.find({'email':email,'password':password})
        else:
            user = collec.find({'email':email})
        user = user.next()
    except StopIteration:
        user = -1
    return user

def getallUsers():
    users = []
    collec = mydb['users']
    users =  list(collec.find())
    return users
