from flask import Flask, render_template, session, request, \
				  redirect, url_for, flash, get_flashed_messages
from austinboard.database import engine, db_session, Base, \
							User, Post, Comment, Tag, \
							print_table, delete_all_rows, get_taginput
from sqlalchemy import desc
from austinboard.nl2br import nl2br
import datetime
import os


app = Flask(__name__)
app.config.update(
	SECRET_KEY='DRAOBNITSUA'
)

app.jinja_env.filters['nl2br'] = nl2br

error = dict()


@app.before_request
def init_db():	
	Base.metadata.create_all(bind=engine)	


@app.teardown_appcontext
def shutdown_session(exception=None):
	db_session.remove()



def update_stats():	
	entries = db_session.query(Post).order_by(desc('id'))
	alltags = db_session.query(Tag).order_by('id')
	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()
	today = datetime.datetime.now().strftime("%y-%m-%d")
	return dict(entries=entries, alltags=alltags,
				numusers=numusers, numposts=numposts, today=today)


def parse_taginput(taginput):
	taglist = list()	
	for tag in taginput.split(';'):
		tag = tag.strip()
		if tag != "" and (not tag in taglist):
			taglist.append(tag)	
	return taglist



@app.route('/login', methods=['POST'])
def login():

	popup = None
	query = db_session.query(User)
	user = query.filter(User.username==request.form['username']).first()

	if user == None:
		error['login'] = 'Invalid username'
		flash('Invalid username', 'login')
		popup = 'alert'
	elif user.password != request.form['password']:		
		error['login'] = 'Invalid password'
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
			error['deluser'] = 'Wrong password'
			flash('Wrong password', 'deluser')
			popup = 'alert'

	ctx = update_stats()
	ctx['popup'] = popup
	return render_template('deleteuser.html', **ctx)



@app.route('/')
def main():
	return redirect(url_for('showentries'))

	

@app.route('/main/popup=<popup>')
@app.route('/main/', defaults={'popup': None})
def showentries(popup):
	'''
	print_table(User)
	print_table(Post)
	print_table(Tag)
	'''
	ctx = update_stats()
	ctx['popup'] = popup
	return render_template('main.html', **ctx)



@app.route('/addpost', methods=['POST', 'GET'])
def addpost():	

	title = ""
	text = ""
	taginput = ""
	popup = None

	if request.method == 'POST':
		if session['logged_in']:
			title = request.form['title']
			text  = request.form['text']
			tagtextlist = parse_taginput(request.form['tags'])
			taginput = "; ".join(tagtextlist)
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
					error['tag'] = 'Too long tag(s) (Under 20 characters)'
					flash('Too long tag(s) (Under 20 characters)', 'addpost')
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
				return redirect(url_for('showpost', post_id=post.id))
			else:
				popup = 'alert'

	ctx = update_stats()
	ctx['title'] = title
	ctx['text'] = text
	ctx['tags'] = taginput
	ctx['popup'] = popup
	return render_template('addpost.html', **ctx)



@app.route('/modifypost_<post_id>', methods=['POST', 'GET'])
def modifypost(post_id):

	post = db_session.query(Post).filter(Post.id==post_id).one()
	title = post.title
	text = post.text
	taginput = get_taginput(post.tags)
	popup = None

	if request.method == 'POST':
		if session['logged_in'] and \
		   post.user.username==session['username']:
			title = request.form['title']
			text  = request.form['text']
			tagtextlist = parse_taginput(request.form['tags'])
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
					error['tag'] = 'Too long tag(s) (Under 20 characters)'
					flash('Too long tag(s) (Under 20 characters)', 'modpost')
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
				return redirect(url_for('showpost', post_id=post_id))
			else:
				popup = 'alert'

	ctx = update_stats()
	ctx['post_id'] = post_id
	ctx['title'] = title
	ctx['text'] = text
	ctx['tags'] = taginput
	ctx['popup'] = popup
	return render_template('modpost.html', **ctx)



@app.route('/showpost_<post_id>/popup=<popup>')
@app.route('/showpost_<post_id>', defaults={'popup': None})
def showpost(post_id, popup):

	post = db_session.query(Post).filter(Post.id==post_id).first()

	ctx = update_stats()
	ctx['post'] = post
	ctx['popup'] = popup	
	return render_template('showpost.html', **ctx)

'''
def required_login(endpoint):
	def wrap(func):
		def decorated_func(*args, **kwargs):
			if session['logged_in']:
				func(*args, **kwargs)
			else:
				return redirect(url_for(endpoint, post_id=kwargs['post_id']))
		return decorated_func
	return wrap
'''

@app.route('/post_<post_id>_addcomment', methods=['POST', 'GET'])
def addcomment(post_id):

	post = db_session.query(Post).filter(Post.id==post_id).one()	
	text = ""
	popup = None

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
			if len(messages) == 0:				
				now = datetime.datetime.now()
				comment = Comment(text, now)
				comment.user = db_session.query(User).\
						filter(User.username==session['username']).one()
				comment.post = post
				db_session.add(comment)
				db_session.commit()
				text = ""
			else:
				popup = 'alert'

	ctx = update_stats()
	ctx['post'] = post
	ctx['comtext'] = text
	ctx['popup'] = popup
	return render_template('showpost.html', **ctx)



@app.route('/deletepost_<post_id>')
def deletepost(post_id):
	post = db_session.query(Post).filter(Post.id==post_id).one()
	
	if session['logged_in'] \
	   and post.user.username==session['username']:
		tags = post.tags
		db_session.delete(post)
		db_session.commit()

		for tag in tags:
			if len(tag.posts)==0:
				db_session.delete(tag)
		
		db_session.commit()
		return redirect(url_for('showentries'))	

	return redirect(url_for('showpost', post_id=post_id))



@app.route('/confirm_deletepost_<post_id>')
def confirm_deletepost(post_id):
	return redirect(url_for('showpost', post_id=post_id, popup='confirm'))



@app.route('/taggedlist_<tag_id>')
def showtaggedlist(tag_id):

	tag = db_session.query(Tag).filter(Tag.id==tag_id).first()
	
	ctx = update_stats()
	ctx['tag'] = tag
	return render_template('taggedlist.html', **ctx)



@app.route('/search', methods=['POST', 'GET'])
def searchposts():

	if request.method == 'POST':
		posts = list()
		keyword = request.form['keyword']
		allposts = db_session.query(Post).order_by(desc('id'))
		for post in allposts:
			if (post.title).find(keyword) != -1 \
				or (post.text).find(keyword) != -1:
				posts.append(post)
		
		ctx = update_stats()
		ctx['keyword'] = keyword
		ctx['posts'] = posts
		return render_template('searchposts.html', **ctx)

	return redirect(url_for('showentries'))