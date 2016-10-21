# users.py

import os
import hashlib

from flask import Flask, render_template, session, request, \
				  redirect, url_for, flash, get_flashed_messages

from austinboard.app import app
from austinboard.database import db_session, User
from austinboard.helper import update_stats

def hash_password(password):
	salt = os.environ.get('SALT', '')
	db_password = password + salt
	h = hashlib.md5(db_password.encode())
	#h = hashlib.md5(password.encode())
	return h.hexdigest()


@app.route('/login', methods=['POST'])
def login():
	popup = None
	query = db_session.query(User)
	user = query.filter(User.username==request.form['username']).first()

	if user == None:
		flash('Invalid username', 'login')
		popup = 'alert'	
	elif user.password != hash_password(request.form['password']):
		flash('Invalid password', 'login')
		popup = 'alert'
	else:
		session['logged_in'] = True
		session['username'] = request.form['username']
	
	return redirect(url_for('showentries', popup=popup))



@app.route('/signup', methods=['POST', 'GET'])
def signup():

	popup = None

	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		cfpassword = request.form['cfpassword']
	
		u = db_session.query(User).filter(User.username==username).first()		
		if not u is None:
			flash('Existing username', 'signup')
		else:
			if len(username.split()) != 1:
				flash('Whitespace is Not allowed in a valid username', 'signup')
			elif len(username)<4 or 20<len(username):
				flash('Invalid length of username', 'signup')
			elif len(password)<4 or 20<len(password):
				flash('Invalid length of password', 'signup')
			elif password != cfpassword:
				flash('Invalid confirm password', 'signup')
		
		messages = get_flashed_messages(category_filter=['signup'])
		if len(messages) == 0:			
			user = User(username, hash_password(password))
			db_session.add(user)
			db_session.commit()
			session['logged_in'] = True
			session['username'] = request.form['username']
			return redirect(url_for('showentries'))
		else:
			popup = 'alert'

	ctx = update_stats()
	ctx['popup'] = popup
	return render_template('signup.html', **ctx)
	

@app.route('/logout')
def logout():
	session['logged_in'] = False
	return redirect(url_for('showentries'))


@app.route('/deleteuser', methods=['POST', 'GET'])
def deleteuser():

	popup = None

	if request.method == 'POST':		
		query = db_session.query(User)
		user = query.filter(User.username==session['username']).one()
		if user.password == request.form['password']:
			db_session.delete(user)
			db_session.commit()
			session['logged_in'] = False
			return redirect(url_for('showentries'))
		else:
			flash('Wrong password', 'deluser')
			popup = 'alert'

	ctx = update_stats()
	ctx['popup'] = popup
	return render_template('deleteuser.html', **ctx)


