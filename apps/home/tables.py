from flask_table import Table, Col

class Results(Table):
    id = Col('Course Id', show=False)
    name = Col('Course name')
    credit_points = Col('Credits')
