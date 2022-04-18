from wtforms import Form, StringField, SelectField

class CourseSearchForm(Form):
    choices = [('Lecturer', 'Lecturer'),
               ('Course', 'Course'),
               ('Course Number', 'Course Number')]
    select = SelectField('Search for Course:', choices=choices)
    search = StringField('')

