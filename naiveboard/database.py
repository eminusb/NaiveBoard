from sqlalchemy import create_engine, Table, ForeignKey,\
					   Column, Integer, Unicode, String, Boolean
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
#import datetime

#engine = create_engine('sqlite:///naiveboard/database.db', echo=False, convert_unicode=True)
engine = create_engine('postgresql://postgres:dhcndrl1@localhost:5555/pgdatabase', echo=False, convert_unicode=True)
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
		return '<User %s: %s>' % (self.username, self.password)


class Post(Base):
	__tablename__ = 'posttable'

	id = Column(Integer, primary_key=True)
	title 	= Column(String(50), nullable=False)
	text	= Column(String(2000), nullable=False)
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


postxtag_table = Table('association', Base.metadata, 
	Column('posttable_id', Integer, ForeignKey('posttable.id')),
	Column('tagtable_id', Integer, ForeignKey('tagtable.id'))
)
class Tag(Base):
	__tablename__ = 'tagtable'

	id = Column(Integer, primary_key=True)
	text = Column(String(20), nullable=False)

	posts = relationship('Post', backref='tags', secondary=postxtag_table)

	def __init__(self, text):
		self.text = text

	def __repr__(self):
		return '<Tag ''%s''>' % (self.text)


def check_username(username):
	query = db_session.query(User)
	user = query.filter(User.username==username).first()
	if user == None:
		return False
	else:
		return True

def check_password(user, password):
	user.passowrd == password
	pass


def validate_username(username):
	query = db_session.query(User)
	user = query.filter(User.username==username).first()
	pass

def print_table(classname):
	cols = db_session.query(classname).order_by(classname.id).all()
	for col in cols:
		print(col)
	print('\n')

def delete_all_cols(classname):
	cols = db_session.query(classname).order_by(classname.id).all()
	for col in cols:
		db_session.delete(col)
	db_session.commit()