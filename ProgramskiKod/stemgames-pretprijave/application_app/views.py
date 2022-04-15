import datetime
import json
import os
import random
import collections

from flask import Blueprint, render_template, flash, redirect, url_for
from flask import request, abort, jsonify, make_response
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
from sqlalchemy import distinct, func, select

from . import db

from flask import current_app as app

from .forms import ApplicationForm
from .models import StudentApplication, Category, Component, Institution, Credentials

app_form = Blueprint('app_form', __name__)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    user = Credentials.query.filter_by(name=username).all()
    if not user:
        return
    user = user[0]
    return user.check_password(password)

def user_institution_limit():
    username = auth.current_user()
    user = Credentials.query.filter_by(name=username).all()
    if not user:
        raise ValueError
    return user[0].limit_to_institution

def _save_file(form):
    f = form.cv.data
    if f is None:
        return

    filename = secure_filename(f.filename)

    inst = Institution.query.get(form.institution.data).name
    new_name = "%s_%s_%s_%d%s"%(form.first_name.data,
                              form.last_name.data,
                              inst, random.randint(10000, 99999),
                              os.path.splitext(filename)[1])

    f.save(os.path.join(app.config.get('CV_UPLOAD_FOLDER'), new_name))

def _save_application(form, app_id=None):
    dob = datetime.datetime.combine(form.dob.data,
                                    datetime.datetime.min.time())

    if app_id is None:
        application = StudentApplication()
    else:
        application = StudentApplication.query.get(app_id)

    application.first_name = form.first_name.data
    application.last_name = form.last_name.data
    application.email = form.email.data
    application.pin = form.pin.data
    application.street = form.street.data
    application.city = form.city.data
    application.postal_code = form.postal_code.data
    application.country = form.country.data
    application.dob = dob
    application.gender = form.gender.data
    application.t_shirt_size = form.t_shirt_size.data
    application.comment = form.comment.data
    application.cell_number = form.cell_number.data

    application.institution = Institution.query.get(form.institution.data)
    application.categories = []

    for cat_id in form.categories.data:
        application.categories.append(Category.query.get(cat_id))

    if app_id is None:
        db.session.add(application)
    db.session.commit()

def _prepopulated_form(application):
    form = ApplicationForm()
    form.first_name.data = application.first_name
    form.last_name.data = application.last_name
    form.email.data = application.email
    form.pin.data = application.pin
    form.street.data = application.street
    form.city.data = application.city
    form.postal_code.data = application.postal_code
    form.country.data = application.country
    form.dob.data = application.dob
    form.gender.data = application.gender
    form.t_shirt_size.data = application.t_shirt_size
    form.cell_number = form.cell_number.data
    form.comment.data = application.comment
    form.institution.data = application.institution.id
    form.gdpr_checkbox.data = True

    form.categories.data = [c.id for c in application.categories]
    form.component.data = application.categories[0].component.id
    return form

def _get_allowed_components(institution_id, gender=None):
    institution = Institution.query.get(institution_id)
    components = []
    components_visited = set()
    for cat in institution.categories:
        if gender is not None and cat.gender_constraint not in (None, gender):
            continue
        if cat.component_id in components_visited:
            continue
        components.append({'id': cat.component.id,
                           'name':cat.component.name,
                           'choice_limit': cat.component.choice_limit,
                           'cv_required': cat.component.cv_required})
        components_visited.add(cat.component.id)
    return list(components)

@app_form.route('/', methods=['GET', 'POST'])
def index():
    app_id = request.args.get('edit')
    if app_id is not None and request.method == 'GET':
        app_id = int(app_id)
        form = _prepopulated_form(StudentApplication.query.get(app_id))
    else:
        form = ApplicationForm()
    pdnames = [field.name for field in form]
    pdnames = pdnames[:pdnames.index('institution')+1]
    if form.validate_on_submit():
        _save_application(form, app_id)
        _save_file(form)
        if request.args.get('adret') is  None:
            #return redirect(url_for('app_form.success', institution=form.institution.data))
            return redirect('https://stemgames.hr/pre-applications/success?institution=%d'%form.institution.data)
        else:
            #return redirect(url_for('app_form.admin'))
            return redirect('https://stemgames.hr/pre-applications/admin')
    return render_template('index.html', form=form, pdnames=pdnames, app_id=app_id)

@app_form.route('/allowed_categories')
def ajax_categories():
    institution_id = int(request.args.get('institution'))
    component_id = int(request.args.get('component'))
    gender = request.args.get('gender')

    inst_categories = Institution.query.get(institution_id).categories
    data = [{'id': cat.id, 'name': cat.name} for cat in inst_categories if
            cat.component_id == component_id and cat.gender_constraint in (None, gender)]
    response = make_response(json.dumps(data))
    response.content_type='application/json'
    return response

