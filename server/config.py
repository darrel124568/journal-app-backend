from flask import Flask
from flask_migrate import Migrate
from models import bcrypt, db

#app configurations
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bcrypt.init_app(app)

migrate = Migrate(app, db)
db.init_app(app)
