from __app import *


@app.route('/api/auth')
def api_auth():
    req = json.loads(request.data.decode())
    if request.cookies.get('refreshToken'):
        result = JWTs.decodeTokins(type_sc='REFRASH', JWT_text=request.cookies.get('refreshToken'))
        print('Уже авторизован')
        res = make_response({
            'status':'auth_later - вы авторизован'
        })
    else:
        q = DB.GET(f"""SELECT * FROM users WHERE login = '{req['login']}'""")
        print(q)
        if(len(q)==0):
            res = make_response({
                'status':'auth_not - Не верные данные'
            })
            return(res, 400)
            
        else:
            if(PasswordCache.check_password(q[0][2], req['password'])):
                res = make_response({
                    'status':'auth_now - успешная авторизация'
                })
                jwts = JWTs.generateTokins({
                    "id": q[0][0], 
                    "login": req['login'], 
                    'password': req['password']
                })
                res.set_cookie('refreshToken', jwts['refreshTokin'], 60*60*24*30)
            else:
                res = make_response({
                    'status':'auth_not - Не верные данные'
                })
                return(res, 400)
    return(res, 200)
    # q = DB.GET('SELECT * FROM users')


@app.route('/api/deauth')
def api_deauth():
    if request.cookies.get('refreshToken'):
        res = make_response({
            'status':'deauth_now',
            'text':{
                'ru':'Вы вышли',
                'en':'u reauth'
            }
        })
    else:
        res = make_response({
            'status':'deauth_later',
            'text':{
                'ru':'Вы не вошли',
                'en':'u dont auth'
            }
        })

    res.set_cookie('refreshToken', 'deauth', 0)
    return(res, 200)


@app.route('/api/register')
def api_register():
    if request.cookies.get('refreshToken'):
        res = {
            'status':'you_auth',
            'text':{
                'ru':'Вы сейчас авторизаванны',
                'en':'u auth now'
            }
        }
        return(res, 400)
    else:
        
        
        try:
            req = json.loads(request.data.decode())
            if('login'and'password'and'email' in req):
                q = DB.GET(f"""SELECT * FROM users WHERE login = '{req['login']}' or email = '{req['email']}' """)
                if(len(q)==0):
                    password_hash = PasswordCache.hash_password(req['password'])
                    DB.POST(f""" INSERT INTO users VALUES(null, '{req['login']}', '{password_hash}', '{req['email']}' ) """)
                    res = {
                        'status':'good - Вы авторизованы'
                    }
                    
                    return(res, 200)
                else:
                    res = {
                        'status':'errors - Указанные данные заняты'
                    }
                    return(res, 400)
                
            
            else:
                res = {
                'status':'errors - not valid'
                }
                return(res, 400)
        except:
            res = {
                'status':'errors ex'
            }
            return(res, 400)
    # res.set_cookie('refreshToken', 'deauth', 0)


@app.route('/api/createAuc')
def api_createAuc():
    if request.cookies.get('refreshToken'):
        da_Token = JWTs.decodeTokins(type_sc='REFRASH', JWT_text=request.cookies.get('refreshToken'))
        result = JWTs.checkTokins(da_Token, request.cookies.get('refreshToken'))
        if(result[0]):
            req = json.loads(request.data.decode())
            # print(req)
            print(da_Token)
            if('title' and 'info' and 'betStart' and 'betStep' and 'endTime' in req):
                now = datetime.datetime.now() + datetime.timedelta(days=int(req['endTime'].replace('d','')))
                dateN = (now.strftime('%Y-%m-%d %H:%M:%S'))
                z = F""" INSERT INTO auc VALUES(null, {da_Token['payload']['data']['id']}, '{req['title']}', '{req['info']}', '{req['betStart']}', '{req['betStep']}', '{req['betStart']}', '{dateN}', 'active') """
                DB.POST(z)
                res = {
                    'status':'you_auth - Создан акцион',
                }
                return(res, 200)
            else:
                res = {
                    'status':'not valid - Не верный формат данных',
                }
                return(res, 400)
        else:
            res = {
            'status':'you_auth - Токин просрочен',
        }
        return(res, 400)
    else:
        res = {
            'status':'you_auth - Вы не авторизованы',
        }
        return(res, 400)


@app.route('/api/getAuc')
def api_getAuc():
    if request.cookies.get('refreshToken'):
        da_Token = JWTs.decodeTokins(type_sc='REFRASH', JWT_text=request.cookies.get('refreshToken'))
        result = JWTs.checkTokins(da_Token, request.cookies.get('refreshToken'))
        if(result[0]):
            try:
                req = json.loads(request.data.decode())
            except:
                req = ''
            # print(req)
            if(('filter' in req) and (req['filter'] in ('active', 'end', 'all'))):
                tx = f""" SELECT * FROM auc WHERE status = "{req['filter']}" """ if req['filter'] != 'all' else 'SELECT * FROM auc'
            else:
                tx = 'SELECT * FROM auc'
            
            d = DB.GET(tx)
            data = []
            for el in d:
                data.append({

                    'title':el[2],
                    'info':el[3],
                    'betStart':el[4],
                    'betStep':el[6],
                    'bet':el[5],
                    'end_time':el[7],
                    'status':el[8]

                })
            print(data)
        res = {
            'status':'good - Всё хорошо',
            'auc':data
        }
        return(res, 200)
    else:
        res = {
            'status':'you_not_auth - Вы не авторизованы',
        }
        return(res, 400)
# @socketio.on('my event bar')
# def test_message(message):
#     print(message)
#     emit('Hah')



# @socketio.on('test repka')
# def test_message(message):
#     print(message)
#     emit('repka', {'data': {'name':"Amal",'lastName':'Agishev', 'message':random.randint(0, 515)}})

