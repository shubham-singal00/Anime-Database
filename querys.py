from dbconnect import connection
from flask import session
import gc
c ,conn =connection()

#anime gerne,Anime
def execute_query(sqlQ):
    animes = []
    c.execute(sqlQ)
    data = c.fetchall()
    for row in data:
        anime = [row[0],row[1], row[2],[]]
        c.execute("SELECT GENRE FROM ANIME_GENRE WHERE ANIME_ID='" + str(row[0]) + "'")
        genres=c.fetchall()
        for genre in genres:
            anime[3].append(genre[0])
        animes.append(anime)
    conn.commit()
    gc.collect()

    return animes


def showallanime():
    sqlQ = "select * from ANIME"
    return execute_query(sqlQ)


def searchanime(query):
    sqlQ = "select * from ANIME where ANIMENAME LIKE '%" + str(query) + "%'"
    return execute_query(sqlQ)

#user_anime

def user_anime():
    sqlQ = "select ANIME_ID,LIKED from USER_ANIME where USERNAME ='" + session['username'] + "'"
    c.execute(sqlQ)
    user=[]
    data= c.fetchall()
    for row in data:
        tup=[row[0],row[1]]
        user.append(tup)
    conn.commit()
    gc.collect()

    return user


#user_anime
def insert_user_anime(watched, liked):
    for anime_id in watched:
        if anime_id in liked:
            sqlQ = "insert into USER_ANIME VALUES ('" + session['username'] + "'," + str(anime_id) + "," + str(1) + ")"
        else:
            sqlQ = "insert into USER_ANIME VALUES ('" + session['username'] + "'," + str(anime_id) + ",NULL)"
        c.execute(sqlQ)
        conn.commit()

    gc.collect()
    return 1


def  likednow_user_anime(liked):
    for anime_id in liked:
        sqlQ = "update USER_ANIME set LIKED=1 where USERNAME='" + session['username'] + "' and ANIME_ID=" + str(anime_id)
        c.execute(sqlQ)
        conn.commit()
    gc.collect()


def  dellike_user_anime(liked):
    for anime_id in liked:
        sqlQ = "update USER_ANIME set LIKED=NULL where USERNAME='" + session['username'] + "' and ANIME_ID=" + str(anime_id)
        c.execute(sqlQ)
        conn.commit()
    gc.collect()


def  delete_user_anime(watched):
     for anime_id in watched:
        sqlQ ="delete from USER_ANIME where USERNAME='" + session['username'] + "' and ANIME_ID=" + str(anime_id)
        c.execute(sqlQ)
        conn.commit()
     gc.collect()



#user_gerne
def user_genre():
    c.execute("SELECT GENRE FROM USER_GENRE WHERE USERNAME='" + session['username'] + "'")
    genres = c.fetchall()
    animeg=[]
    for genre in genres:
        animeg.append(genre[0])
    return animeg