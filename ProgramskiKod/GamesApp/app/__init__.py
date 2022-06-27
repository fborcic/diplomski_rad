import logging

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA

"""
 Logging configuration
"""

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object("config")
db = SQLA(app)


from .sec import MySecurityManager
from .index import MyIndexView
appbuilder = AppBuilder(app, db.session,
        security_manager_class=MySecurityManager,
        indexview = MyIndexView)


from . import views
