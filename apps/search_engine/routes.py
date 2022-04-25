from apps.home import blueprint
from flask import render_template, request, flash, redirect
from flask_login import login_required
from apps.authentication.models import *
import apps.search_engine.search as se
from flask_login import current_user

@blueprint.route('/index.html', methods=['GET', 'POST'])
@login_required
def index():
    count = 0
    category = request.form.get("category")
    questions = db.session.query(Questions).all()
    num_questions = db.session.query(Questions).count()
    if request.method == 'POST':
        for q in questions:
            if request.form.get('question-' + str(q.id)) == 'Dont care':
                count +=1
        if count == num_questions:
            return search_results(category, 0, None)
        else:
            first_id = db.session.query(Questions).first().id
            ratings = []
            for q in questions:
                answer = request.form.get('question-' + str(q.id))
                if answer != 'Dont care':
                    ratings.append((q.id - first_id, int(answer)))
        return search_results(category, 1, ratings)
    return render_template('home/index.html', segment='index', questions=questions, num_questions=num_questions)


@blueprint.route('/results.html')
def search_results(search, question, ratings):
    taken_courses = [course.course_id for course in current_user.courses]
    search_string = request.form.get("search_string")
    if search_string:
        results = se.search_course(search, search_string)
        if question == 1 and len(results) > 1:
            results = se.get_closest_courses(ratings, results)
    else:
        qry = db.session.query(Courses)
        results = qry.all()
        if question == 1 and len(results) > 1:
            results = se.get_closest_courses(ratings, results)
    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        # display results
        return render_template('home/results.html', results=results, taken_courses=taken_courses)
