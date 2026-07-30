from flask import Flask
from flask_migrate import Migrate
from models import db
from flask_bycrypt import Bycrypt

#app configurations
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bcrypt = Bycrypt(app)

migrate = Migrate(app, db)
db.init_app(app)