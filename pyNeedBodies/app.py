import os   
import random
import string
from flask import Flask, render_template, jsonify, redirect, request
import pandas as pd
import numpy as np
from markupsafe import escape_silent
from PasswordManager import PasswordManager

app = Flask(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))

def readArenaData():
    path = dir_path + '/arenas.xlsx'
    if os.path.exists(path):
        df = pd.read_excel(dir_path + '/arenas.xlsx')
    else:
        df = pd.DataFrame(columns=['arena',
                                   'address',
                                   'city',
                                   'province',
                                   'postal',
                                   'country',
                                   'website'])
    return df

def readGameData():
    path = dir_path + '/games.xlsx'
    if os.path.exists(path):
        df = pd.read_excel(dir_path + '/games.xlsx')
    else:
        df = pd.DataFrame(columns=['id',
                                   'host',
                                   'date',
                                   'time',
                                   'location',
                                   'player limit',
                                   'player list',
                                   'goalie limit',
                                   'goalie list'])
    return df

def readUserData():
    path = dir_path + '/users.xlsx'
    if os.path.exists(path):
        df = pd.read_excel(dir_path + '/users.xlsx')
    else:
        df = pd.DataFrame(columns=['id',
                                   'name',
                                   'email',
                                   'phone',
                                   'games',
                                   'hosted games',
                                   'role'])
    return df

def readHashData():
    path = dir_path + '/userhash.xlsx'
    if os.path.exists(path):
        df = pd.read_excel(dir_path + '/userhash.xlsx')
    else:
        df = pd.DataFrame(columns=['id',
                                   'salt',
                                   'hash',
                                   'RID'])
    return df

def writeData(df, fileName):
    df.to_excel(dir_path + '/' + fileName, index=False)

df_arenas = readArenaData()
df_games = readGameData()
df_users = readUserData()
df_hash = readHashData()

@app.route('/arenas')
def getArenas():
    global df_arenas
    myArenas = df_arenas.copy()

    city = escape_silent(request.args.get('city'))
    if len(city) != 0:
        myArenas = myArenas[myArenas['city'] == city]

    province = escape_silent(request.args.get('prov'))
    if len(province) != 0:
        myArenas = myArenas[myArenas['province'] == province]

    country = escape_silent(request.args.get('country'))
    if len(country) != 0:
        myArenas = myArenas[myArenas['country'] == country]

    myArenas['website'] = myArenas['website'].astype(str)

    return myArenas.to_json(orient='records')

@app.route('/games')
def getGames():
    global df_games
    myGames = df_games.copy()

    gameID = escape_silent(request.args.get('gameID'))
    if len(gameID) != 0:
        myGames = myGames[myGames['id'] == gameID]

    host = escape_silent(request.args.get('host'))
    if len(host) != 0:
        myGames = myGames[myGames['host'] == host]
    
    date = escape_silent(request.args.get('date'))
    if len(date) != 0:
        myGames = myGames[myGames['date'] == date]

    location = escape_silent(request.args.get('location'))
    if len(location) != 0:
        myGames = myGames[myGames['location'] == location]

    myGames['id'] = myGames['id'].astype(str)
    myGames['date'] = myGames['date'].astype(str)
    myGames['time'] = myGames['time'].astype(str)
    
    return myGames.to_json(orient='records')

@app.route('/users')
def getUsers():
    global df_users
    myUsers = df_users.copy()
    
    gameID = escape_silent(request.args.get('games'))
    myUsers = filterByGame(myUsers, gameID)
    myUsers['id'] = myUsers['id'].astype(str)
    myUsers['phone'] = myUsers['phone'].astype(str)

    return myUsers.to_json(orient='records')

@app.route('/addGame/<string:hostID>/<string:host>/<int:playerLim>/<int:goalieLim>', methods=['POST'])
def addGame(hostID=None, host=None, playerLim=None, goalieLim=None):

    global df_users
    global df_games
    myGames = df_games.copy()

    dateTimeLocation = request.json
    date = dateTimeLocation['date']
    time = dateTimeLocation['time']
    # expected date: yyyymmdd and time: hhmm
    date,time = formatDateTime(date, time)
    location = dateTimeLocation['location']
    game_id = generateID(myGames['id'])

    new_entry = [{'id': str(game_id),
                'host': host,
                'date': str(date),
                'time': str(time),
                'location': location,
                'player limit': playerLim,
                'player list': '',
                'goalie limit': goalieLim,
                'goalie list': ''}]
    
    df_games = pd.concat([myGames, pd.DataFrame.from_records(new_entry)], ignore_index=True)

    df_users['hosted games'] = df_users['hosted games'].astype(str)
    df_users.loc[df_users['id'] == hostID, 'hosted games'] = df_users.loc[df_users['id'] == hostID, 'hosted games'].replace('nan', '')

    df_users.loc[df_users['id'] == hostID, 'hosted games'] += str(game_id) + ';'

    writeData(df_games, 'games.xlsx')
    writeData(df_users, 'users.xlsx')

    #return df_games.to_json(orient='records')
    #return jsonify(new_entry[0])
    return 'success'

