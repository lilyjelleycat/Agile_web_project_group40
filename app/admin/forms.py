from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_wtf.file import FileField, FileRequired, FileAllowed
from app.models import Movie

class UploadMoviesForm(FlaskForm):
    file = FileField(
        'Upload Movies File',
        validators=[
            FileRequired(),
            FileAllowed(['csv'], 'Only CSV files are allowed!')
        ]
    )
    submit = SubmitField('Upload')
 
class FindMovieForm(FlaskForm):
    searchString = StringField('Search', validators=[DataRequired(), Length(min=2, max=200)])
    submit = SubmitField('Search Movies')
 
class EditMovieForm(FlaskForm):
    tconst = StringField('Id', validators=[DataRequired(), Length(min=9, max=20)])
    primaryTitle = StringField('Primary Title', validators=[DataRequired(), Length(min=2)])
    originalTitle = StringField('Original Title', validators=[DataRequired(), Length(min=2)])
    Poster_Link = StringField('Poster URL', validators=[DataRequired(), Length(min=2)])
    startYear = IntegerField('Released Year', validators=[DataRequired()])
    genres = StringField('Genres', validators=[DataRequired(), Length(min=2)])
    Certificate = StringField('Certificate', validators=[DataRequired(), Length(min=1)])
    runtimeMinutes = StringField('Runtime', validators=[DataRequired(), Length(min=2)])
    Director = StringField('Director', validators=[DataRequired(), Length(min=2)])
    Star1 = StringField('Star 1', validators=[DataRequired(), Length(min=2)])
    Star2 = StringField('Star 2', validators=[DataRequired(), Length(min=2)])
    Star3 = StringField('Star 3', validators=[DataRequired(), Length(min=2)])
    Star4 = StringField('Star 4', validators=[DataRequired(), Length(min=2)])
    Overview = TextAreaField('Overview', validators=[DataRequired(), Length(min=2)])
    submit = SubmitField('Update Movie')
    
    def setMovieData(self, movie):
        self.tconst.data = movie.tconst
        self.primaryTitle.data = movie.primaryTitle
        self.originalTitle.data = movie.originalTitle
        self.Poster_Link.data = movie.Poster_Link
        self.startYear.data = movie.startYear
        self.genres.data = movie.genres
        self.Certificate.data = movie.Certificate
        self.runtimeMinutes.data = movie.runtimeMinutes
        self.Director.data = movie.Director
        self.Star1.data = movie.Star1
        self.Star2.data = movie.Star2
        self.Star3.data = movie.Star3
        self.Star4.data = movie.Star4
        self.Overview.data = movie.Overview

class AdminChangeUserPasswordForm(FlaskForm):
    new_password = PasswordField(
        "New password", validators=[DataRequired(), Length(min=6, message="The password length should be at least 6 characters")]
    )
    confirm_new_password = PasswordField(
        "Confirm the new password",
        validators=[
            DataRequired(),
            EqualTo("new_password", message="The passwords entered twice are inconsistent"),
        ],
    )
    submit = SubmitField("Submit")