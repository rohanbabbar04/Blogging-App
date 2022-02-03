from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class SearchForm(FlaskForm):
    string = StringField('Search', render_kw={"placeholder": "Search content"})
    search_button = SubmitField('Search')
