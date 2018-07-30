import mongoengine
from demo2 import settings
from demo2 import app
from demo2.api import v1

mongoengine.connect('demo2', host=settings.DEMO_HOST)

if __name__ == '__main__':
    app.run()
