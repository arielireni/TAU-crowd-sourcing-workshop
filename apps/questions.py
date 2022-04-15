from apps.authentication.models import *


def get_questions():
    return Questions.query.all()

# TODO: return the answers to the DB
