from flask import Flask, render_template, session, request, redirect, url_for, flash, get_flashed_messages
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

error = dict()

@app.before_request
def init_db():	
	Base.metadata.create_all(bind=engine)	

@app.teardown_appcontext
def shutdown_session(exception=None):
	db_session.remove()



@app.route('/AustinBoard/main')
def showentries():

	#loginerror = request.args.get('loginerror')
	#posterror = request.args.get('posterror')
	#error = { 'login': loginerror, 'post': posterror }

	entries = db_session.query(Post).order_by(desc('id'))
	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()
	today = datetime.datetime.now().strftime("%y-%m-%d")	
	users = db_session.query(User).all()
	print('\n')
	for user in users:
		print(user)
	print('\n')
	return render_template('main.html', 
							entries=entries, 
							numusers=numusers, numposts=numposts, 
							today=today)


@app.route('/AustinBoard/login', methods=['POST'])
def login():

	query = db_session.query(User)
	user = query.filter(User.username==request.form['username']).first()

	if user == None:
		error['login'] = 'Invalid username'
		flash('Invalid username', 'login')
	elif user.password != request.form['password']:		
		error['login'] = 'Invalid password'
		flash('Invalid username', 'login')
	else:
		session['logged_in'] = True
		session['username'] = request.form['username']
	
	print("is logged in?")
	print(session['logged_in'])
	return redirect(url_for('showentries'))


@app.route('/AustinBoard/signup', methods=['POST', 'GET'])
def signup():

	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		cfpassword = request.form['cfpassword']
	
		u = db_session.query(User).filter(User.username==username).first()		
		if not u is None:
			error['signup'] = 'Existing username'
			flash('Existing username', 'signup')
		else:
			if len(username.split()) != 1:
				error['signup'] = 'Whitespace is Not allowed in a valid username'
				flash('Whitespace is Not allowed in a valid username', 'signup')
			elif len(username)<4 or 20<len(username):
				error['signup'] = 'Invalid length of username'
				flash('Invalid length of username', 'signup')
			elif len(password)<4 or 20<len(password):
				error['signup'] = 'Invalid length of password'
				flash('Invalid length of password', 'signup')
			elif password != cfpassword:
				error['signup'] = 'Invalid confirm password'
				flash('Invalid confirm password', 'signup')
		
		messages = get_flashed_messages(category_filter=['signup'])
		if len(messages) == 0:
			user = User(username, password)
			db_session.add(user)
			db_session.commit()
			session['logged_in'] = True
			session['username'] = request.form['username']
			return redirect(url_for('showentries'))

	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()
	return render_template('signup.html', 
							numusers=numusers, numposts=numposts)
	

@app.route('/AustinBoard/logout')
def logout():
	session['logged_in'] = False
	return redirect(url_for('showentries'))


@app.route('/AustinBoard/deleteuser', methods=['POST', 'GET'])
def deleteuser():

	if request.method == 'POST':		
		query = db_session.query(User)
		user = query.filter(User.username==session['username']).one()
		if user.password == request.form['password']:
			db_session.delete(user)
			db_session.commit()
			session['logged_in'] = False
			return redirect(url_for('showentries'))
		else:
			error['deluser'] = 'Wrong password'
			flash('Wrong password', 'deluser')

	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()	
	return render_template('deleteuser.html', 
							numusers=numusers, numposts=numposts)


@app.route('/AustinBoard/addpost', methods=['POST', 'GET'])
def addpost():	

	title = ""
	text = ""
	if request.method == 'POST':
		if session['logged_in']:
			title = request.form['title']
			text  = request.form['text']
			now = datetime.datetime.now()

			if len(title) == 0:
				error['title'] = 'Empty title'
				flash('Empty title', 'addpost')
			elif len(title) > 50:				
				error['title'] = 'Too long title (Under 50 charaters)'
				flash('Too long title (Under 50 charaters)', 'addpost')
			
			if len(text) == 0:
				error['text'] = 'Empty text body'
				flash('Empty text', 'addpost')
			elif len(text) > 2000:
				error['text'] = 'Too long text (Under 2000 charaters)'
				flash('Too long text (Under 2000 charaters)', 'addpost')

			messages = get_flashed_messages(category_filter=['addpost'])
			if len(messages) == 0:
				post = Post(title, text, now)			
				post.user = db_session.query(User).\
						filter(User.username==session['username']).one()

				db_session.add(post)
				db_session.commit()
				return redirect(url_for('showentries'))

	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()	
	return render_template('addpost.html', 
							numusers=numusers, numposts=numposts,
							title=title, text=text)


@app.route('/AustinBoard/showpost_<post_id>')
def showpost(post_id):
	post = db_session.query(Post).filter(Post.id==post_id).one()	
	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()	
	today = datetime.datetime.now().strftime("%y-%m-%d")
	
	return render_template('showpost.html', post=post, comtext='',
					numusers=numusers, numposts=numposts, today=today)


@app.route('/AustinBoard/post_<post_id>_addcomment', methods=['POST', 'GET'])
def addcomment(post_id):
	post = db_session.query(Post).filter(Post.id==post_id).one()	
	text = ""

	if request.method=='POST':
		if session['logged_in']:
			text = request.form['text']

			if len(text)==0:
				error['comment'] = 'Empty comment'
				flash('Empty comment', 'addcom')
			elif len(text)>140:
				error['comment'] = 'Too long comment (Under 140 characters)'
				flash('Too long comment (Under 140 characters)', 'addcom')

			messages = get_flashed_messages(category_filter=['addcom'])
			print(messages)
			if len(messages) == 0:
				now = datetime.datetime.now()
				comment = Comment(text, now)
				comment.user = db_session.query(User).\
						filter(User.username==session['username']).one()
				comment.post = post
				db_session.add(comment)
				db_session.commit()
	
	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()	
	today = datetime.datetime.now().strftime("%y-%m-%d")
	
	return render_template('showpost.html', post=post, comtext=text,
					numusers=numusers, numposts=numposts, today=today)
	#return redirect(url_for('showpost', post_id=post_id, comtext=text))


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
	title = post.title
	text = post.text

	if request.method == 'POST':
		if session['logged_in'] and \
		   post.user.username==session['username']:
			title = request.form['title']
			text  = request.form['text']

			if len(title) == 0:
				error['title'] = 'Empty title'
				flash('Empty title', 'modpost')
			elif len(title) > 50:				
				error['title'] = 'Too long title (Under 50 charaters)'
				flash('Too long title (Under 50 charaters)', 'modpost')
			
			if len(text) == 0:
				error['text'] = 'Empty text body'
				flash('Empty text', 'modpost')
			elif len(text) > 2000:
				error['text'] = 'Too long text (Under 2000 charaters)'
				flash('Too long text (Under 2000 charaters)', 'modpost')

			messages = get_flashed_messages(category_filter=['modpost'])
			if len(messages) == 0:
				now = datetime.datetime.now()
				post.title 	= title
				post.text 	= text
				post.date 	= now.strftime("%y-%m-%d")
				post.time	= now.strftime("%H:%M:%S")				
				db_session.add(post)
				db_session.commit()
				return redirect(url_for('showentries'))

	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()	
	return render_template('modify.html', post_id=post_id,
							title=title, text=text,
							numusers=numusers, numposts=numposts)
