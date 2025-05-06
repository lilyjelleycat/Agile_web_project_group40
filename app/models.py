from app import db

class Movie(db.Model):
    __tablename__ = 'movie'
    tconst = db.Column(db.Text, primary_key=True)
    primaryTitle = db.Column(db.Text, nullable=False)
    originalTitle = db.Column(db.Text, nullable=False)
    poster_link = db.Column(db.Text, nullable=False)
    startYear = db.Column(db.Integer, nullable=False)
    genres = db.Column(db.Text, nullable=False)
    certificate = db.Column(db.Text, nullable=False)
    runtimeMinutes = db.Column(db.Integer, nullable=False)
    director = db.Column(db.Text, nullable=False)
    star1 = db.Column(db.Text, nullable=False)
    star2 = db.Column(db.Text, nullable=False)
    star3 = db.Column(db.Text, nullable=False)
    star4 = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Movie {self.primaryTitle}>'

class Person(db.Model):
    __tablename__ = 'person'
    nconst = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    birthYear = db.Column(db.Integer, nullable=False)
    deathYear = db.Column(db.Integer, nullable=False)
    primaryProfession = db.Column(db.Text, nullable=False)
    knownForTitles = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Person {self.name}>'

class Principal(db.Model):
    __tablename__ = 'principal'
    tconst = db.Column(db.Text, db.ForeignKey('movie.tconst'), primary_key=True)
    ordering = db.Column(db.Integer, primary_key=True)
    nconst = db.Column(db.Text, db.ForeignKey('person.nconst'), primary_key=True)
    category = db.Column(db.Text, nullable=False)
    job = db.Column(db.Text, nullable=False)
    characters = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Principal {self.tconst}>'

class Member(db.Model):
    __tablename__ = 'member'
    username = db.Column(db.Text, primary_key=True)
    firstName = db.Column(db.Text, nullable=False)
    lastName = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    hashPwd = db.Column(db.Text, nullable=False)
    UserRoles = db.relationship('UserRole', backref='member', lazy=True)
 
    def __repr__(self):
        return f'<Member {self.firstName} {self.lastName}>'

class Roles(db.Model):
    __tablename__ = 'roles'
    role = db.Column(db.Text, primary_key=True, nullable=False)
    UserRoles = db.relationship('UserRole', backref='roles', lazy=True)

    def __repr__(self):
        return f'<Roles {self.role}>'

class UserRole(db.Model):
    __tablename__ = 'user_role'
    username = db.Column(db.Text, db.ForeignKey('member.username'), primary_key=True)
    role = db.Column(db.Text, db.ForeignKey('roles.role'), primary_key=True)

    def __repr__(self):
        return f'<UserRole {self.username}>'