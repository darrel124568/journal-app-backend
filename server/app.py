from config import app, db
from flask_restful import Resource, Api
from flask import request, session
from marshmallow import ValidationError
from models import User, UserSchema, JournalEntry, JournalEntrySchema

api = Api(app=app)

# Require authentication for every endpoint except account creation and login.
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
            # Deserialize and validate the request before storing the new user.
            data = UserSchema().load(request.get_json())
            new_user = User(username=data["username"])
            new_user.password_hash = data["password_hash"]
            session["user_id"] = new_user.id
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
            # Treat a missing or malformed JSON body as an invalid login attempt instead of a bad request.
            data = request.get_json(silent=True) or {}
            username = data.get("username")
            password = data.get("password")

            user = User.query.filter_by(username=username).first()
            # Store only the user id in the signed session after authentication.
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
        # Pagination to avoid overwhelming the front-end
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        entries = JournalEntry.query.filter_by(user_id=session["user_id"]).paginate(
            page=page, per_page=per_page
        )
        return JournalEntrySchema(many=True).dump(entries.items), 200
#=======================
#POST TO JOURNAL ENTRIES
#=======================
class AddEntry(Resource):
    def post(self):
        try:
            data = request.get_json()
            # Ownership is derived from the sessionnot the client
            data["user_id"] = session["user_id"]
            new_entry = JournalEntry(**JournalEntrySchema().load(data))
            db.session.add(new_entry)
            db.session.commit()
            return JournalEntrySchema().dump(new_entry), 201
        except ValidationError as errors:
            return {"errors": errors.messages}, 400
        except Exception:
            db.session.rollback()
            return {"error": "could not add user"}, 500


#=======================
#UPDATE JOURNAL ENTRIES
#=======================
class Patch(Resource):
    def patch(self, id):
        try:
            entry = JournalEntry.query.filter_by(
                id=id, user_id=session["user_id"]
            ).first()
            if not entry:
                return {}, 404

            data = JournalEntrySchema(partial=True, exclude=("user_id",)).load(
                request.get_json(silent=True) or {}
            )
            # Apply only fields accepted by the partial schema validation.
            for key, value in data.items():
                setattr(entry, key, value)
            db.session.commit()
            return JournalEntrySchema().dump(entry), 200
        except ValidationError as errors:
            return {"errors": errors.messages}, 400
        except Exception:
            db.session.rollback()
            return {"error": "could not update entry"}, 500
#=======================
#DELETE JOURNAL ENTRIES
#=======================
class Delete(Resource):
    def delete(self, id):
        entry = JournalEntry.query.filter_by(
            id=id, user_id=session["user_id"]
        ).first()
        if not entry:
            return {}, 404

        try:
            db.session.delete(entry)
            db.session.commit()
            return {"message": "deleted successfully"}, 200
        except Exception:
            db.session.rollback()
            return {"error": "could not delete entry"}, 500

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(CheckSession, '/checkSession', endpoint='checkSession')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(Entries, "/entries", endpoint='entries')
api.add_resource(AddEntry, "/add_entry", endpoint='add_entry')
api.add_resource(Patch, "/patch/<int:id>", endpoint='patch')
api.add_resource(Delete, "/delete/<int:id>", endpoint='delete')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
