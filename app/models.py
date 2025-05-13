from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Member.query.get(user_id)

# Movie Table

class Movie(db.Model):
    __tablename__ = 'movie'

    tconst = db.Column(db.Text, primary_key=True)
    primaryTitle = db.Column(db.Text)
    originalTitle = db.Column(db.Text)
    Poster_Link = db.Column(db.Text)
    startYear = db.Column(db.Integer)
    genres = db.Column(db.Text)
    Certificate = db.Column(db.Text)
    runtimeMinutes = db.Column(db.Integer)
    Director = db.Column(db.Text)
    Star1 = db.Column(db.Text)
    Star2 = db.Column(db.Text)
    Star3 = db.Column(db.Text)
    Star4 = db.Column(db.Text)
    Overview = db.Column(db.Text)
    reviews = db.relationship('Review', backref='has', lazy=True)

    def __repr__(self):
        return f'<Movie {self.primaryTitle}>'

# User Table (Members)
# Inheriting from UserMixin to provide default implementations for user authentication
class Member(db.Model, UserMixin):
    __tablename__ = 'member'
    username = db.Column(db.String, primary_key=True)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    hashPwd = db.Column(db.String, nullable=False)
    reviews = db.relationship('Review', backref='member', lazy=True)
    roles = db.relationship('UserRole', backref='member', lazy=True)
    
    def get_id(self):
        # This method is used by Flask-Login to get the user ID
        # Note that we use username here as this is the primary key
        return self.username
    
    def has_role(self, role_name):
        if self.roles:
            for role in self.roles:
                if role.role == role_name:
                    return True
        return False
    
    def __repr__(self):
        return f'<Member {self.username}>'


# Role Table
class Role(db.Model):
    __tablename__ = 'roles'

    role = db.Column(db.String, primary_key=True)
    users = db.relationship('UserRole', backref='role_obj', lazy=True)

    def __repr__(self):
        return f'<Role {self.role}>'

# UserRole Table
class UserRole(db.Model):
    __tablename__ = 'user_role'

    username = db.Column(db.String, db.ForeignKey('member.username'), primary_key=True)
    role = db.Column(db.String, db.ForeignKey('roles.role'), primary_key=True)

    def __repr__(self):
        return f'<UserRole {self.username} - {self.role}>'

# Review Table
class Review(db.Model):
    __tablename__ = 'review'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_id = db.Column(db.String, db.ForeignKey('movie.tconst'), nullable=False)
    username = db.Column(db.String, db.ForeignKey('member.username'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=True)
    movie = db.relationship('Movie')

    def __repr__(self):
        return f'<Review {self.movie_id} by {self.username}>'
