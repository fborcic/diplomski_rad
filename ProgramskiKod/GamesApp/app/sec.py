from flask_appbuilder.security.sqla.manager import SecurityManager
from .models import UserExtended
from .sec_views import UserDBModelViewExtended

class MySecurityManager(SecurityManager):
    user_model = UserExtended
    userdbmodelview = UserDBModelViewExtended
