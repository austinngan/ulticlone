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
announcement = ''

def islogged():
    print(session.keys())
    print('email' in session.keys())
    return 'email' in session.keys()

def isAdmin(email):
    if email in adminlist:
        return True
    return False

def get_db():
    DATABASE = os.path.join(os.path.dirname(__file__), "database.db")
    db = sqlite3.connect(DATABASE, check_same_thread=False, timeout=10)
    return db

@app.route("/", methods=['GET', 'POST'])
def home():
    global announcement
    if islogged() == True:
        if (request.method == 'POST'):
            announcement = request.form.get('announcement')
            return redirect('/')
        return render_template('home.html', user=session['name'], announcement = announcement)
    if (request.method == 'POST'):
            announcement = request.form.get('announcement')
            return redirect('/')
    return render_template('home.html', announcement = announcement)

@app.route("/logout",  methods=['GET', 'POST'])
def logout():
    # try except is for when user is not logged in and does /logout anyways and a KeyError occurs
    try:
        session.pop('email')
        session.pop('name')
    except KeyError:
        return redirect("/")
    return redirect("/")

#login takes the user object and sets cookies
@app.route("/login",  methods=['GET', 'POST'])
def login():
    #create users table so user can login
    db = get_db()
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
        name = request.form.get("name")
        password = request.form.get("password")
        print(email)

        #error handling for empty username
        if email == '':
            return render_template("login.html", error="Empty email, who are you?")

        db = get_db()
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
                c.execute("SELECT name FROM users WHERE email=?", (email,))
                session['name'] = c.fetchone()[0] #get first string of tuple
                print(session['name'])
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

        db = get_db()
        c = db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users(email TEXT, password TEXT, name TEXT, usauID INT, UNIQUE(email))")
        c.execute("SELECT email FROM users WHERE email=?", (email,))
        c.execute("INSERT INTO users(email, password, name, usauID) VALUES(?, ?, ?, ?)", (email, password, name, usau,))
        #temporary usauID is denoted by the 0

        #table for <year> rostering
        c.execute("CREATE TABLE IF NOT EXISTS {year}(email TEXT, name TEXT, team TEXT, usauID INT, present INT, absent INT)".format(year="A"+str(current_year)))
        #insert information into <year> table
        c.execute("INSERT INTO {year}(email, name, usauID, present, absent) VALUES(?, ?, ?, 0, 0)".format(year="A"+str(current_year)), (email, name, usau,))

        '''session['email'] = email
        session['name'] = name
        '''

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
        db = get_db()
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
    print(session['name'])
    return render_template("roster.html", user=session['name'], allYears = all_roster.keys(), allInfo = list(all_roster.values()), admin=False)
    #!!!!!!!!!! set admin to a variable NOT ALWAYS TRUE

@app.route("/draw", methods=['GET', 'POST'])
def draw():
    if not islogged():
        return redirect("/login")

    return render_template("draw.html", user=session['name']) #placeholder stuff

@app.route("/plays", methods=['GET', 'POST'])
def plays():
    if not islogged():
        return redirect("/login")
    return render_template("plays.html", user=session['name']) #placeholder stuff

@app.route("/attendance", methods=['GET', 'POST'])
def attendance():
    if not islogged():
        return redirect("/login")

    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM {currentYear}".format(currentYear="A"+str(current_year)))
    #(email TEXT, name TEXT, team TEXT, usauID INT, present INT, absent INT)
    info = c.fetchall()
    print(info)

    return render_template("attendance.html", user=session['name'], allInfo=info) #placeholder stuff

@app.route("/changeAttendance", methods=['GET', 'POST'])
def changeAttendance():
    #only if you are an admin can you update attendance
    #if isAdmin(session['email']):
    if True:
        db = get_db()
        c = db.cursor()
        c.execute("SELECT * FROM {currentYear}".format(currentYear="A"+str(current_year)))
        info = c.fetchall()
        print(info)

        return render_template("updateAttendance.html", allInfo=info)

    return redirect("/attendance")

