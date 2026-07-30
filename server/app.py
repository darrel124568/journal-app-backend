from config import app, db
from flask_restful import Resource, Api
from flask import request, jsonify, session
from marshmallow import ValidationError
from models import User, UserSchema, JournalEntry, JournalEntrySchema

api = Api(app=app)

#=============
#SIGN-UP ROUTE
#=============
class Signup(Resource):
    def post(self):
        try:
            data = UserSchema().load(request.get_json())
            new_user = User(**data)

            db.session.add(new_user)
            db.session.commit()
            return UserSchema().dump(new_user), 201
        except ValidationError as errors:
            return {"errors": errors.messages}, 400
        except Exception:
            db.session.rollback()
            return {"error": "could not add user"}, 500
class Login(Resource):
    def post(self):
        try:
            data = request.get_json(silent=True) or {}
            username = data.get("username")
            password = data.get("password")

            user = User.query.filter_by(username=username).first()
            if user and user.authenticate(password):
                session["user_id"] = user.id
                return UserSchema().dump(user), 200
            return {"error": "unauthorized"}, 401

        except Exception:
            return {"error": "could not login"}, 500


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(Login, '/login', endpoint='login')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
