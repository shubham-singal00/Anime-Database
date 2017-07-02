from flask import Flask
from flaskext.mysql import MySQL
app = Flask(__name__)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'acesps'
app.config['MYSQL_DATABASE_DB'] = 'Anime'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

def connection():
    conn =mysql.connect()
    c = conn.cursor()
    return c, conn