@app.route("/updated", methods=['GET', 'POST'])
def updated():
    if (request.method == 'POST'):
        db = get_db()
        c = db.cursor()
        c.execute("SELECT email FROM {currentYear}".format(currentYear="A"+str(current_year)))
        #(email TEXT, name TEXT, team TEXT, usauID INT, present INT, absent INT)
        info = c.fetchall()

        for player in info:
            print(player[0])
            checkedOff = request.form.get(player[0])
            print(checkedOff)
            if (checkedOff == "on"): #checkbox is "on" if it was checked off
                #add to player's present in db
                c.execute("UPDATE {year} SET present=present+1 WHERE email=?".format(year="A"+str(current_year)), (player[0],))
                #c.execute("UPDATE A2021 SET present=present+1 WHERE email=?", (player[0],))
                print("finished")
            else:
                c.execute("UPDATE {currentYear} SET absent=absent+1 WHERE email=?".format(currentYear="A"+str(current_year)), (player[0],))
                print("lol")
                #add to player's absence

        db.commit()
        db.close()
    return redirect("/attendance")

@app.route("/tracker", methods=['GET', 'POST'])
def tracker():
    if not islogged():
        return redirect("/login")
    db = get_db()
    c = db.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS frees(period INT, isFree INT, name TEXT)")
    c.execute("SELECT * FROM frees WHERE isFree=1")
    info = c.fetchall()
    print(info)


    return render_template("tracker.html", user = session['name'], allFrees = info)

@app.route("/frees", methods=['GET', 'POST'])
def frees():
    if not islogged():
        return redirect("/login")

    print("post?")
    if (request.method == 'POST'):
        print("yes")
        db = get_db()
        c = db.cursor()

        for i in range(1,11):
            c.execute("DELETE FROM frees WHERE period=? AND name=?", (i, session['name']))

        pd1 = request.form.get("p1")
        pd2 = request.form.get("p2")
        pd3 = request.form.get("p3")
        pd4 = request.form.get("p4")
        pd5 = request.form.get("p5")
        pd6 = request.form.get("p6")
        pd7 = request.form.get("p7")
        pd8 = request.form.get("p8")
        pd9 = request.form.get("p9")
        pd10 = request.form.get("p10")

        c.execute("INSERT INTO frees(period, isFree, name) VALUES(?, ?, ?)", (1, pd1, session['name'],))
        c.execute("INSERT INTO frees(period, isFree, name) VALUES(?, ?, ?)", (2, pd2, session['name'],))
        c.execute("INSERT INTO frees(period, isFree, name) VALUES(?, ?, ?)", (3, pd3, session['name'],))
        c.execute("INSERT INTO frees(period, isFree, name) VALUES(?, ?, ?)", (4, pd4, session['name'],))
        c.execute("INSERT INTO frees(period, isFree, name) VALUES(?, ?, ?)", (5, pd5, session['name'],))
        c.execute("INSERT INTO frees(period, isFree, name) VALUES(?, ?, ?)", (6, pd6, session['name'],))
        c.execute("INSERT INTO frees(period, isFree, name) VALUES(?, ?, ?)", (7, pd7, session['name'],))
        c.execute("INSERT INTO frees(period, isFree, name) VALUES(?, ?, ?)", (8, pd8, session['name'],))
        c.execute("INSERT INTO frees(period, isFree, name) VALUES(?, ?, ?)", (9, pd9, session['name'],))
        c.execute("INSERT INTO frees(period, isFree, name) VALUES(?, ?, ?)", (10, pd10, session['name'],))
        db.commit()
        db.close()
        return redirect("/tracker")

    return render_template('frees.html', user=session['name'])

@app.route("/about", methods=['GET', 'POST'])
def about():

    return render_template("about.html", user=session['name'])

if __name__=="__main__":
    app.debug = True
    app.run()
