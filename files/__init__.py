from flask import Flask
 
app = Flask(__name__)

app.secret_key = 'development key'

app.config['SQLALCHEMY_DATABASE_URI'] = '######################'

from models import db
db.init_app(app)

import files.routes
