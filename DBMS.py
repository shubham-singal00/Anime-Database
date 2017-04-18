from flask import Flask,render_template,request,url_for,redirect,flash,session
from flaskext.mysql import MySQL
from passlib.hash import sha256_crypt
from wtforms import validators,Form,StringField,BooleanField,PasswordField
from functools import wraps

# from  import escape_string as thwart
import gc

mysql = MySQL()

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'


app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'acesps'
app.config['MYSQL_DATABASE_DB'] = 'Anime'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#app.config['MYSQL_DATABASE_POST'] = '5000'


mysql.init_app(app)

@app.route('/')
def homepage():
    session.clear()
    gc.collect()
    return render_template('index.html')


@app.route('/dashboard/')
def dashboard():
   return render_template('dashboard.html')


@app.route('/login/', methods=["GET", "POST"])
def login_page():
    error = ''
    try:
        if request.method == "POST":
            conn = mysql.connect()
            c = conn.cursor()
            c.execute("SELECT * FROM User WHERE username = (%s)",request.form['username'] )
            data = c.fetchone()[2]

            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']

                flash("You are now logged in as " + request.form['username'] + " ")
                return redirect(url_for("dashboard"))

            else:
                error = "Invalid credentials, try again."

        gc.collect()

        return render_template("login.html", error=error)

    except Exception as e:
        flash(e)
        error = "Invalid credentials, try again."
        return render_template("login.html", error=error)


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=45)])
    name = StringField ('Name', [validators.Length(min=4, max=45)])
    password = PasswordField('New Password',[validators.Length(min=4, max=45)])
    confirm = PasswordField('Repeat Password',[validators.DataRequired(),
        validators.EqualTo('password', message='Passwords must match')
    ])


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_page'))

    return wrap


@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('homepage'))


@app.route('/register/',methods=['GET','POST'])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username = form.username.data
            name = form.name.data
            password =sha256_crypt.encrypt((str(form.password.data)))
            conn=mysql.connect()
            c=conn.cursor()
            print(password)
            x = c.execute("SELECT * FROM User WHERE username ='" + username + "'")
            print(x)
            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)

            else:
                c.execute("INSERT INTO User ( name , username, password )VALUES ('" + name + "','" + username + "', '" + password + "')")
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


