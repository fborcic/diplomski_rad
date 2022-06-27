from flask import render_template, g
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.sqla.filters import BaseFilter
from flask_appbuilder.models.sqla.filters import get_field_setup_query
from flask_appbuilder import ModelView, ModelRestApi

from . import appbuilder, db
from .models import *


class CredentialsFilterFunction(BaseFilter):
    def apply(self, query, func):
        query, field = get_field_setup_query(query, self.model, self.column_name)
        return query.filter(field.any(ToolCredentials.id.in_(func())))


def get_user_allowed_credentials():
    return set(c.id for role in g.user.roles \
            for c in role.accessible_credentials)


class OrganizationContactModelView(ModelView):
    datamodel = SQLAInterface(OrganizationContact)
    list_columns = ['organization', 'contact_person', 'role']


class OrganizationModelView(ModelView):
    datamodel = SQLAInterface(Organization)
    related_views = [OrganizationContactModelView]

    list_columns = ['name', 'generic_email']

class SponsorCommentsModelView(ModelView):
    datamodel = SQLAInterface(SponsorComments)
    list_columns = ['sponsor', 'comment']

class SubcontractorCommentsModelView(ModelView):
    datamodel = SQLAInterface(SubcontractorComments)
    list_columns = ['subcontractor', 'comment']

class SponsorModelView(ModelView):
    datamodel = SQLAInterface(Sponsor)
    related_views = [SponsorCommentsModelView]
    show_template = 'appbuilder/general/model/show_cascade.html'

    list_columns = ['name']


class InventoryItemModelView(ModelView):
    datamodel = SQLAInterface(InventoryItem)

    list_columns = ['name']

class IncomeModelView(ModelView):
    datamodel = SQLAInterface(Income)

    list_columns = ['name', 'value', 'date_received']

class ExpenseModelView(ModelView):
    datamodel = SQLAInterface(Expense)
    list_columns = ['name', 'value',
            'approved_by', 'date_paid']

class PlannedExpenseModelView(ModelView):
    datamodel = SQLAInterface(PlannedExpense)
    list_columns = ['name', 'value', 'date_planned']

class PlannedIncomeModelView(ModelView):
    datamodel = SQLAInterface(PlannedIncome)
    list_columns = ['name', 'value', 'date_planned']

class InstitutionParticipationModelView(ModelView):
    datamodel = SQLAInterface(InstitutionParticipation)
    list_columns = ['project', 'edu_institution', 'vote_number']

class EduInstitutionModelView(ModelView):
    datamodel = SQLAInterface(EduInstitution)
    related_views = [InstitutionParticipationModelView]
    list_columns = ['abbreviation']

class SponsorCategoryModelView(ModelView):
    datamodel = SQLAInterface(SponsorCategory)
    related_views = [SponsorModelView]
    list_columns = ['name', 'description']

class SponsorResponsivenessLevelModelView(ModelView):
    datamodel = SQLAInterface(SponsorResponsivenessLevel)
    related_views = [SponsorModelView]
    list_columns = ['score', 'name']

class SubcontractorModelView(ModelView):
    datamodel = SQLAInterface(Subcontractor)
    list_columns = ['organization', 'project']

class InstitutionRepresentationModelView(ModelView):
    datamodel = SQLAInterface(InstitutionRepresentation)
    list_columns = ['edu_institution', 'person', 'main_representative']

class DigitalDocumentModelView(ModelView):
    datamodel = SQLAInterface(DigitalDocument)
    list_columns = ['name', 'date', 'author', 'link']

class PhysicalDocumentModelView(ModelView):
    datamodel = SQLAInterface(PhysicalDocument)
    list_columns = ['name', 'date', 'author', 'location']

class ContractModelView(ModelView):
    datamodel = SQLAInterface(Contract)
    related_views = [PhysicalDocumentModelView,
            DigitalDocumentModelView]
    list_columns = ['name', 'sponsor', 'internal_signee', 'signed']

