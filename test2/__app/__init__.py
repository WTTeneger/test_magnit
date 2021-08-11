import random
import time
import datetime

from __module import JWT, data_base, theards, senderMail
from __settings import env


from flask import *
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room, send
DB = data_base.DB

JWTs = JWT.tokinService()
PasswordCache = JWT.password_cache()
# print(JWTs)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.debug = True
CORS(app)
socketio = SocketIO(app)
from __app import api, view