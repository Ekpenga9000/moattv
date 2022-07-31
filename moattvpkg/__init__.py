from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app) # whatever is in the instance of Flask will be in here. 

from moattvpkg import routes
# you can also import any other variable, object, model you would need  
