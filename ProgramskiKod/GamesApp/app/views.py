from flask import render_template
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, ModelRestApi

from . import appbuilder, db
from .models import Project, EduInstitution, Organization, Sponsor

"""
    Create your Model based REST API::

    class MyModelApi(ModelRestApi):
        datamodel = SQLAInterface(MyModel)

    appbuilder.add_api(MyModelApi)


    Create your Views::


    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)


    Next, register your Views::


    appbuilder.add_view(
        MyModelView,
        "My View",
        icon="fa-folder-open-o",
        category="My Category",
        category_icon='fa-envelope'
    )
"""

"""
    Application wide 404 error handler
"""

class OrganizationModelView(ModelView):
    datamodel = SQLAInterface(Organization)

    list_columns = ['name']

class SponsorModelView(ModelView):
    datamodel = SQLAInterface(Sponsor)
    related_views = [OrganizationModelView]

    list_columns = ['name']

class ProjectModelView(ModelView):
    datamodel = SQLAInterface(Project)
    related_views = [SponsorModelView]

    list_columns = ['name']



@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )


db.create_all()
appbuilder.add_view(
        ProjectModelView,
        "Projects",
        icon = "fa-folder-open-o",
        category = "General",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        SponsorModelView,
        "Sponsors",
        icon = "fa-folder-open-o",
        category = "Partnerships",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        OrganizationModelView,
        "Organizations",
        icon = "fa-folder-open-o",
        category = "General",
        category_icon = "fa-folder-open-o"
    )
