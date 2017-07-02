from dbconnect import connection
import datetime
from flask import session

HTML_TEMPLATE ="""
{% extends "header.html" %}
{% block body %}
    <ul><li> Total Number of users: {{x}} </li>
<li> Total Number of Animes :{{y}} </li >
<li> Toatal Number of genre of Animes available:{{z}}</li>
<li>{{STR}}</li>
</ul>
{% endblock %}
"""

def make_report():
        try:
            c, conn = connection()
            x = c.execute("SELECT * FROM User")
            y = c.execute("SELECT *  FROM ANIME")
            z = c.execute("SELECT DISTINCT GENRE FROM ANIME_GENRE")
            userId = str(session['username'])
            c.close()
            conn.close()
            STR = "User: " + userId + " Generated Report at: " + str(datetime.datetime.now())

            filename = "report.html"
            savePath ='/home/acesps/PycharmProjects/Anime-Database/templates/' + filename
            saveData = (HTML_TEMPLATE.replace("{{x}}",str(x)).replace("{{y}}",str(y)).replace("{{z}}",str(z)).replace("{{STR}}",STR))
            template_save = open(savePath, "w")
            template_save.write(saveData)
            template_save.close()
        except Exception as e:
            print(str(e))
        return

