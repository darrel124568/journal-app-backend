from datetime import date
from marshmallow import ValidationError, fields, validate, validates_schema, Schema
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, MetaData
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates

meta = MetaData()
db = SQLAlchemy(metadata=meta)
bcrypt = Bcrypt()

#===================
#USER MODEL
#===================
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)

    journalEntries = db.relationship('JournalEntry', back_populates='user')

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))

#==================
#JournalEntry MODEL
#==================
class JournalEntry(db.Model):
    __tablename__ = 'journalEntries'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    year_created = db.Column(db.Date, default=date.today)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', back_populates='journalEntries')

#=========
#SCHEMAS
#=========
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(
        required=True,
        load_only=True,
        attribute='password_hash',
        validate=validate.Length(min=1),
    )
    password_confirmation = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=1),
    )
    journalEntries = fields.Nested(
        lambda: JournalEntrySchema(exclude=('user',)),
        many=True,
        dump_only=True,
    )

    @validates_schema
    def passwords_match(self, data, **kwargs):
        if data['password_hash'] != data['password_confirmation']:
            raise ValidationError(
                {'password_confirmation': ['Passwords must match.']}
            )


class JournalEntrySchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    year_created = fields.Date(dump_only=True)
    user_id = fields.Int(required=True)
    user = fields.Nested(UserSchema, dump_only=True, exclude=('journalEntries',))