@app_form.route('/allowed_components')
def ajax_components():
    institution_id = int(request.args.get('institution'))
    gender = request.args.get('gender')

    data = _get_allowed_components(institution_id, gender)
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response

@app_form.route('/representatives')
def ajax_representatives():
    institution_id = int(request.args.get('institution'))
    representatives = Institution.query.get(institution_id).representatives

    data = [{'name':'%s %s'%(r.first_name, r.last_name), 'email':r.email} for r in representatives]
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response

@app_form.route('/success')
def success():
    institution_id = int(request.args.get('institution'))
    representatives = Institution.query.get(institution_id).representatives
    data = [{'name':'%s %s'%(r.first_name, r.last_name), 'email':r.email} for r in representatives]

    return render_template('success.html', rep_data=data)

def filter_applications(str_id):
    if not str_id.isdigit():
        return StudentApplication.query.all()
    else:
        return StudentApplication.query.filter_by(institution_id=int(str_id)).all()

@app_form.route('/applications')
@auth.login_required
def ajax_applications():
    inst_limit = user_institution_limit()
    if inst_limit is not None:
        str_id = str(inst_limit)
    else:
        str_id = request.args.get('institution', '')
    apps = filter_applications(str_id)
    data = [{'id': app.id,
             'first_name':app.first_name,
             'last_name':app.last_name,
             'email':app.email,
             'institution':app.institution.name,
             'component':app.categories[0].component.name} for app in apps]
    data = {'data':data}
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response


@app_form.route('/application/<app_id>')
@auth.login_required
def ajax_application_details(app_id):
    app = StudentApplication.query.get(int(app_id))
    app_data = {'first_name': app.first_name,
                'last_name': app.last_name,
                'email': app.email,
                'gender': app.gender,
                'street':app.street,
                'city':app.city,
                'postal_code':app.postal_code,
                'country':app.country,
                'pin': app.pin,
                'dob': datetime.datetime.strftime(app.dob,'%F'),
                't_shirt_size': app.t_shirt_size,
                'institution': app.institution.name,
                'comment': app.comment,
                'component': app.categories[0].component.name,
                'categories':[c.name for c in app.categories],
                }
    response = make_response(json.dumps(app_data))
    response.content_type = 'application/json'
    return response

@app_form.route('/application/<app_id>', methods=['DELETE'])
@auth.login_required
def ajax_application_delete(app_id):
    app = StudentApplication.query.get(app_id)
    db.session.delete(app)
    db.session.commit()
    return '{"response":"Success"}'

@app_form.route('/admin')
@auth.login_required
def admin():
    inst_limit = user_institution_limit()
    insts = json.dumps({str(i.id):i.name for i in Institution.query.all() \
                            if inst_limit is None or i.id==inst_limit})
    return render_template('admin.html', institutions=insts,
                           hide_select=(inst_limit is not None))


@app_form.route('/statistics')
def stats():
    ids = {'problem':1, 'sports':2, 'esports':3, 'support':4}
    current_institution = request.args.get('institution')
    if not current_institution: current_institution = '-1'
    applications = filter_applications(current_institution)

    institutions = list(Institution.query.all())
    inst_ctr = collections.Counter()
    for app in filter_applications('all'):
        inst_ctr[app.institution.name] += 1

    inst_dist = {'labels':list(inst_ctr.keys()),
                 'data':list(inst_ctr.values())}

    comp_dist = collections.Counter()
    for app in applications:
        comp_dist[app.categories[0].component_id] += 1

    cat_dist={}
    for key in ids.values():
        ctr = collections.Counter()
        for app in applications:
            for cat in app.categories:
                if cat.component_id == key:
                    ctr[cat.name] += 1
        cat_dist[str(key)]=list(zip(*ctr.items()))

    timestamps = [app.timestamp for app in applications]

    now = datetime.datetime.now()
    hour_ago = now - datetime.timedelta(hours=1)
    start_of_day = datetime.datetime(now.year, now.month, now.day)
    start_of_week = start_of_day - datetime.timedelta(days=now.weekday())

    apps_all_time = len(timestamps)
    apps_last_hour = sum(1 for t in timestamps if t>hour_ago)
    apps_today = sum(1 for t in timestamps if t>start_of_day)
    apps_this_week = sum(1 for t in timestamps if t>start_of_week)

    numdata = {'total':apps_all_time,
               'today':apps_today,
               'week':apps_this_week,
               'hour':apps_last_hour,
               'problem':comp_dist[1],
               'sports':comp_dist[2],
               'esports':comp_dist[3],
               'support':comp_dist[4]}

    json_strings = {'time_stamps': json.dumps([str(t) for t in timestamps]),
                    'category_distribution': json.dumps(cat_dist),
                    'institution_distribution': json.dumps(inst_dist),
                    'numeric_data': json.dumps(numdata),
                    'institutions': json.dumps({str(i.id):i.name for i in institutions})}
    return render_template('stats.html', json_strings=json_strings,
                            current_institution=current_institution)