@app.route('/removeGame/<string:gameID>')
def removeGame(gameID=None):
    global df_games

    if len(df_games[df_games['id'] == gameID]) == 0:
        return "no game found"

    df_games = df_games[df_games['id'] != gameID]

    writeData(df_games, 'games.xlsx')

    return "success"

@app.route('/addUser/<string:name>/<string:phone>', methods=['POST'])
def addUser(name=None, phone=None):
    global df_users
    global df_hash
    myUsers = df_users.copy()
    userRequestInfo = request.json
    email = userRequestInfo['email']
    password = userRequestInfo['password']
    userID = generateID(myUsers['id'])

    new_entry = [{
        'id': str(userID),
        'name': name,
        'email': email,
        'phone': str(phone),
        'games': '',
        'hosted games': '',
        'role': 'user'
    }]

    errorMsg = CheckIfEmailPhoneUsed(new_entry)
    if errorMsg != None:
        return {"id": "  ",
                 "name":"  ",
                 "email":"  ",
                 "phone":"  ",
                 "games":errorMsg,
                 "hosted games":"  ",
                 "role":"  "}

    df_users = pd.concat([myUsers, pd.DataFrame.from_records(new_entry)], ignore_index=True)
    writeData(df_users, 'users.xlsx')

    # ------ hash password ------
    pwd = PasswordManager(password)
    hashJson = pwd.ToJson(userID)
    new_entry_hash = [{
        'id': str(userID),
        'salt': hashJson['salt'].decode('utf-8'),
        'hash': hashJson['hash'].decode('utf-8'),
        'RID': ''.join(random.choice(string.ascii_uppercase) for i in range(30))
    }]

    df_hash = pd.concat([df_hash, pd.DataFrame.from_records(new_entry_hash)], ignore_index=True)
    writeData(df_hash, 'userhash.xlsx')

    #return df_users.to_json(orient='records')
    return jsonify(new_entry[0])

@app.route('/checkUser/<string:userID>', methods=['POST'])
def checkUser(userID=None):
    global df_users
    global df_hash
    df_users['id'] = df_users['id'].astype(str)
    df_hash['id'] = df_hash['id'].astype(str)
    df_hash['hash'] = df_hash['hash'].astype(str)

    userRequestInfo = request.json
    password = userRequestInfo['password']

    user = df_users[df_users['id'] == userID]
    if len(user) == 0:
        return "error: no user found"
    
    userHash = df_hash[df_hash['id'] == userID]
    if len(userHash) == 0:
        return "error: no hash found"
    
    pwd = PasswordManager(password)
    if pwd.checkPassword(password, userHash['hash'].values[0].encode('utf-8')):
        return "success"
    else:
        return "wrong password"
    

@app.route('/addUserToGame/<string:userID>/<string:gameID>/<string:isGoalie>')
def addUserToGame(userID=None, gameID=None, isGoalie=None):
    global df_users
    global df_games
    df_users['id'] = df_users['id'].astype(str)
    df_games['id'] = df_games['id'].astype(str)
    df_users['games'] = df_users['games'].astype(str)
    df_games['player list'] = df_games['player list'].astype(str)
    df_games['goalie list'] = df_games['goalie list'].astype(str)

    booGoalie = (isGoalie == 'yes')

    user = df_users[df_users['id'] == userID]
    game = df_games[df_games['id'] == gameID]

    if len(user) == 0:
        return "Error: no user found"

    if len(game) == 0:
        return "Error: no game found"

    userGames = user['games'].values[0]
    gamePlayers = game['player list'].values[0]
    gameGoalies = game['goalie list'].values[0]


    if CheckIfUserInGame(userGames, gameID):
        return "You're already in this game!"
    if not booGoalie and (CountPlayers(gameID) >= int(game['player limit'].values[0])):
        return "Players for this game are full!"
    if booGoalie and (CountGoalies(gameID) >= int(game['goalie limit'].values[0])):
        return "Goalies for this game are full!"
    
    if str.find(gamePlayers, 'nan') != -1:
        gamePlayers = str.strip(gamePlayers, 'nan')
    if str.find(gameGoalies, 'nan') != -1:
        gameGoalies = str.strip(gameGoalies, 'nan')
    if str.find(userGames, 'nan') != -1:
        userGames = str.strip(userGames, 'nan')

    userGames = userGames + gameID + ';'
    df_users.loc[df_users['id'] == userID, 'games'] = userGames
    
    if booGoalie:
        gameGoalies += userID + ';'
        df_games.loc[df_games['id'] == gameID, 'goalie list'] = gameGoalies
    else:
        gamePlayers += userID + ';'
        df_games.loc[df_games['id'] == gameID, 'player list'] = gamePlayers

    writeData(df_users, 'users.xlsx')
    writeData(df_games, 'games.xlsx')

    return 'success'

