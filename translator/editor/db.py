import os
from django.conf import settings
from tinydb import TinyDB


path = os.path.join(settings.BASE_DIR, 'db.json')
db = TinyDB(path)
paragraphs = db.table('paragraphs')
