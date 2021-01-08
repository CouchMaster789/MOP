"""
functions for computing the necessary storage of media metadata
"""

import os

from app import create_app, db
from models import Source, Movie
from utils import get_flat_movies


def scan_and_store(*sources):
    """scans and stores metadata (for media found at sources) into db"""

    movies = {os.path.join(movie.path, movie.filename): movie for movie in Movie.query.all()}

    for source in sources:
        for movie in get_flat_movies(source):
            if not check_movie_exists(movies, movie):
                add_movie(movie)
            else:
                update_movie(movies, movie)

    db.session.commit()


def add_movie(movie):
    db.session.add(
        Movie(movie["path"], movie["marked"]["original_filename"],
              marked_codec=movie["marked"]["codec"], marked_edition=movie["marked"]["edition"],
              marked_resolution=movie["marked"]["resolution"], marked_sample=movie["marked"]["sample"],
              marked_source=movie["marked"]["source"], marked_title=movie["marked"]["title"],
              marked_year=movie["marked"]["year"])
    )


def update_movie(movies, movie):
    movie_to_update = movies[os.path.join(movie["path"], movie["marked"]["original_filename"])]
    movie_to_update.marked_codec = movie["marked"]["codec"]
    movie_to_update.marked_edition = movie["marked"]["edition"]
    movie_to_update.marked_resolution = movie["marked"]["resolution"]
    movie_to_update.marked_sample = movie["marked"]["sample"]
    movie_to_update.marked_source = movie["marked"]["source"]
    movie_to_update.marked_title = movie["marked"]["title"]
    movie_to_update.marked_year = movie["marked"]["year"]


def check_movie_exists(movies, movie):
    return os.path.join(movie["path"], movie["marked"]["original_filename"]) in movies


if __name__ == '__main__':
    with create_app().app_context():
        import time

        start = time.time()

        scan_and_store(*Source.query.all())

        print(time.time() - start)
