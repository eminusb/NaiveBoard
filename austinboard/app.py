
from flask import Flask
from austinboard.nl2br import nl2br, urllink

app = Flask(__name__)
app.config.update(SECRET_KEY='DRAOBNITSUA')

app.jinja_env.filters['nl2br'] = nl2br
app.jinja_env.filters['urllink'] = urllink

