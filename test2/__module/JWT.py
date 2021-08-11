import jwt
import json
import base64
import time
import hashlib
import uuid
from __settings import env



class tokinService():
    def __init__(self):
        """ Конструктор 
        
        При создание принимает ключ шифровки
        """


    def generateTokins(self, payload) -> json:
        """
        Генерит пару ключей

        Returns:
            json: [description]
        """
        data = { "payload":{
            'data': payload,
            'expiresIn': '30m',
            'time_create': time.time()
        }}
        ACCESS = jwt.encode(data, env.JWT_ACCESS_SECRET, algorithm="HS256")

        data['payload']['expiresIn'] = '30d'
        
        REFRESH = jwt.encode(data, env.JWT_REFRESH_SECRET, algorithm="HS256")

        data_re = {
            'accessTokin':ACCESS,
            'refreshTokin':REFRESH
        }
        return(data_re)

    
    def decodeTokins(self, type_sc:str = 'ACCESS', JWT_text:str = '') -> json:
        if(type_sc =="ACCESS"):
            q = jwt.decode(JWT_text, env.JWT_ACCESS_SECRET, algorithms=["HS256"])
        else:
            q = jwt.decode(JWT_text, env.JWT_REFRESH_SECRET, algorithms=["HS256"])
        return(q)
        

    def checkTokins(self, tokinDecode:json, tokin = ''):
        types = ''
        tplas = 0
        qr_otv = ' '
        if('m' in tokinDecode['payload']['expiresIn']):
            types='access'
            tplas = int(tokinDecode['payload']['expiresIn'].replace('m',''))
            mng = 60
            tplas *= mng
            status = 'ACCESS'

        elif('d' in tokinDecode['payload']['expiresIn']):
            types='refresh'
            tplas = int(tokinDecode['payload']['expiresIn'].replace('d',''))
            mng = 60*60*24
            tplas *= mng
            status = 'REFRESH'

 
        print(((tokinDecode['payload']['time_create'] + tplas) - time.time()))
        # print(status)
        if(((tokinDecode['payload']['time_create'] + tplas) - time.time())>0):
            return(True,'live')
        else:
            return(False, 'timeEnd')


class password_cache():
    """Работа с кэшем паролей
    ~~~
    """
    def __init__(self):
        """ Конструктор 
        """

    def hash_password(self, password):
        # uuid используется для генерации случайного числа
        salt = uuid.uuid4().hex
        return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt


    def check_password(self, hashed_password, user_password):
        password, salt = hashed_password.split(':')
        return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

