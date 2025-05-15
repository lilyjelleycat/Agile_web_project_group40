from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length
from app.models import Movie

class SearchForm(FlaskForm):
    searchString = StringField('Search', validators=[DataRequired(), Length(min=2, max=200)])
    submit = SubmitField('Search Movies')

class AnalyticsViewerForm(FlaskForm):
    friend_username = SelectField("View analytics for", coerce=str)
    submit = SubmitField("Load Analytics")
    
class EditReviewForm(FlaskForm):
    review_id = HiddenField("Review ID")
    rating = SelectField("Rating", choices=[(str(i), i) for i in range(1, 6)], validators=[DataRequired()])
    content = TextAreaField("Review", validators=[DataRequired()])
    submit = SubmitField("Update Review")
