from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from functools import wraps
import requests
import json
import sqlite3

app = Flask(__name__)

app.secret_key = "my precious"
app.db = "sample.db"


# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

@app.route('/welcome')
def welcome():
	return render_template('welcome.html')

#home page route
@app.route('/')
@app.route('/home')
@login_required
def home():
	g.db = connect_db()
	cur = g.db.execute('select * from posts')
	posts = [dict(title=row[0], description=row[1]) for row in cur.fetchall()]
	print posts
	g.db.close()
	return render_template('index.html', posts=posts)  # render a template


@app.route('/login', methods=['GET','POST'])
def login():
	error = None
	if(request.method == "POST"):
		if(request.form['username'] != "admin" or request.form['password'] != "admin"):
			error = "Invalid credentials. Please provide valid info!"
		else:
			session['logged_in'] = True
			flash("You were just logged in!")
			return redirect(url_for('home'))
	elif "logged_in" in session:
		return redirect(url_for('home'))	
	return render_template('login.html', error = error)


@app.route('/logout')
@login_required
def logout():
	session.pop('logged_in', None)
	flash("You were just logged out!")
	return redirect(url_for('welcome'))



#############################################
##	 Movie Crawler for Cinema Guide	App	   ##
#############################################
@app.route('/movies')
@login_required
def movies():
	params = {
  	"api_key": "tEZQKzFNhBcq_xHn7ZJ5CLlL",
  	"offset": "0"
	}
	r = requests.get('https://www.parsehub.com/api/v2/projects/txhqg7TVzQRtVBtuzvkv4BGF/last_ready_run/data', params=params)
	
	return render_template('movies.html', movies=json.loads(r.text)['selection1'])
	#return r.text


def connect_db():
	return sqlite3.connect(app.db)



if __name__ == '__main__':
	app.run(debug = True)
