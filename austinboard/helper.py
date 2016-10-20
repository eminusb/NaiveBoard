
import datetime

from sqlalchemy import desc

from austinboard.database import db_session, User, Post, Comment, Tag

def update_stats():
	entries = db_session.query(Post).order_by(desc('id'))
	alltags = db_session.query(Tag).order_by('id')
	numposts = db_session.query(Post).count()
	numusers = db_session.query(User).count()
	today = datetime.datetime.now().strftime("%y-%m-%d")
	return dict(entries=entries, alltags=alltags,
				numusers=numusers, numposts=numposts, today=today)

