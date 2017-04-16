from flask import Flask,render_template,request,url_for,redirect,flash,session
from flaskext.mysql import MySQL
from passlib.hash import sha256_crypt
from wtforms import validators,Form,StringField,BooleanField,PasswordField
#from  import escape_string as thwart
import gc

mysql = MySQL()

app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'acesps'
app.config['MYSQL_DATABASE_DB'] = 'Anime'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#app.config['MYSQL_DATABASE_POST'] = '5000'


mysql.init_app(app)

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/dashboard/')
def show_user_profile():
   return render_template('dashboard.html')

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    name = StringField ('Name', [validators.Length(min=4, max=50)])
    password = PasswordField('New Password')
    confirm = PasswordField('Repeat Password',[validators.DataRequired(),
        validators.EqualTo('password', message='Passwords must match')
    ])

@app.route('/showSignUp')
def showSignUP():
    return render_template('signup.html')

@app.route('/register/',methods=['GET','POST'])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username = form.username.data
            name = form.name.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            conn=mysql.connect()
            c=conn.cursor()

            x = c.execute("SELECT * FROM User WHERE username ='" + username + "'")

            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('signup.html', form=form)

            else:
                c.execute("INSERT INTO User ( name , username, password )VALUES ('" + name + "','" + username + "', '" + password + "')" )

                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('dashboard'))

        return render_template("register.html", form=form)

    except Exception as e:
        return (str(e))

@app.route("/Authenticate")
def Authenticate():
    username = request.args.get('UserName')
    password = request.args.get('Password')
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from User where username='" + username + "' and password='" + password + "'")
    data = cursor.fetchone()
    if data is None:
        return "Username or Password is wrong"
    else:
        return "Logged in successfully"



    #accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)',
     #                         [validators.Required()])



if __name__ == '__main__':
    app.run()

