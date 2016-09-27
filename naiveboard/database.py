from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Unicode, String, Boolean, ForeignKey
#import datetime

engine = create_engine('sqlite:///naiveboard/database.db', echo=False, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()
		

class User(Base):
	__tablename__ = 'usertable'

	id = Column(Integer, primary_key=True)
	username = Column(String(20), nullable=True, unique=True)
	password = Column(String(20), nullable=True)	

	def __init__(self, username, password):
		self.username = username
		self.password = password
	def __repr__(self):
		return '<User %s>' % (self.username)


class Post(Base):
	__tablename__ = 'posttable'

	id = Column(Integer, primary_key=True)
	title 	= Column(String(50), nullable=False)
	text	= Column(String(500), nullable=False)
	date 	= Column(String(10), nullable=False)
	time	= Column(String(8), nullable=False)
	
	user_id = Column(Integer, ForeignKey('usertable.id'))
	user = relationship('User', backref='posts')

	def __init__(self, title, text, when):
		self.title 	= title
		self.text	= text
		self.date 	= when.strftime("%y-%m-%d")
		self.time	= when.strftime("%H:%M:%S")
	def __repr__(self):
		return '<Post %s>' % (self.title)


class Comment(Base):
	__tablename__ = 'commenttable'

	id = Column(Integer, primary_key=True)
	text = Column(String(140), nullable=False)
	date = Column(String(10), nullable=False)
	time = Column(String(8), nullable=False)

	user_id = Column(Integer, ForeignKey('usertable.id'))
	user = relationship('User', backref='comments')
	post_id = Column(Integer, ForeignKey('posttable.id'))
	post = relationship('Post', backref='comments')

	def __init__(self, text, when):
		self.text = text
		self.date 	= when.strftime("%y-%m-%d")
		self.time	= when.strftime("%H:%M:%S")
	def __repr__(self):
		return '<Comment %s>' % (self.text)