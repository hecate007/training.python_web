#!/usr/bin/env python

from flask import Flask
from flask import g
from flask import render_template
from flask import abort
from flask import request
from flask import url_for
from flask import redirect
from flask import flash
import flask_login
import sqlite3
from contextlib import closing

class User(object):
 
    def __init__(self , id, username ,password):
        self.id = id
        self.username = username
        self.password = password
 
    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return unicode(self.id)
 
    def __repr__(self):
        return '<User %r>' % (self.username)

app = Flask(__name__)

app.config.from_pyfile('microblog.cfg')
# set the secret key.  keep this really secret:
app.secret_key = 'shhhh.. this is a secret'

#create login manager
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    con = get_database_connection()
    cur = con.execute('SELECT id, username, password FROM users WHERE id=? ORDER BY id DESC',[userid])
    userInfo = cur.fetchone()
    return User(*userInfo)
    
@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    username = request.form['username']
    password = request.form['password']
    try:
        con = get_database_connection()
        con.execute('insert into users (username, password) values (?, ?)',
                [username, password])
        con.commit()
        flash('User successfully registered')
    except sqlite3.Error:
        abort(500)
    return redirect(url_for('login'))
 
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']    
    con = get_database_connection()
    cur = con.execute('SELECT id, username, password FROM users WHERE username=? AND password=? ORDER BY id DESC',[username,password])
    userInfo = cur.fetchone()
    if not userInfo:
        flash('Username or Password is invalid' , 'error')
        return redirect(url_for('login'))
    registered_user = User(*userInfo)
    flask_login.login_user(registered_user)
    flash('Logged in successfully')
    return redirect(request.args.get('next') or url_for('show_entries'))
    
@app.route('/logout')
def logout():
    flask_login.logout_user()
    flash('Logged out successfully')
    return redirect(url_for('show_entries')) 

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_database_connection():
    db = getattr(g, 'db', None)
    if db is None:
        g.db = db = connect_db()
    return db


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def write_entry(title, text):
    con = get_database_connection()
    con.execute('insert into entries (title, text) values (?, ?)',
                [title, text])
    con.commit()


def get_all_entries():
    con = get_database_connection()
    cur = con.execute('SELECT title, text FROM entries ORDER BY id DESC')
    return [dict(title=row[0], text=row[1]) for row in cur.fetchall()]


@app.route('/')
def show_entries():
    entries = get_all_entries()
    username = ""
    loggedin = flask_login.current_user.is_authenticated()
    if loggedin:
        username = flask_login.current_user.username
    return render_template('show_entries.html', entries=entries,loggedin=loggedin,currentuser=username)


@app.route('/add', methods=['POST'])
@flask_login.login_required
def add_entry():
    try:
        write_entry(request.form['title'], request.form['text'])
        flash('Posted successfully')
    except sqlite3.Error:
        flash('Posted unsuccessfully')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run(debug=True)