class InvoiceIncomingItemModelView(ModelView):
    datamodel = SQLAInterface(InvoiceIncomingItem)
    list_columns = ['name', 'value']

class InvoiceIncomingModelView(ModelView):
    datamodel = SQLAInterface(InvoiceIncoming)
    related_views = [InvoiceIncomingItemModelView,
            DigitalDocumentModelView,
            PhysicalDocumentModelView]
    list_columns = ['name', 'date_issued', 'issued_to', 'date_due',
            'value', 'registered_with_accounting']
    show_template = 'appbuilder/general/model/show_cascade.html'

class InvoiceOutgoingModelView(ModelView):
    datamodel = SQLAInterface(InvoiceOutgoing)
    list_columns = ['name', 'vendor_name', 'date_issued', 'date_due',
            'registered_with_accounting']

class ParticipationCategoryModelView(ModelView):
    datamodel = SQLAInterface(ParticipationCategory)
    list_columns = ['name']

class ParticipantInfoModelView(ModelView):
    datamodel = SQLAInterface(ParticipantInfo)
    list_columns = ['project', 'person', 'responsible_organization',
            'participation_approved']

class OrganizationTeamModelView(ModelView):
    datamodel = SQLAInterface(OrganizationTeam)
    list_columns = ['name', 'part_of_team']

class OrganizationVolunteerModelView(ModelView):
    datamodel = SQLAInterface(OrganizationVolunteer)
    list_columns = ['person', 'is_active']

class ProjectOrganizationTeamModelView(ModelView):
    datamodel = SQLAInterface(ProjectOrganizationTeam)
    list_columns = ['organization_team', 'project']
    related_views = [OrganizationVolunteerModelView]

class VehicleReservationModelView(ModelView):
    datamodel = SQLAInterface(VehicleReservation)
    list_columns = ['vehicle', 'person', 'reservation_start_time',
            'reservation_end_time']

class VehicleModelView(ModelView):
    datamodel = SQLAInterface(Vehicle)
    list_columns = ['name', 'plate_number',
            'owner_person', 'owner_organization']

class ToolCredentialPermissionModelView(ModelView):
    datamodel = SQLAInterface(ToolCredentialPermission)
    list_columns = ['role', 'credentials']

class ToolCredentialsModelView(ModelView):
    datamodel = SQLAInterface(ToolCredentials)
    related_views = [ToolCredentialPermissionModelView]
    list_columns = ['tool_name', 'username', 'password']
    base_filters = [('have_access',
        CredentialsFilterFunction, get_user_allowed_credentials)]

class LocationModelView(ModelView):
    datamodel = SQLAInterface(Location)
    related_views = [PhysicalDocumentModelView,
                InventoryItemModelView]
    list_columns = ['name']


class ProjectModelView(ModelView):
    datamodel = SQLAInterface(Project)
    related_views = [SponsorModelView,
                     InstitutionParticipationModelView,
                     ParticipantInfoModelView]

    list_columns = ['name']

class PersonModelView(ModelView):
    datamodel = SQLAInterface(Person)
    related_views = [InventoryItemModelView,
                     VehicleModelView,
                     VehicleReservationModelView,
                     PhysicalDocumentModelView]

    list_columns = ['full_name', 'email', 'phone', 'sex',
                    'oib_or_pin']

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
        category_icon = "fa-book"
    )
appbuilder.add_view(
        OrganizationModelView,
        "Organizations",
        icon = "fa-folder-open-o",
        category = "General",
    )
appbuilder.add_view(
        SponsorModelView,
        "Sponsors",
        icon = "fa-folder-open-o",
        category = "Partnerships",
        category_icon = "fa-handshake-o"
    )
appbuilder.add_view(
        PersonModelView,
        "People",
        icon = "fa-folder-open-o",
        category = "General",
    )
