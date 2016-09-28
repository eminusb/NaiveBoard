from flask import Flask, render_template, session, request, redirect, url_for
from naiveboard.database import engine, db_session, Base, User, Post, Comment
from sqlalchemy import desc
from naiveboard.nl2br import nl2br
import datetime

app = Flask(__name__)
#app.config.update(DEBUG=True)

app.jinja_env.filters['nl2br'] = nl2br

app.config.update(
	SECRET_KEY='AUSTINBOARD',
	USERNAME='admin',
	PASSWORD='default'
)



@app.before_request
def init_db():	
	Base.metadata.create_all(bind=engine)

@app.teardown_appcontext
def shutdown_session(exception=None):
	db_session.remove()



@app.route('/AustinBoard/main')
def showentries():

	entries = db_session.query(Post).order_by(desc('id'))
	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()
	today = datetime.datetime.now().strftime("%y-%m-%d")

	return render_template('main.html', entries=entries, 
							numusers=numusers, numposts=numposts, 
							today=today)


@app.route('/AustinBoard/login', methods=['POST'])
def login():

	error = None	
	query = db_session.query(User)
	user = query.filter(User.username==request.form['username']).first()
	if user == None:
		error = 'Invalid username'
	elif user.password != request.form['password']:
		error = 'Invalid password'
	else:
		session['logged_in'] = True
		session['username'] = request.form['username']

	return redirect(url_for('showentries', error=error))


@app.route('/AustinBoard/signup', methods=['POST', 'GET'])
def signup():

	error = None	
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		cfpassword = request.form['cfpassword']
	
		u = db_session.query(User).filter(User.username==username).first()		
		if not u is None:
			error = 'Existing username'
		elif len(username)<4 or 20<len(username):
			error = 'Invalid length of username'		
		elif len(password)<4 or 20<len(password):
			error = 'Invalid length of password'
		elif password != cfpassword:
			error = 'Invalid confirm password'
		else:
			user = User(username, password)
			db_session.add(user)
			db_session.commit()
			session['logged_in'] = True
			session['username'] = request.form['username']
			return redirect(url_for('showentries'))

	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()
	return render_template('signup.html', error=error,
							numusers=numusers, numposts=numposts)
	

@app.route('/AustinBoard/logout')
def logout():
	session['logged_in'] = False
	return redirect(url_for('showentries'))


@app.route('/AustinBoard/delete', methods=['POST', 'GET'])
def deleteuser():
	if request.method == 'POST':		
		query = db_session.query(User)
		user = query.filter(User.username==session['username']).one()
		if user.password == request.form['password']:
			db_session.delete(user)
			db_session.commit()
			session['logged_in'] = False
			return redirect(url_for('showentries'))

	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()	
	return render_template('delete.html', 
							numusers=numusers, numposts=numposts)


@app.route('/AustinBoard/addpost', methods=['POST', 'GET'])
def addpost():
	if request.method == 'POST':
		if session['logged_in']:
			title = request.form['title']
			text  = request.form['text']
			now = datetime.datetime.now()

			post = Post(title, text, now)			
			post.user = db_session.query(User).\
						filter(User.username==session['username']).one()

			db_session.add(post)
			db_session.commit()
			return redirect(url_for('showentries'))

	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()	
	return render_template('addpost.html', 
							numusers=numusers, numposts=numposts)


@app.route('/AustinBoard/showpost_<post_id>')
def showpost(post_id):
	post = db_session.query(Post).filter(Post.id==post_id).one()

	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()	
	today = datetime.datetime.now().strftime("%y-%m-%d")	

	return render_template('showpost.html', post=post,
					numusers=numusers, numposts=numposts, today=today)


@app.route('/AustinBoard/post_<post_id>_addcomment', methods=['POST', 'GET'])
def addcomment(post_id):
	post = db_session.query(Post).filter(Post.id==post_id).one()

	if request.method=='POST':
		if session['logged_in']:
			text = request.form['text']
			if not len(text)==0:
				now = datetime.datetime.now()
				comment = Comment(text, now)
			
				comment.user = db_session.query(User).\
						filter(User.username==session['username']).one()
				comment.post = post

				db_session.add(comment)
				db_session.commit()

	return redirect(url_for('showpost', post_id=post_id))			


@app.route('/AustinBoard/deletepost_<post_id>')
def deletepost(post_id):
	post = db_session.query(Post).filter(Post.id==post_id).one()

	if session['logged_in']:
		if post.user.username==session['username']:
			db_session.delete(post)
			db_session.commit()
			return redirect(url_for('showentries'))	

	return redirect(url_for('showpost', post_id=post_id))


@app.route('/AustinBoard/modifypost_<post_id>', methods=['POST', 'GET'])
def modifypost(post_id):
	post = db_session.query(Post).filter(Post.id==post_id).one()

	if request.method == 'POST':
		if session['logged_in']:
			if post.user.username==session['username']:
				title = request.form['title']
				text  = request.form['text']
				now = datetime.datetime.now()
				post = Post(title, text, now)
				
				db_session.add(post)
				db_session.commit()
				return redirect(url_for('showentries'))

	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()	
	return render_template('modify.html', post=post,
							numusers=numusers, numposts=numposts)
