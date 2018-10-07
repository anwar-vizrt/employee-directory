from util.constants import Roles
class Employee:
    def __init__(self, json_data = None, raw_data = None):
        if json_data:
            self.__username = json_data['username']
            self.__password = json_data['password']
            self.__email = json_data['email']
            self.__firstname = json_data['firstname']
            self.__lastname = json_data['lastname']
            self.__birthdate = json_data['birthdate']
            self.__phonenumber = json_data['phonenumber']
            self.__type = Roles.RoleType[json_data['type']]
        if raw_data:
            self.__username = raw_data['username']
            self.__password = raw_data['hashed_password']
            self.__email = raw_data['email']
            self.__firstname = raw_data['firstname']
            self.__lastname = raw_data['lastname']
            birthdate = raw_data['birthdate']
            birthdate = birthdate.strftime('%d-%m-%Y')
            self.__birthdate = birthdate
            self.__phonenumber = raw_data['phonenumber']
            self.__type = raw_data['type']

    def toJson(self):
        type = None
        for key, value in Roles.RoleType.items():
            if value == self.__type:
                type = key

        return {
            "username": self.__username,
            "passward": self.__password,
            "firstname": self.__firstname,
            "lastname": self.__lastname,
            "type": type,
            "birthdate": self.__birthdate,
            "email": self.__email,
            "phonenumber": self.__phonenumber
        }

    def equals(self, obj):
        if obj is None or not isinstance(obj, Employee):
            return False
        if obj.__username == self.__username and obj.__password == self.__password and obj.__phonenumber == self.__phonenumber and obj.__email == self.__email and obj.__type == self.__type and obj.__firstname == self.__firstname and obj.__lastname == self.__lastname and obj.__birthdate == self.__birthdate:
            return True
        else:
            return False

    def set_hashed_password(self,hashed_password):
        self.__password = hashed_password

    def getUsername(self):
        return self.__username

    def getPassword(self):
        return self.__password

    def getEmail(self):
        return self.__email

    def getFirstname(self):
        return self.__firstname

    def getLastname(self):
        return self.__lastname

    def getType(self):
        return self.__type

    def getBirthdate(self):
        return self.__birthdate

    def getPhonenumber(self):
        return self.__phonenumber
