from apps.home import blueprint
from flask import render_template, request, flash, redirect
from flask_login import login_required
from apps.home.forms import CourseSearchForm
from apps.authentication.models import *


@blueprint.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    search = CourseSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    return render_template('home/index.html', segment='index', form=search)


@blueprint.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']
    if search_string:
        if search.data['select'] == 'Lecturer':
            qry = db.session.query(Courses, CoursesLecturers).filter(
                Lecturers.id == CoursesLecturers.lecturer_id).filter(
                Lecturers.name.contains(search_string))
            results = [item[0] for item in qry.all()]
        elif search.data['select'] == 'Course':
            qry = db.session.query(Courses).filter(
                Courses.name.contains(search_string))
            results = qry.all()
        elif search.data['select'] == 'Course Number':
            qry = db.session.query(Courses).filter(
                Courses.id.contains(search_string))
            results = qry.all()
        else:
            qry = db.session.query(Courses)
            results = qry.all()
    else:
        qry = db.session.query(Courses)
        results = qry.all()
    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        # display results
        return render_template('results.html', results=results)
