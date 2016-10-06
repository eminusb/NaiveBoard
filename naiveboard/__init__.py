from flask import Flask, render_template, session, request, \
				  redirect, url_for, flash, get_flashed_messages
from naiveboard.database import engine, db_session, Base, \
							User, Post, Comment, Tag, \
							print_table, delete_all_rows, get_taginput
from sqlalchemy import desc
from naiveboard.nl2br import nl2br
from naiveboard.austinfunct import parse_taginput
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
	alltags = db_session.query(Tag).order_by('id')
	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()
	today = datetime.datetime.now().strftime("%y-%m-%d")	

	print_table(User)
	print_table(Post)
	print_table(Tag)

	return render_template('main.html', 
							entries=entries, alltags=alltags,
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
	alltags = db_session.query(Tag).order_by('id')
	return render_template('signup.html', alltags=alltags,
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
	alltags = db_session.query(Tag).order_by('id')
	return render_template('deleteuser.html', alltags=alltags,
							numusers=numusers, numposts=numposts)


@app.route('/AustinBoard/addpost', methods=['POST', 'GET'])
def addpost():	

	title = ""
	text = ""
	taginput = ""

	if request.method == 'POST':
		if session['logged_in']:
			title = request.form['title']
			text  = request.form['text']
			tags  = request.form['tags']
			tagtextlist = parse_taginput(tags)
			#tags  = parse_taginput(request.form['tags'])
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

			for tagtext in tagtextlist:
				if len(tagtext) > 20:
					error['tag'] = 'Too long tag (Under 20 characters)'
					flash('Too long tag (Under 20 characters)', 'addpost')
					break

			messages = get_flashed_messages(category_filter=['addpost'])
			if len(messages) == 0:
				post = Post(title, text, now)
				post.user = db_session.query(User).\
						filter(User.username==session['username']).one()
				for tagtext in tagtextlist:
					tag = db_session.query(Tag).filter(Tag.text==tagtext).first()
					if tag is None:
						tag = Tag(tagtext)
					tag.posts.append(post)	

				db_session.add(post)
				db_session.commit()
				return redirect(url_for('showentries'))

	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()
	alltags = db_session.query(Tag).order_by('id')
	return render_template('addpost.html', alltags=alltags,
							numusers=numusers, numposts=numposts,
							title=title, text=text, tags=taginput)


@app.route('/AustinBoard/modifypost_<post_id>', methods=['POST', 'GET'])
def modifypost(post_id):

	post = db_session.query(Post).filter(Post.id==post_id).one()
	title = post.title
	text = post.text
	taginput = get_taginput(post.tags)

	if request.method == 'POST':
		if session['logged_in'] and \
		   post.user.username==session['username']:
			title = request.form['title']
			text  = request.form['text']
			tags  = request.form['tags']
			tagtextlist = parse_taginput(tags)
			taginput = "; ".join(tagtextlist)

			if len(title) == 0:
				error['title'] = 'Empty title'
				flash('Empty title', 'addpost')
			elif len(title) > 50:				
				error['title'] = 'Too long title (Under 50 charaters)'
				flash('Too long title (Under 50 charaters)', 'modpost')
			
			if len(text) == 0:
				error['text'] = 'Empty text body'
				flash('Empty text', 'addpost')
			elif len(text) > 2000:
				error['text'] = 'Too long text (Under 2000 charaters)'
				flash('Too long text (Under 2000 charaters)', 'modpost')

			for tagtext in tagtextlist:
				if len(tagtext) > 20:
					error['tag'] = 'Too long tag (Under 20 characters)'
					flash('Too long tag (Under 20 characters)', 'modpost')
					break

			messages = get_flashed_messages(category_filter=['modpost'])
			if len(messages) == 0:
				now = datetime.datetime.now()
				post.title 	= title
				post.text 	= text
				post.date 	= now.strftime("%y-%m-%d")
				post.time	= now.strftime("%H:%M:%S")

				for tag in post.tags:
					post.tags.remove(tag)
					if len(tag.posts)==0:
						db_session.delete(tag)
				db_session.commit()

				for tagtext in tagtextlist:
					tag = db_session.query(Tag).filter(Tag.text==tagtext).first()
					if tag is None:
						tag = Tag(tagtext)
					tag.posts.append(post)

				db_session.add(post)
				db_session.commit()
				#return redirect(url_for('showentries'))
				return redirect(url_for('showpost', post_id=post_id))

	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()
	alltags = db_session.query(Tag).order_by('id')
	return render_template('modify.html', post_id=post_id, alltags=alltags,
							numusers=numusers, numposts=numposts,
							title=title, text=text, tags=taginput)


@app.route('/AustinBoard/showpost_<post_id>/popup=<popup>')
@app.route('/AustinBoard/showpost_<post_id>', defaults={'popup': False})
def showpost(post_id, popup):

	post = db_session.query(Post).filter(Post.id==post_id).first()

	alltags = db_session.query(Tag).order_by('id')
	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()	
	today = datetime.datetime.now().strftime("%y-%m-%d")
	
	return render_template('showpost.html', post=post, comtext='',
					numusers=numusers, numposts=numposts, 
					alltags=alltags, today=today, popup=popup)


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
	alltags = db_session.query(Tag).order_by('id')
	today = datetime.datetime.now().strftime("%y-%m-%d")
	
	return render_template('showpost.html', post=post, comtext=text,
					numusers=numusers, numposts=numposts, 
					alltags=alltags, today=today)
	#return redirect(url_for('showpost', post_id=post_id, comtext=text))


@app.route('/AustinBoard/deletepost_<post_id>')
def deletepost(post_id):
	post = db_session.query(Post).filter(Post.id==post_id).one()
	
	if session['logged_in']:
		if post.user.username==session['username']:
			tags = post.tags
			db_session.delete(post)
			db_session.commit()

			for tag in tags:
				if len(tag.posts)==0:
					db_session.delete(tag)
			db_session.commit()

			return redirect(url_for('showentries'))	

	return redirect(url_for('showpost', post_id=post_id))


@app.route('/AustinBoard/confirm_deletepost_<post_id>')
def confirm_deletepost(post_id):
	return redirect(url_for('showpost', post_id=post_id, popup=True))



@app.route('/AustinBoard/taggedlist_<tag_id>')
def showtaggedlist(tag_id):

	tag = db_session.query(Tag).filter(Tag.id==tag_id).first()
	entries = tag.posts

	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()
	alltags = db_session.query(Tag).order_by('id')
	today = datetime.datetime.now().strftime("%y-%m-%d")	

	return render_template('taggedlist.html', tag=tag,
							entries=entries, 
							numusers=numusers, numposts=numposts, 
							today=today, alltags=alltags)

@app.route('/test')
def test():
	return render_template('test.html')