appbuilder.add_view(
        InventoryItemModelView,
        "Inventory",
        icon = "fa-folder-open-o",
        category = "Operations",
        category_icon = "fa-shopping-cart"
    )
appbuilder.add_view(
        IncomeModelView,
        "Income",
        icon = "fa-folder-open-o",
        category = "Finance",
        category_icon = "fa-money"
    )
appbuilder.add_view(
        ExpenseModelView,
        "Expenses",
        icon = "fa-folder-open-o",
        category = "Finance",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        PlannedIncomeModelView,
        "Planned Income",
        icon = "fa-folder-open-o",
        category = "Finance",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        PlannedExpenseModelView,
        "Planned Expenses",
        icon = "fa-folder-open-o",
        category = "Finance",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        ContractModelView,
        "Contracts",
        icon = "fa-folder-open-o",
        category = "Partnerships",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        LocationModelView,
        "Locations",
        icon = "fa-folder-open-o",
        category = "General",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        SponsorCategoryModelView,
        "Sponsor Categories",
        icon = "fa-folder-open-o",
        category = "Partnerships",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        SubcontractorModelView,
        "Subcontractors",
        icon = "fa-folder-open-o",
        category = "Operations",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        SubcontractorCommentsModelView,
        "Subcontractor Comments",
        icon = "fa-folder-open-o",
        category = "Operations",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        SponsorCommentsModelView,
        "Sponsor Comments",
        icon = "fa-folder-open-o",
        category = "Partnerships",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        InstitutionParticipationModelView,
        "Institution Participation",
        icon = "fa-folder-open-o",
        category = "Participation",
        category_icon = "fa-group"
    )
appbuilder.add_view(
        InstitutionRepresentationModelView,
        "Institution Representation",
        icon = "fa-folder-open-o",
        category = "Participation",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        InvoiceIncomingItemModelView,
        "Incoming Invoice Item",
        icon = "fa-folder-open-o",
        category = "Finance",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        InvoiceIncomingModelView,
        "Incoming Invoices",
        icon = "fa-folder-open-o",
        category = "Finance",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        InvoiceOutgoingModelView,
        "Outgoing Invoices",
        icon = "fa-folder-open-o",
        category = "Finance",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        ParticipantInfoModelView,
        "Participants",
        icon = "fa-folder-open-o",
        category = "Participation",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        ParticipationCategoryModelView,
        "Participation Categories",
        icon = "fa-folder-open-o",
        category = "Participation",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        DigitalDocumentModelView,
        "Digital Documents",
        icon = "fa-folder-open-o",
        category = "General",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        PhysicalDocumentModelView,
        "Physical Documents",
        icon = "fa-folder-open-o",
        category = "General",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        OrganizationTeamModelView,
        "General Organization Teams",
        icon = "fa-folder-open-o",
        category = "General",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        ProjectOrganizationTeamModelView,
        "Project Organization Teams",
        icon = "fa-folder-open-o",
        category = "General",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        OrganizationVolunteerModelView,
        "Volunteers",
        icon = "fa-folder-open-o",
        category = "General",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        VehicleModelView,
        "Vehicles",
        icon = "fa-folder-open-o",
        category = "Operations",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        VehicleReservationModelView,
        "Vehicle Reservations",
        icon = "fa-folder-open-o",
        category = "Operations",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        ToolCredentialsModelView,
        "Tool Credentials",
        icon = "fa-folder-open-o",
        category = "General",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        ToolCredentialPermissionModelView,
        "Tool Credential Permissions",
        icon = "fa-folder-open-o",
        category = "Security",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        EduInstitutionModelView,
        "Educational institutions",
        icon = "fa-folder-open-o",
        category = "General",
        category_icon = "fa-folder-open-o"
    )
appbuilder.add_view(
        SponsorResponsivenessLevelModelView,
        "Sponsor Responsiveness Categories",
        icon = "fa-folder-open-o",
        category = "Partnerships",
        category_icon = "fa-folder-open-o"
    )