@app.route('/removeUserFromGame/<string:userID>/<string:gameID>')
def removeUserFromGame(userID=None, gameID=None):
    global df_users
    global df_games
    df_users['id'] = df_users['id'].astype(str)
    df_games['id'] = df_games['id'].astype(str)
    df_users['games'] = df_users['games'].astype(str)
    df_games['player list'] = df_games['player list'].astype(str)
    df_games['goalie list'] = df_games['goalie list'].astype(str)


    user = df_users[df_users['id'] == userID]
    game = df_games[df_games['id'] == gameID]

    if len(user) == 0:
        return "Error: no user found"

    if len(game) == 0:
        return "Error: no game found"
    
    userGames = user['games'].values[0]
    gamePlayers = game['player list'].values[0]
    gameGoalies = game['goalie list'].values[0]
    
    if CheckIfUserInGame(userGames, gameID) == False:
        return "You're not in this game!"
    
    userGames = RemoveID(gameID, userGames)

    df_users.loc[df_users['id'] == userID, 'games'] = userGames
    
    booGoalie = CheckIfGoalie(userID, gameID)
    if booGoalie:
        gameGoalies = RemoveID(userID, gameGoalies)

        df_games.loc[df_games['id'] == gameID, 'goalie list'] = gameGoalies
    else:
        gamePlayers = RemoveID(userID, gamePlayers)

        df_games.loc[df_games['id'] == gameID, 'player list'] = gamePlayers

    writeData(df_users, 'users.xlsx')
    writeData(df_games, 'games.xlsx')

    return 'success'

@app.route('/getUserGames/<string:userID>')
def getUserGames(userID=None):
    global df_users
    global df_games
    df_users['id'] = df_users['id'].astype(str)
    df_games['id'] = df_games['id'].astype(str)
    df_users['games'] = df_users['games'].astype(str)
    df_games['player list'] = df_games['player list'].astype(str)
    df_games['goalie list'] = df_games['goalie list'].astype(str)

    user = df_users[df_users['id'] == userID]
    if len(user) == 0:
        return jsonify([])
    
    userGames = user['games'].values[0]
    userGameIDs = userGames.split(';')

    gamesUserIsIn = df_games[df_games['id'].isin(userGameIDs)]

    gamesUserIsIn['id'] = gamesUserIsIn['id'].astype(str)
    gamesUserIsIn['date'] = gamesUserIsIn['date'].astype(str)
    gamesUserIsIn['time'] = gamesUserIsIn['time'].astype(str)
    return gamesUserIsIn.to_json(orient='records')

@app.route('/getUserRID/<string:userID>')
def getUserRID(userID=None):
    global df_hash
    df_hash['id'] = df_hash['id'].astype(str)

    user = df_hash[df_hash['id'] == userID]
    if len(user) == 0:
        return "Error: no user found"
    
    return user['RID'].values[0]

