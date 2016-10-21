# post.py

import os
import datetime

from flask import Flask, render_template, session, request, \
				  redirect, url_for, flash, get_flashed_messages

from austinboard.app import app
from austinboard.database import db_session, User, Post, Tag, \
								 print_table
from austinboard.helper import update_stats



def get_taginput(tags):
	tagtextlist = list()
	for tag in tags:
		tagtextlist.append(tag.text)
	return "; ".join(tagtextlist)

def parse_taginput(taginput):
	taglist = list()	
	for tag in taginput.split(';'):
		tag = tag.strip()
		if tag != "" and (not tag in taglist):
			taglist.append(tag)	
	return taglist



@app.route('/main/popup=<popup>')
@app.route('/main/', defaults={'popup': None})
def showentries(popup):

	print_table(User)
	#print_table(Post)
	#print_table(Tag)
	
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
				flash('Empty title', 'addpost')
			elif len(title) > 50:				
				flash('Too long title (Under 50 charaters)', 'addpost')
			
			if len(text) == 0:
				flash('Empty text', 'addpost')
			elif len(text) > 2000:
				flash('Too long text (Under 2000 charaters)', 'addpost')

			for tagtext in tagtextlist:
				if len(tagtext) > 20:
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
				flash('Empty title', 'addpost')
			elif len(title) > 50:				
				flash('Too long title (Under 50 charaters)', 'modpost')
			
			if len(text) == 0:
				flash('Empty text', 'addpost')
			elif len(text) > 2000:
				flash('Too long text (Under 2000 charaters)', 'modpost')

			for tagtext in tagtextlist:
				if len(tagtext) > 20:
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


def search_posts_with_keyword(keyword):
	posts = []
	allposts = db_session.query(Post).order_by(desc('id'))
	for post in allposts:
		if (post.title).find(keyword) != -1 \
				or (post.text).find(keyword) != -1:
				posts.append(post)				
	return posts


@app.route('/search', methods=['GET'])
def searchposts():
	# get input
	keyword = request.args.get('keyword')

	# compute
	posts = search_posts_with_keyword(keyword)

	# template context
	ctx = update_stats()
	ctx['keyword'] = keyword
	ctx['posts'] = posts	
	return render_template('searchposts.html', **ctx)

