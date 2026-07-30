from config import app, db
from flask_restful import Resource, Api
from flask import request, jsonify, session
from marshmallow import ValidationError
from models import User, UserSchema, JournalEntry, JournalEntrySchema

api = Api(app=app)

@app.before_request
def before_request():
    accepted = ["signup", "login"]
    if request.endpoint not in accepted and (not session.get("user_id")):
        return {}, 401
    
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

#=============
#LOGIN ROUTE
#=============
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
#=============
#CHECK SESSION ROUTE
#=============
class CheckSession(Resource):
    def get(self):
        user = User.query.get(session["user_id"])
        return UserSchema().dump(user), 200
#=============
#LOGOUT ROUTE
#=============
class Logout(Resource):
    def delete(self):
        session.pop("user_id")
        return {}, 201

#===========================================
#JOURNAL ENTRIES INDEX ROUTE WITH PAGINATION
#===========================================
class Entries(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        entries = JournalEntry.query.filter_by(user_id=session["user_id"]).paginate(
            page=page, per_page=per_page
        )
        return JournalEntrySchema(many=True).dump(entries.items), 200

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(CheckSession, '/checkSession', endpoint='checkSession')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(Entries, "/entries", endpoint='entries')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
