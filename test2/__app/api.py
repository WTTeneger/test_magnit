from __app import *


@app.route('/api/auth', methods=["POST"])
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


@app.route('/api/deauth', methods=["POST"])
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


@app.route('/api/register', methods=["POST"])
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


@app.route('/api/createAuc', methods=["POST"])
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
                z = F""" INSERT INTO auc VALUES(null, {da_Token['payload']['data']['id']}, '{req['title']}', '{req['info']}', '{req['betStart']}', '{req['betStep']}', '{dateN}', 'active') """
                DB.POST(z)

                d = DB.GET('SELECT email, login FROM users')
                print(d)
                for el in d:
                    print(el)
                    senderMail.SendMessageMail(el[0], el[1], f'Создан аукцион {req["title"]}')
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


@app.route('/api/getAuc', methods=["GET"])
@app.route('/api/getAuc/<int:aucId>', methods=["GET"])
def api_getAuc(aucId = None):
    if request.cookies.get('refreshToken'):
        da_Token = JWTs.decodeTokins(type_sc='REFRASH', JWT_text=request.cookies.get('refreshToken'))
        result = JWTs.checkTokins(da_Token, request.cookies.get('refreshToken'))
        if(result[0]):
            if not(aucId):
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
                        'betStep':el[5],
                        'end_time':el[6],
                        'status':el[7]

                    })
                print(data)
                res = {
                    'status':'good - Всё хорошо',
                    'auc':data
                }
                return(res, 200)
            else:
                tx = f'SELECT * FROM auc WHERE id = {aucId}'
                el = DB.GET(tx)
                if(len(el)>0):
                    el = el[0]
                    bets = []
                    data_from_db_where_bets = DB.GET(f"""SELECT users.login, bets.bet from bets, users where bets.userId = users.id and bets.aucId = {aucId}""")
                    print(data_from_db_where_bets)
                    for ee in data_from_db_where_bets:
                        print(ee)
                        bets.append({
                            'name': ee[0],
                            'bets': ee[1]
                        })
                    return_data_auc = ({
                        'title':el[2],
                        'info':el[3],
                        'betStart':el[4],
                        'betStep':el[5],
                        'end_time':el[6],
                        'status':el[7],
                        'bets':bets

                    })
                    res = return_data_auc
                    return(res, 200)
                else:
                    res = {
                    'status':'auc_notFound - Аукцион с таким id не найден',
                    }
                    return(res, 200)
    else:
        res = {
            'status':'you_not_auth - Вы не авторизованы',
        }
        return(res, 400)



@app.route('/api/newBet', methods=["POST"])
def api_postBet():
    if request.cookies.get('refreshToken'):
        da_Token = JWTs.decodeTokins(type_sc='REFRASH', JWT_text=request.cookies.get('refreshToken'))
        result = JWTs.checkTokins(da_Token, request.cookies.get('refreshToken'))
        if(result[0]):
            try:
                req = json.loads(request.data.decode())
            except:
                res = {
                'status':'you_not_valid - Не верный формат',
                }
                return(res, 400)
            d = DB.GET(f""" SELECT * FROM auc where id = {req['id_auc']} and status = 'active' """)
            if(len(d)>0):
                if(req['bet'] % d[0][5] == 0):
                    if(len(d)>0):
                        print(req)
                        t = f""" SELECT * FROM bets where `aucId` = {req['id_auc']} ORDER BY bet DESC LIMIT 1"""
                        dd = DB.GET(t)
                        


                        #Ставок нет
                        if(len(dd)==0):
                            print('Ставок нет, значит стартовая ', d[0][4])
                            if(req['bet'] >= d[0][4] + d[0][5]):
                                t = f""" SELECT * FROM bets where `aucId` = {req['id_auc']} ORDER BY bet DESC LIMIT 1"""
                                DB.POST(f""" INSERT INTO bets VALUES(null, {d[0][0]}, {da_Token['payload']['data']['id']}, {req['bet']}, '{time.strftime('%Y-%m-%d %H:%M:%S')}') """)
                                senderMail.sender_mail_groups_from_auc(d[0][0], da_Token['payload']['data']['id'], d[0][2])
                                res = {
                                    'status':'good - Ваша ставка принята',
                                    }
                                return(res, 200)
                            else:
                                res = {
                                'status':f'bet_low - Ваша ставка меньше или равна, чем стартовая ({d[0][4]})',
                                }
                                return(res, 400)
                        #Ставки есть
                        else:
                            if(dd[0][2] != da_Token['payload']['data']['id']):
                                print(dd[0][3]+ d[0][4] , req['bet'])
                                if(req['bet'] >= dd[0][3]+ d[0][5]):
                                    DB.POST(f""" INSERT INTO bets VALUES(null, {d[0][0]}, {da_Token['payload']['data']['id']}, {req['bet']}, '{time.strftime('%Y-%m-%d %H:%M:%S')}') """)
                                    senderMail.sender_mail_groups_from_auc(d[0][0], da_Token['payload']['data']['id'], d[0][2])
                                    res = {
                                    'status':'good - Ваша ставка принята',
                                    }
                                    return(res, 200)
                                else:
                                    res = {
                                    'status':f'bet_low - Ваша ставка меньше или равна, чем текущая ({dd[0][3]})',
                                    }
                                    return(res, 400)
                            else:
                                res = {
                                'status':f'owner_last_bet_you - Текущая ставка это ваша ставка',
                                }
                                return(res, 400)





                    else:
                        res = {
                        'status':'auction_not_found - Аукцион не найдет, или ставки больше не принимаются',
                        }
                        return(res, 400)
                else:
                    res = {
                    'status':'bet_not_valid - Не коректная ставка она не соответсвует шагу',
                    }
                    return(res, 200)
            else:
                res = {
                'status':'auc_notFound - Аукцион с этим id не найден, или завершён',
                }
                return(res, 200)
            # print(d)
            res = {
            'status':'you_not_valid - Ставка сделана',
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

