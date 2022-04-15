from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, \
        SelectMultipleField, BooleanField
from wtforms import widgets
from wtforms.fields.html5 import DateField as H5DateField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, Length, NumberRange

from .models import Category, Component, Institution

TSHIRT_CHOICES = [('', '---'),
                  ('XS', 'XS'),
                  ('S', 'S'),
                  ('M', 'M'),
                  ('L', 'L'),
                  ('XL', 'XL'),
                  ('XXL', 'XXL')]


class CheckboxGroupField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ApplicationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    cell_number = StringField('Cell phone number', validators=[DataRequired()])
    pin = StringField('OIB (Croatian citizens)/Travel document number (others)',
                     validators=[DataRequired(), Length(max=100)])

    street = StringField('Street address', validators=[DataRequired(), Length(min=3, max=200)])
    city = StringField('City', validators=[DataRequired(), Length(max=60)])
    postal_code = StringField('Postal code', validators=[DataRequired(), Length(max=20)])
    country = StringField('Country', validators=[DataRequired(), Length(max=60)])

    dob = H5DateField('Date of birth', format='%Y-%m-%d', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('', '---'),('M', 'Male'), ('F', 'Female')],
                         validators=[DataRequired()])
    t_shirt_size = SelectField('T-shirt size', choices=TSHIRT_CHOICES,
                               validators=[DataRequired()])

    institution = SelectField('Institution',
            choices=[(-1, '---')]+[(i.id, i.name) for i in Institution.query.all()],
            coerce=int, validators=[NumberRange(min=0, message="Please select an institution"),])

    gdpr_checkbox = BooleanField('I have read and understood the Notice', validators=[DataRequired()])

    component = SelectField('Type of participation',
            choices=[(-1, '---')]+[(i.id, i.name) for i in Component.query.all()],
            coerce=int, validators=[NumberRange(min=0, message="Please select a type")])

    categories = SelectMultipleField('Categories',
            choices=[(i.id, i.name) for i in Category.query.all()], coerce=int,
            validators=[DataRequired()])

    cv = FileField('Upload your CV')

    comment = StringField(u'Optional comment', widget=widgets.TextArea(),
              validators=[Length(max=1024)])

    submit = SubmitField('Submit application')




