# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import flask_login
from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
import apps.for_you.recommendations as rs
import apps.questions as qs
from apps.home.routes import get_segment


@blueprint.route('/for-you.html')
def for_you():
    segment = get_segment(request)
    return render_template("home/" + 'for-you.html', segment=segment,
                           courses=rs.recommend_courses(flask_login.current_user))