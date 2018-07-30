import mongoengine
from demo2.model.base_model import BaseModel


class Article(BaseModel, mongoengine.Document):
    title = mongoengine.StringField(required=True, default='')
    added = mongoengine.DateTimeField(required=True, default='')
    url = mongoengine.StringField(required=True, unique=True, default='')
    author = mongoengine.ReferenceField('User', default=False)

    meta = {
        'collection': 'articles',
        'indexes': [
            {
                'fields': ['url'],
                'unique': True
            }
        ]
    }

    @classmethod
    def get_by_id(cls, id):
        return cls.objects(id=id).first()

    @classmethod
    def delete_by_id(cls, id):
        lunch = cls.objects(id=id).first()
        lunch.delete()

    def api_base_response(self):
        return {'id': str(self.id), 'url': self.url}

    def api_response(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'added': self.added.timestamp(),
            'url': self.url,
            'author': (str(self.author.id)
                       if self.author else {})
        }
