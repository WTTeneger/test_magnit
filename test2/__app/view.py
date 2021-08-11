from __app import *

@app.route('/')
def index():
    q = DB.GET('SELECT * FROM users')
    
    return(str(q))




# senderMail.SendMessageMail('amal.agishev@mail.ru', 'Мфы', 'Крутяяк')