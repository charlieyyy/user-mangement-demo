import mongoengine
from demo2.model.base_model import BaseModel


class User(BaseModel, mongoengine.Document):
    username = mongoengine.StringField(required=True, unique=True)
    password = mongoengine.StringField(required=True)
    email = mongoengine.EmailField(required=True, unique=True)
    level = mongoengine.IntField(required=True, default=1)

    meta = {
        'collection': 'users',
        'indexes': [
            {
                'fields': ['username'],
                'unique': True
            }
        ]
    }

    @classmethod
    def validate_password(cls, username, password):
        user = cls.get_by_username(username)
        if user and user.password.encode('utf-8') == password.encode('utf-8'):
            return user

    @classmethod
    def get_by_username(cls, username):
        return cls.objects(username=username).first()

    @classmethod
    def delete_by_username(cls, username):
        lunch = cls.objects(username=username).first()
        lunch.delete()

    @property
    def is_admin(self):
        return self.level == 9

    @property
    def is_editor(self):
        return self.level == 2

    def api_base_response(self):
        return {'id': str(self.id), 'username': self.username}

    def me(self):
        return self.api_response()

    def api_response(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email if self.email else ''
        }


def authenticate(user, username, password):
    user = User.validate_password(username, password)
    return user if user else None


def identity(payload):
    return User.objects.get(id=payload['identity'])
