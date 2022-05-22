from apps.search_engine import blueprint
from flask import render_template, request, flash, redirect, url_for
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
        search_string = request.form.get("search_string")
        search_string = search_string if len(search_string) > 0 else 'All'
        # Check how many sorting questions were marked as 'Any'
        for q in questions:
            if request.form.get('question-' + str(q.id)) == 'Any':
                count += 1
        # In case all sorting questions were marked as 'Any'
        if count == num_questions:
            # Perform search by  the search string
            return redirect(
                url_for('searchengine_blueprint.search_results', search_string=search_string, category=category,
                        question=0, ratings='0'))
        else:
            # Perform search by the search string and sort the results
            first_id = db.session.query(Questions).first().id
            ratings = []
            # Create a list of tuples of chosen question ids to sort by and the rating
            for q in questions:
                answer = request.form.get('question-' + str(q.id))
                if answer != 'Any':
                    ratings.append((q.id - first_id, int(answer)))
            # Convert ratings to string
            str_ratings = ''
            for r in ratings:
                str_ratings += str(r[0]) + ',' + str(r[1]) + ','
        return redirect(
            url_for('searchengine_blueprint.search_results', search_string=search_string, category=category, question=1,
                    ratings=str_ratings[:-1]))
    return render_template('home/index.html', segment='index', questions=questions, num_questions=num_questions)


@blueprint.route('/results.html?str=<search_string>&category=<category>&question=<question>&ratings=<ratings>')
def search_results(search_string, category, question, ratings):
    question = int(question)
    # Convert ratings to list
    if search_string == 'All':
        search_string = None

    if ratings != '0':
        ratings = ratings.split(',')
        ratings = [(int(ratings[2*i]), int(ratings[2*i + 1])) for i in range(int(len(ratings)/2))]
    else:
        ratings = []
    taken_courses = [course.course_id for course in current_user.courses]

    if search_string:
        results = se.search_course(category, search_string)
        if question == 1 and len(results) > 1:
            results = se.get_closest_courses(ratings, results)
    else:
        qry = db.session.query(Courses)
        results = qry.all()
        # In case at least one question was picked
        if question == 1 and len(results) > 1:
            results = se.get_closest_courses(ratings, results)
    if not results:
        flash('No results found! Please try again.')
        return redirect('/')
    else:
        # display results
        return render_template('home/results.html', results=results, taken_courses=taken_courses)