@app.route('/resetUserPassword/<string:userID>', methods=['POST'])
def resetUserPassword(userID=None):
    global df_users
    global df_hash
    df_users['id'] = df_users['id'].astype(str)
    df_hash['id'] = df_hash['id'].astype(str)

    user = df_users[df_users['id'] == userID]
    if len(user) == 0:
        return "Error: no user found"
    
    userHash = df_hash[df_hash['id'] == userID]
    if len(userHash) == 0:
        return "Error: no hash found"
    
    userRequestInfo = request.json
    password = userRequestInfo['password']
    rid = userRequestInfo['RID']

    if userHash['RID'].values[0] != rid:
        return "Error: invalid RID"

    pwd = PasswordManager(password)
    hashJson = pwd.ToJson(userID)
    df_hash.loc[df_hash['id'] == userID, 'salt'] = hashJson['salt'].decode('utf-8')
    df_hash.loc[df_hash['id'] == userID, 'hash'] = hashJson['hash'].decode('utf-8')
    df_hash.loc[df_hash['id'] == userID, 'RID'] = ''.join(random.choice(string.ascii_uppercase) for i in range(30))
    writeData(df_hash, 'userhash.xlsx')

    return "success"

@app.route('/getUserHostedGames/<string:userID>')
def getUserHostedGames(userID=None):
    global df_users
    global df_games
    df_users['id'] = df_users['id'].astype(str)
    df_games['id'] = df_games['id'].astype(str)
    df_users['hosted games'] = df_users['hosted games'].astype(str)
    df_games['player list'] = df_games['player list'].astype(str)
    df_games['goalie list'] = df_games['goalie list'].astype(str)
    

    user = df_users[df_users['id'] == userID]
    if len(user) == 0:
        return jsonify([])
    
    userHostedGames = user['hosted games'].values[0]
    userHostedGameIDs = userHostedGames.split(';')

    hostedGameIDs = df_games[df_games['id'].isin(userHostedGameIDs)]

    hostedGameIDs['id'] = hostedGameIDs['id'].astype(str)
    hostedGameIDs['date'] = hostedGameIDs['date'].astype(str)
    hostedGameIDs['time'] = hostedGameIDs['time'].astype(str)
    return hostedGameIDs.to_json(orient='records')

@app.route('/isUserInGame/<string:userID>/<string:gameID>')
def isUserInGame(userID=None, gameID=None):
    global df_users
    user = df_users[df_users['id'] == userID]

    if len(user) == 0:
        return "no"

    userGames = user['games'].values[0]
    if CheckIfUserInGame(userGames, gameID):
        return "yes"
    else:
        return "no"
    
@app.route('/getEmailCredentials')
def getEmailCredentials():
    email = 'needbodies@outlook.com'
    password = 'Hockey12!'
    return jsonify({'email': email, 'password': password})

def filterByGame(df, gameID):
    if len(gameID) != 0:
        df = df[df['games'].str.contains(gameID)]
    return df

def formatDateTime(date, time):
    return date, time

def generateID(ids=None) -> str:
    filtered_ids = [int(i) for i in ids if len(str(i)) != 0]

    if len(filtered_ids) == 0:
        return 0
    else:
        return str(max(filtered_ids) + 1)

def CheckIfEmailPhoneUsed(data):
    global df_users
    if len(df_users[df_users['email'] == data[0]['email']]) != 0:
        return "email already exists"
    if len(df_users[df_users['phone'] == data[0]['phone']]) != 0:
        return "phone already exists"
    return None

def CheckIfUserInGame(userGames, gameID):
    return str.find(userGames, ';' + gameID + ';') != -1 or (len(userGames) >= len(gameID + ';') and userGames[:len(gameID) + 1] == gameID + ';')

def CheckIfGoalie(userID, gameID):
    global df_games
    df_games['id'] = df_games['id'].astype(str)
    df_games['goalie list'] = df_games['goalie list'].astype(str)
    game = df_games[df_games['id'] == gameID]
    if len(game) == 0:
        return False
    goalieList = game['goalie list'].values[0]
    return str.find(goalieList, ';' + userID + ';') != -1 or (len(goalieList) >= len(gameID + ';') and goalieList[:len(userID) + 1] == userID + ';')

def RemoveID(Id, Ids):
    tag = Id + ';'
    tagLength = len(Id + ';')

    pos = str.find(Ids, ';' + tag)
    if pos != -1:
        Ids = Ids[:(pos + 1)] + Ids[(pos + tagLength + 1):]
    elif len(Ids) >= tagLength and Ids[:tagLength] == tag:
        Ids = Ids[tagLength:]
    return Ids

def CountPlayers(gameID):
    global df_games
    game = df_games[df_games['id'] == gameID]
    if len(game) == 0:
        return 0
    playerList = game['player list'].values[0]
    return str.count(playerList, ';')

def CountGoalies(gameID):
    global df_games
    game = df_games[df_games['id'] == gameID]
    if len(game) == 0:
        return 0
    goalieList = game['goalie list'].values[0]
    return str.count(goalieList, ';')
    