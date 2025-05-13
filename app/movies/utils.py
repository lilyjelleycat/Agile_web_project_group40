from app.models import Movie

def searchMovies(searchString):
    titleQuery1 = Movie.query.filter(Movie.primaryTitle.ilike(f"%{searchString}%"))
    titleQuery2 = Movie.query.filter(Movie.originalTitle.ilike(f"%{searchString}%"))
    dirQuery = Movie.query.filter(Movie.Director.ilike(f"%{searchString}%"))
    star1Query = Movie.query.filter(Movie.Star1.ilike(f"%{searchString}%"))
    star2Query = Movie.query.filter(Movie.Star2.ilike(f"%{searchString}%"))
    star3Query = Movie.query.filter(Movie.Star3.ilike(f"%{searchString}%"))
    star4Query = Movie.query.filter(Movie.Star4.ilike(f"%{searchString}%"))

    return titleQuery1.union(titleQuery2).union(dirQuery).union(star1Query).union(star2Query).union(star3Query).union(star4Query).all()