
import os
import datetime

from flask import redirect, url_for

from austinboard.database import engine, db_session, Base
from austinboard.app import app
from austinboard.users import login, signup, logout, deleteuser
from austinboard.post import showentries, addpost, modifypost, showpost, deletepost, confirm_deletepost, showtaggedlist, searchposts

from austinboard.comment import addcomment

@app.before_request
def init_db():	
	Base.metadata.create_all(bind=engine)

@app.teardown_appcontext
def shutdown_session(exception=None):
	db_session.remove()

@app.route('/')
def main():
	return redirect(url_for('showentries'))

