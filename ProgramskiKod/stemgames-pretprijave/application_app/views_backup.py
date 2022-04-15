import datetime
import collections
import json
import os
import random

from flask import Blueprint, render_template, flash, redirect, url_for
from flask import request, abort, jsonify, make_response
from werkzeug.utils import secure_filename

from . import db

from flask import current_app as app

from .forms import ApplicationForm
from .models import StudentApplication, Category, Component, Institution

app_form = Blueprint('app_form', __name__)

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

def _save_application(form):
    dob = datetime.datetime.combine(form.dob.data,
                                    datetime.datetime.min.time())
    application = StudentApplication(first_name = form.first_name.data,
                                     last_name = form.last_name.data,
                                     email = form.email.data,
                                     cell_number = form.cell_number.data,
                                     pin = form.pin.data,
                                     street = form.street.data,
                                     city = form.city.data,
                                     postal_code = form.postal_code.data,
                                     country = form.country.data,
                                     dob = dob,
                                     gender = form.gender.data,
                                     t_shirt_size = form.t_shirt_size.data,
                                     comment = form.comment.data
            )
    application.institution = Institution.query.get(form.institution.data)

    for cat_id in form.categories.data:
        application.categories.append(Category.query.get(cat_id))
    db.session.add(application)
    db.session.commit()

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
    form = ApplicationForm()
    pdnames = [field.name for field in form]
    pdnames = pdnames[:pdnames.index('institution')+1]
    if form.validate_on_submit():
        _save_application(form)
        _save_file(form)
        #return redirect(url_for('app_form.success', institution=form.institution.data))
        return redirect('https://stemgames.hr/pre-applications/success?institution=%d'%form.institution.data)
    return render_template('index.html', form=form, pdnames=pdnames)

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
