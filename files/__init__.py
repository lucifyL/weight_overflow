from flask import Flask
 
app = Flask(__name__)
 
app.secret_key = 'development key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:zuiaimaomao540@localhost/development'

from models import db
db.init_app(app)

import files.routes