from flask_appbuilder import Model
from flask_appbuilder.security.sqla.models import User, Role
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy import Boolean, Numeric, Date, DateTime
from sqlalchemy import func, select
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import EncryptedType

from . import app

class UserExtended(User):
    __tablename__ = 'ab_user'
    person_id = Column(Integer, ForeignKey('person.id'))
    person = relationship('Person')

class Person(Model):
    id = Column(Integer, primary_key=True)
    full_name = Column(String(50), nullable=False)
    email = Column(String(100))
    phone = Column(String(100))
    sex = Column(String(1), nullable=False)
    oib_or_pin = Column(String(100))

    def __repr__(self):
        return self.full_name


class InstitutionParticipation(Model):
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project')
    edu_institution_id = Column(Integer, ForeignKey('edu_institution.id'))
    edu_institution = relationship('EduInstitution')
    vote_number = Column(Integer)


class OrganizationContact(Model):
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', backref='contacts')
    contact_person_id = Column(Integer, ForeignKey('person.id'))
    contact_person = relationship('Person', backref='organizations')
    role = Column(String(255))


class Organization(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    address = Column(String(1000))
    generic_email = Column(String(200))
    oib = Column(String(50))

    def __repr__(self):
        return self.name


class EduInstitution(Model):
    id = Column(Integer, primary_key=True)
    abbreviation = Column(String(20), nullable=False)
    organization_id = Column(Integer, ForeignKey('organization.id'), nullable=False)
    organization = relationship('Organization', backref=backref('edu_institution'))

    def __repr__(self):
        return self.organization.name


class InstitutionRepresentation(Model):
    id = Column(Integer, primary_key=True)
    edu_institution_id = Column(Integer, ForeignKey('edu_institution.id'), nullable=False)
    edu_institution = relationship("EduInstitution")
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    person = relationship("Person")
    main_representative = Column(Boolean, default=True)


class Project(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)

    def __repr__(self):
        return self.name


class InventoryItem(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    owner_person_id = Column(Integer, ForeignKey('person.id'))
    owner_person = relationship('Person', backref='inventory_items',
            foreign_keys=[owner_person_id])
    owner_organization_id = Column(Integer, ForeignKey('organization.id'))
    owner_organization = relationship('Organization', backref='inventory_items')
    responsible_person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    responsible_person = relationship('Person', foreign_keys=[responsible_person_id],
            backref='inventory_responsible')
    location_id = Column(Integer, ForeignKey('location.id'), nullable=False)
    location = relationship('Location', backref='inventory')
    discarded = Column(Boolean, default=False)


    def __repr__(self):
        return self.name


class Location(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    address = Column(String(200))

    def __repr__(self):
        return self.name


class SponsorCategory(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(String(1000))

    def __repr__(self):
        return self.name


class SponsorResponsivenessLevel(Model):
    id = Column(Integer, primary_key=True)
    score = Column(Integer, nullable=False, unique=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(1000))

    def __repr__(self):
        return self.name


class SponsorComments(Model):
    id = Column(Integer, primary_key=True)
    comment = Column(String(1000), nullable=False)
    sponsor_id = Column(Integer, ForeignKey('sponsor.id'), nullable=False)
    sponsor = relationship('Sponsor', backref='comments')

    def __repr__(self):
        return self.comment


class Sponsor(Model):
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organization.id'), nullable=False)
    organization = relationship('Organization', backref='sponsorship')
    responsible_person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    responsible_person = relationship('Person', backref='sponsor_responsibilities')
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)
    project = relationship('Project', backref='sponsors')
    category_id = Column(Integer, ForeignKey('sponsor_category.id'))
    category = relationship('SponsorCategory', backref='sponsors')
    responsiveness_id = Column(Integer, ForeignKey('sponsor_responsiveness_level.id'))
    responsiveness = relationship('SponsorResponsivenessLevel', backref='sponsors')

    @hybrid_property
    def name(self):
        return repr(self)

    def __repr__(self):
        return self.project.name + ' - ' + self.organization.name


class SubcontractorComments(Model):
    id = Column(Integer, primary_key=True)
    comment = Column(String(1000), nullable=False)
    subcontractor_id = Column(Integer, ForeignKey('subcontractor.id'), nullable=False)
    subcontractor = relationship('Subcontractor', backref='comments')

    def __repr__(self):
        return self.comment


class Subcontractor(Model):
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)
    project = relationship('Project', backref='subcontractors')
    organization_id = Column(Integer, ForeignKey('organization.id'), nullable=False)
    organization = relationship('Organization', backref='subcontract')

    @hybrid_property
    def name(self):
        return repr(self)

    def __repr__(self):
        return self.project.name + ' - ' + self.organization.name

contract_physical_copies = Table('contract_physical_copies', Model.metadata,
        Column('id', Integer, primary_key=True),
        Column('contract_id', Integer, ForeignKey('contract.id')),
        Column('physical_document_id', Integer, ForeignKey('physical_document.id'), unique=True))

contract_digital_copies = Table('contract_digital_copies', Model.metadata,
        Column('id', Integer, primary_key=True),
        Column('contract_id', Integer, ForeignKey('contract.id')),
        Column('digital_document_id', Integer, ForeignKey('digital_document.id'), unique=True))

class Contract(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    sponsor_id = Column(Integer, ForeignKey('sponsor.id'), nullable=False)
    sponsor = relationship('Sponsor', backref='contracts')
    internal_signee_id = Column(Integer, ForeignKey('person.id'))
    internal_signee = relationship('Person')
    signed = Column(Boolean, default=False)
    digital_copies = relationship('DigitalDocument', secondary=contract_digital_copies)
    physical_copies = relationship('PhysicalDocument', secondary=contract_physical_copies)
    invoice_incoming_id = Column(Integer, ForeignKey('invoice_incoming.id'))
    invoice_incoming = relationship('InvoiceIncoming', backref=backref('contract'))

    def __repr__(self):
        return self.name


class Income(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    invoice_incoming_id = Column(Integer, ForeignKey('invoice_incoming.id'))
    invoice_incoming = relationship('InvoiceIncoming', backref=backref('income'))
    value = Column(Numeric, nullable=False)
    date_received = Column(Date)

    def __repr__(self):
        return self.name


class Expense(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    invoice_outgoing_id = Column(Integer, ForeignKey('invoice_outgoing.id'))
    invoice_outgoing = relationship('InvoiceOutgoing', backref=backref('expense'))
    value = Column(Numeric, nullable=False)
    approved_by_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    approved_by = relationship('Person')
    date_paid = Column(Date, nullable=False)

    def __repr__(self):
        return self.name


class PlannedExpense(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    value = Column(Numeric, nullable=False)
    date_planned = Column(Date, nullable=False)

    def __repr__(self):
        return self.name


class PlannedIncome(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    value = Column(Numeric, nullable=False)
    date_planned = Column(Date, nullable=False)

    def __repr__(self):
        return self.name


invoice_incoming_physical_copies = Table('invoice_incoming_physical_copies', Model.metadata,
        Column('id', Integer, primary_key=True),
        Column('invoice_incoming_id', Integer, ForeignKey('invoice_incoming.id')),
        Column('physical_document_id', Integer, ForeignKey('physical_document.id'), unique=True))


invoice_incoming_digital_copies = Table('invoice_incoming_digital_copies', Model.metadata,
        Column('id', Integer, primary_key=True),
        Column('invoice_incoming_id', Integer, ForeignKey('invoice_incoming.id')),
        Column('digital_document_id', Integer, ForeignKey('digital_document.id'), unique=True))


class InvoiceIncomingItem(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    value = Column(Numeric, nullable=False)
    invoice_incoming_id = Column(Integer, ForeignKey('invoice_incoming.id'))
    invoice_incoming = relationship('InvoiceIncoming', backref='items')

    def __repr__(self):
        return self.name


class InvoiceIncoming(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    date_issued = Column(Date, nullable=False)
    issued_to_id = Column(Integer, ForeignKey('organization.id'))
    issued_to = relationship('Organization')
    date_due = Column(Date, nullable=False)
    digital_copies = relationship('DigitalDocument',
        secondary=invoice_incoming_digital_copies)
    physical_copies = relationship('PhysicalDocument',
        secondary=invoice_incoming_physical_copies)
    registered_with_accounting = Column(Boolean)

    @hybrid_property
    def value(self):
        return sum(i.value for i in self.items)

    @value.expression
    def value(cls):
        return (
                select([func.sum(InvoiceIncomingItem.value)]).
                where(InvoiceIncomingItem.invoice_incoming_id == cls.id).
                label('value')
                )

    def __repr__(self):
        return self.name


invoice_outgoing_physical_copies = Table('invoice_outgoing_physical_copies', Model.metadata,
        Column('id', Integer, primary_key=True),
        Column('invoice_outgoing_id', Integer, ForeignKey('invoice_outgoing.id')),
        Column('physical_document_id', Integer, ForeignKey('physical_document.id'), unique=True))


invoice_outgoing_digital_copies = Table('invoice_outgoing_digital_copies', Model.metadata,
        Column('id', Integer, primary_key=True),
        Column('invoice_outgoing_id', Integer, ForeignKey('invoice_outgoing.id')),
        Column('digital_document_id', Integer, ForeignKey('digital_document.id'), unique=True))


class InvoiceOutgoing(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    date_issued = Column(Date, nullable=False)
    vendor_name = Column(String(500), nullable=False)
    vendor_invoice_number = Column(String(500))
    value = Column(Numeric, nullable=False)
    date_due = Column(Date)
    comment = Column(String(1000))
    digital_copies = relationship('DigitalDocument',
        secondary=invoice_outgoing_digital_copies)
    physical_copies = relationship('PhysicalDocument',
        secondary=invoice_outgoing_physical_copies)
    registered_with_accounting = Column(Boolean)

    def __repr__(self):
        return self.name


class ParticipantInfo(Model):
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('person.id'))
    person = relationship('Person', backref='participation', foreign_keys=[person_id])
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', backref='participants')
    responsible_organization_id = Column(Integer, ForeignKey('organization.id'))
    responsible_organization = relationship('Organization', backref='responsible_for')
    participation_approved = Column(Boolean, default=False)
    approved_by_id = Column(Integer, ForeignKey('person.id'))
    approved_by = relationship('Person', foreign_keys=[approved_by_id])
    participation_category_id = Column(Integer, ForeignKey('participation_category.id'))
    participation_category = relationship('ParticipationCategory', backref='participants')
    t_shirt_size = Column(String(10))

    def __repr__(self):
        return self.person.name + ' ' + self.project.name

class ParticipationCategory(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    def __repr__(self):
        return self.name

class DigitalDocument(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    link = Column(String(1000), nullable=False)
    author_id = Column(Integer, ForeignKey('person.id'))
    author = relationship('Person', backref='digital_documents')
    date = Column(Date, nullable=False)
    comment = Column(String(1000))

    def __repr__(self):
        return self.name


class PhysicalDocument(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    location_id = Column(Integer, ForeignKey('location.id'), nullable=False)
    location = relationship('Location', backref='documents')
    author_id = Column(Integer, ForeignKey('person.id'))
    author = relationship('Person', backref='physical_documents')
    date = Column(Date, nullable=False)
    comment = Column(String(1000))

    def __repr__(self):
        return self.name


class OrganizationTeam(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    part_of_team_id = Column(Integer, ForeignKey('organization_team.id'))
    part_of_team = relationship('OrganizationTeam')

    def __repr__(self):
        return self.name


volunteer_team_membership = Table('volunteer_team_membership', Model.metadata,
        Column('id', Integer, primary_key=True),
        Column('project_organization_team_id', ForeignKey('project_organization_team.id')),
        Column('organization_volunteer_id', ForeignKey('organization_volunteer.id')))


volunteer_team_leadership = Table('volunteer_team_leadership', Model.metadata,
        Column('id', Integer, primary_key=True),
        Column('project_organization_team_id', ForeignKey('project_organization_team.id')),
        Column('organization_volunteer_id', ForeignKey('organization_volunteer.id')))


class ProjectOrganizationTeam(Model):
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', backref='organization_teams')
    organization_team_id = Column(Integer, ForeignKey('organization_team.id'))
    organization_team = relationship('OrganizationTeam')

    def __repr__(self):
        return self.organization_team.name + ' ' + self.project.name


class OrganizationVolunteer(Model):
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('person.id'))
    is_active = Column(Boolean)
    person = relationship('Person', backref='volunteer_data')
    member_of = relationship('ProjectOrganizationTeam', secondary=volunteer_team_membership,
            backref='members')
    lead_of = relationship('ProjectOrganizationTeam', secondary=volunteer_team_leadership,
            backref='leads')

    def __repr__(self):
        return self.name


class Vehicle(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    plate_number = Column(String(50), nullable=False)
    owner_person_id = Column(Integer, ForeignKey('person.id'))
    owner_person = relationship('Person', backref='cars')
    owner_organization_id = Column(Integer, ForeignKey('organization.id'))
    owner_organization = relationship('Organization', backref='cars')
    available_to_reserve = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return self.name


class VehicleReservation(Model):
    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('vehicle.id'), nullable=False)
    vehicle = relationship('Vehicle', backref='reservations')
    person_id = Column(Integer, ForeignKey('person.id'))
    person = relationship('Person', backref='vehicle_reservations')
    reservation_start_time = Column(DateTime, nullable=False)
    reservation_end_time = Column(DateTime, nullable=False)
    vehicle_taken_time = Column(DateTime)
    vehicle_returned_time = Column(DateTime)


class ToolCredentials(Model):
    id = Column(Integer, primary_key=True)
    tool_name = Column(String(255), nullable=False)
    username = Column(String(255))
    password = Column(EncryptedType(String(1024), key=app.config['SECRET_KEY']))
    have_access = relationship(Role, secondary='tool_credential_permission', backref='accessible_credentials')

    def __repr__(self):
        return self.tool_name

class ToolCredentialPermission(Model):
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('ab_role.id'))
    credentials_id = Column(Integer, ForeignKey('tool_credentials.id'))
    role = relationship('Role')
    credentials = relationship('ToolCredentials')

    def __repr__(self):
        return repr(self.user) + ' ' + self.credentials.tool_name
