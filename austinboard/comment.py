# command.py
import os

from flask import Flask, render_template, session, request, \
				  redirect, url_for, flash, get_flashed_messages

from austinboard.app import app
from austinboard.database import db_session, User, Post, Comment
from austinboard.helper import update_stats

@app.route('/post_<post_id>_addcomment', methods=['POST', 'GET'])
def addcomment(post_id):

	post = db_session.query(Post).filter(Post.id==post_id).one()	
	text = ""
	popup = None

	if request.method=='POST':
		if session['logged_in']:
			text = request.form['text']

			if len(text)==0:
				flash('Empty comment', 'addcom')
			elif len(text)>140:
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

