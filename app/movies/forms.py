from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,SelectField
from wtforms.validators import DataRequired, Length
from app.models import Movie

class SearchForm(FlaskForm):
    searchString = StringField('Search', validators=[DataRequired(), Length(min=2, max=200)])
    submit = SubmitField('Search Movies')

class AnalyticsViewerForm(FlaskForm):
    friend_username = SelectField("View analytics for", coerce=str)
    submit = SubmitField("Load Analytics")