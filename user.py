import db_connect as db
import datetime
class User:
    def __init__(self,name,email,mobile,password,type='user',isvalid=True,timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
        self.name = name
        self.email = email
        self.mobile = str(mobile)
        self.password = str(password)
        self.type = type
        self.isvalid = isvalid
        self.timestamp = timestamp

    @classmethod
    def fromdict(cls, datadict):
        del datadict['_id']
        del datadict['isvalid']
        return cls(**datadict)

    def getUser(self):
        return self.__dict__

    def invalidateUser(self):
        self.isvalid = False
        db.add_user(self)
