from os import urandom
from flask import Flask, render_template, request, session, redirect
import sqlite3, os.path
import json
import urllib
import random

app = Flask(__name__)
app.secret_key = urandom(32)

current_year = 2021 #is mutable; can increment
starting_year = 2021 #not mutable
adminlist = ['admin@admin.com']

def islogged():
    print(session.keys())
    return 'email' in session.keys()

def isAdmin(email):
    if email in adminlist:
        return True
    return False

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route("/logout",  methods=['GET', 'POST'])
def logout():
    # try except is for when user is not logged in and does /logout anyways and a KeyError occurs
    try:
        session.pop('email')
    except KeyError:
        return redirect("/")
    return redirect("/")

#login takes the user object and sets cookies
@app.route("/login",  methods=['GET', 'POST'])
def login():
    #create users table so user can login
    db = sqlite3.connect("users.db")
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users(email TEXT, password TEXT, name TEXT, usauID INT, UNIQUE(email))")
    db.commit()
    db.close()
    return render_template('login.html')


# authentication of login; verifies login information
@app.route("/auth", methods=['GET', 'POST'])
def auth():
    print("post?")
    if (request.method == 'POST'):
        print("yes")

        email = request.form.get("email")
        password = request.form.get("password")
        print(email)

        #error handling for empty username
        if email == '':
            return render_template("login.html", error="Empty email, who are you?")

        db = sqlite3.connect('users.db')
        c = db.cursor()
        #in case users goes straight to /register w/o running /login code
        c.execute("CREATE TABLE IF NOT EXISTS users(email TEXT, password TEXT, name TEXT, usauID INT, UNIQUE(email))")
        c.execute("SELECT email FROM users WHERE email=? ", (email,))
        # username inputted by user is not found in database
        if c.fetchone() == None:
            return render_template("login.html", error="Wrong email, double check spelling or register")
        # username is found
        else:
            c.execute("SELECT password FROM users WHERE email=? ", (email,))
            # password associated with username in database does not match password inputted

            #c.fetchone() returns a tuple with the password
            #first convert the tuple into the password string only, then compare
            if ( ''.join(c.fetchone()) ) != password:
                return render_template("login.html", error="Wrong password")
            # password is correct
            else:
                session['email'] = email
                print(session['email'])
        db.close()
        print("redirecting")
        return redirect('/')

    #get method
    else:
        return redirect('/login')

@app.route("/register", methods=['GET', 'POST'])
def register():

    if islogged():
        return redirect("/")

    if (request.method == 'POST'):
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        reenterpasswd = request.form.get("reenterpasswd")
        usau = request.form.get("usauID")

        #error handling
        if email == '':
            return render_template("register.html", error="Empty username, who are you?")
        elif password == '':
            return render_template("register.html", error="Empty password, you'll get hacked y'know :)")
        elif password != reenterpasswd:
            return render_template("register.html", error="Passwords don't match")
        #username can have leading numbers and special chars in them

        db = sqlite3.connect('users.db')
        c = db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users(email TEXT, password TEXT, name TEXT, usauID INT, UNIQUE(email))")
        c.execute("SELECT email FROM users WHERE email=?", (email,))
        c.execute("INSERT INTO users(email, password, name, usauID) VALUES(?, ?, ?, ?)", (email, password, name, usau,))
        #temporary usauID is denoted by the 0

        #table for <year> rostering
        c.execute("CREATE TABLE IF NOT EXISTS {year}(email TEXT, name TEXT, team TEXT, usauID INT)".format(year="A"+str(current_year)))
        #insert information into <year> table
        c.execute("INSERT INTO {year}(email, name, usauID) VALUES(?, ?, ?)".format(year="A"+str(current_year)), (email, name, usau,))

        session['email'] = email

        db.commit()
        db.close()
        print("reee")
        return redirect("/login")

    else:
        return render_template("register.html") # , test='&quot'

@app.route("/roster", methods=['GET', 'POST'])
def roster():
    if not islogged():
        return redirect("/login")

    all_roster = {} #dictionary of all the roster info; {2022: [name, g/b, usauID]}
    temp_current_year = current_year #mutate the current_year info without actually changing the current_year
    while temp_current_year >= starting_year:
        db = sqlite3.connect('users.db')
        c = db.cursor()
        c.execute("SELECT * FROM {currentYear}".format(currentYear="A"+str(temp_current_year)))
        info = c.fetchall()

        #add the info into the dictionary
        all_roster[temp_current_year] = info
        #decrement current_year
        temp_current_year -= 1

    print(all_roster) #{2021: [('h@gmail.com', '123', 'han', None, None)], [('yo@gmail.com', '123', etc)]
                      # 2022: [('a@gmail.com',)]}
    print(all_roster.values())
    print(list(all_roster.values())[0])
    return render_template("roster.html", allYears = all_roster.keys(), allInfo = list(all_roster.values()), admin=True)
    #return render_template("roster.html", allInfo = all_roster, admin = True)
    #!!!!!!!!!! set admin to a variable NOT ALWAYS TRUE

@app.route("/draw", methods=['GET', 'POST'])
def draw():
    if not islogged():
        return redirect("/login")

    return render_template("draw.html") #placeholder stuff

@app.route("/attendance", methods=['GET', 'POST'])
def attendance():
    if not islogged():
        return redirect("/login")

    return render_template("attendance.html") #placeholder stuff

@app.route("/tracker", methods=['GET', 'POST'])
def tracker():
    if not islogged():
        return redirect("/login")
    return render_template("tracker.html")

@app.route("/about", methods=['GET', 'POST'])
def about():

    return render_template("about.html")

if __name__=="__main__":
    app.debug = True
    app.run()
