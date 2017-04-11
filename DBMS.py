from flask import Flask , render_template,json,request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/user/<username>')
def show_user_profile(username):
    return 'user %s' %username

@app.route('/showSignUp')
def showSignUP():
    return render_template('signup.html')

@app.route('/signUp',methods=['POST'])
def signUp():

    _name = request.form['inputName']
    _email= request.form['inputEmail']
    _password = request.form['inputPassword']

    if _name and _email and _password:
        return json.dumps({'html': '<span>All fields good !!</span>'})
    else:
        return json.dumps({'html': '<span>Enter the required fields</span>'})



if __name__ == '__main__':
    app.run()

