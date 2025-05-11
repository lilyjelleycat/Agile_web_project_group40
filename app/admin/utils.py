from app import db
from app.models import Movie
import pandas as pd

def process_movies_file(filedata):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(filedata)
    
    # Iterate through the DataFrame and add each movie to the database
    for index, row in df.iterrows():
        movieQuery1 = Movie.query.filter(Movie.primaryTitle.ilike(f"%{row['Series_Title']}%"))
        movieQuery2 = Movie.query.filter(Movie.originalTitle.ilike(f"%{row['Series_Title']}%"))
        results = movieQuery1.union(movieQuery2).all()
        if results:
            results[0].Overview = row['Overview']
        else:
            movie = Movie(
                tconst=row['Series_Title'],
                primaryTitle=row['Series_Title'],
                originalTitle=row['Series_Title'],
                Poster_Link=row['Poster_Link'],
                startYear=row['Released_Year'],
                genres=row['Genre'],
                Certificate=row['Certificate'],
                runtimeMinutes=row['Runtime'],
                Director=row['Director'],
                Star1=row['Star1'],
                Star2=row['Star2'],
                Star3=row['Star3'],
                Star4=row['Star4']
            )
            db.session.add(movie)

    db.session.commit()
