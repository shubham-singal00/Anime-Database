from flask import Flask,render_template,request,url_for,redirect,flash,session
from flaskext.mysql import MySQL
from passlib.hash import sha256_crypt
from wtforms import validators,Form,StringField,PasswordField
from functools import wraps
from dbconnect import connection
from querys import searchanime,showallanime,user_anime,insert_user_anime,likednow_user_anime,dellike_user_anime,delete_user_anime,user_genre
from report_making import make_report

# from  import escape_string as thwart
import gc

mysql = MySQL()

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_page'))

    return wrap


@app.route('/')
def homepage():
    session.clear()
    gc.collect()
    return render_template('index.html')

@app.route('/report/',methods=["GET"])
def report():
    make_report()
    return render_template('report.html')


@app.route('/save/', methods=["GET", "POST"])
@login_required
def save():
 try:
    animes=showallanime()
    user=user_anime()
    animeg=user_genre()

    if request.method == "POST":
        watched = request.form.getlist("watched")
        liked= request.form.getlist("liked")
        num = []
        for l in  watched:
            num.append((int)(l))
        watched = num
        div = []
        for l in liked:
            div.append((int)(l))
        liked= div
        watched2=[]
        watched5=[]
        watched6=[]
        liked2=[]
        liked3=[]
        liked4=[]
        for anime in user:
            if anime[0] in watched:
                    if anime[0]in liked and anime[1]!=1 :
                        liked3.append(anime[0])
                    if anime[0] not in liked  and anime[1]==1:
                        liked4.append(anime[0])
            if anime[0] not in watched:
                watched5.append(anime[0])
            watched6.append(anime[0])
        for anime in watched :
            if anime not in watched6:
               watched2.append(anime)
        for anime in liked:
            if anime in watched:
                if anime not in watched6:
                    liked2.append(anime)
        insert_user_anime(watched2,liked2)
        likednow_user_anime(liked3)
        dellike_user_anime(liked4)
        delete_user_anime(watched5)
        animes = showallanime()
        user = user_anime()


    gc.collect()
    return render_template('dashboard.html',animes=animes,user=user,animeg=animeg)
 except Exception as e:
    flash(e)
 return render_template('dashboard.html',animes=animes,user=user)



@app.route('/dashboard/', methods=["GET", "POST"])
@login_required
def dashboard():
    animes=showallanime()
    user=user_anime()
    animeg=user_genre()
    gc.collect()
    return render_template('dashboard.html',animes=animes,user=user,animeg=animeg)

@app.route('/delete/', methods=["GET", "POST"])
def delete():
    try:
        if request.method == "POST":
            c, conn = connection()
            c.execute("delete from User where USERNAME='" + session['username'] + "'")
            session.clear()
            gc.collect()
            return render_template('index.html')
        return  render_template('delete.html')

    except Exception as e:
        flash(e)
        error = "Invalid credentials, try again."
    return render_template("login.html",error=error)


@app.route('/login/', methods=["GET", "POST"])
def login_page():
    error = ''
    try:
        if request.method == "POST":
            c, conn = connection()
            c.execute("SELECT * FROM User WHERE username = (%s)",request.form['username'] )

            data = c.fetchone()[2]
            if data:
                if sha256_crypt.verify(request.form['password'], data):
                    print("hi")
                    session['logged_in'] = True
                    session['username'] = request.form['username']

                    flash("You are now logged in as " + request.form['username'] + " ")
                    return redirect(url_for("dashboard"))

                else:
                    print("hi2")
                    error = "Invalid credentials, try again."
                    flash(error)
            else :
                error = "Invalid credentials, try again."
                flash(error)

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


class passForm(Form):
    oldpass = StringField('Old Password', [validators.Length(min=4, max=45)])
    password = PasswordField('New Password',[validators.Length(min=4, max=45)])
    confirm = PasswordField('Repeat Password',[validators.DataRequired(),
        validators.EqualTo('password', message='Passwords must match')
    ])



@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('homepage'))

@app.route('/Password/',methods=['GET','POST'])
def password():
    try:
        form = passForm(request.form)

        if request.method == "POST" and form.validate():
            oldpass = form.oldpass.data
            password =sha256_crypt.encrypt((str(form.password.data)))
            c ,conn =connection()
            x = c.execute("SELECT * FROM User WHERE username ='" + session['username'] + "'")
            print(x)
            data = c.fetchone()[2]
            if data:
                if sha256_crypt.verify(oldpass, data):
                    print("hi")
                    c.execute("update User set password='" + password + "' where USERNAME='" + session['username'] +")" )

                else:
                    print("hi2")
                    error = "Invalid credentials, try again."
                    flash(error)
            else:
                error = "Invalid credentials, try again."
                flash(error)

        gc.collect()
        error="hi"
        return render_template("login.html", error=error)

    except Exception as e:
        flash(e)
    return render_template("dashboard.html")


@app.route('/register/',methods=['GET','POST'])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username = form.username.data
            name = form.name.data
            password =sha256_crypt.encrypt((str(form.password.data)))
            c ,conn =connection()
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


@app.route('/add_anime/',methods=['GET','POST'])
@login_required
def add_anime():
    error = ''
    try:
        if request.method == "POST":
            print("hi")
            c, conn = connection()
            print("hi1")
            x = c.execute("SELECT * FROM ANIME WHERE ANIMENAME ='" + request.form['animename'] + "'")
            print("hi2")
            print(x)
            if int(x) > 0:
                flash("The Anime is already in the database")
                return render_template('add_anime.html',error=error)
            else:
                print("hi3")
                print(request.form['animename'])
                print(request.form['num'])
                c.execute("INSERT INTO ANIME (ANIMENAME,EPISODES) VALUES ('" + request.form['animename'] + "'," + request.form['num'] + ")")
                print("hi4")
                conn.commit()
                c.execute("SELECT * FROM ANIME WHERE ANIMENAME = (%s)", request.form['animename'])
                print("h5")
                anime=c.fetchone()
                print(anime)
                for i in range(0,10):
                    c.execute("INSERT INTO ANIME_GENRE VALUES(" + str(anime[0]) + ",'" + request.form["genre " + str(i)] + "')")
                    conn.commit()
                print("hi7")
                flash("Anime  added to the database ")
                gc.collect()
                return redirect(url_for("dashboard"))


        return render_template("add_anime.html", error=error)

    except Exception as e:
        #flash(e)
        error = "Invalid credentials, try again."
    return render_template("add_anime.html", error=error)


@app.route('/search/', methods=['POST'])
def search():
    if request.method == "POST":        
        animes=searchanime(request.form['search'])
        user = user_anime()
    return render_template("dashboard.html",animes = animes,user=user )


@app.route("/Auth")
def asd():
    return render_template("temp.html")


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
    app.run(debug=True)


