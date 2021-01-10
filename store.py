"""
functions for computing the necessary storage of media metadata
"""
import os

from app import create_app, db
from models import Source, Movie, compute_hash
from utils import get_flat_movies


def scan_and_store(*sources):
    """scans and stores metadata (for media found at sources) into db"""

    movies = {os.path.join(movie.path, movie.filename): movie for movie in Movie.query.all()}

    for source in sources:
        for scanned_movie in get_flat_movies(source):
            if not check_movie_exists(movies, scanned_movie):
                add_movie(scanned_movie)
            else:
                update_movie(movies, scanned_movie)

    db.session.commit()


def add_movie(movie):
    db.session.add(
        Movie(movie["path"], movie["marked"]["original_filename"],
              marked_codec=movie["marked"]["codec"], marked_edition=movie["marked"]["edition"],
              marked_resolution=movie["marked"]["resolution"], marked_sample=movie["marked"]["sample"],
              marked_source=movie["marked"]["source"], marked_title=movie["marked"]["title"],
              marked_year=movie["marked"]["year"])
    )


def update_movie(movies, scanned_movie):
    movie_to_update = movies[os.path.join(scanned_movie["path"], scanned_movie["marked"]["original_filename"])]

    if compute_movie_hash(scanned_movie) != movie_to_update.obj_hash:
        movie_to_update.marked_codec = scanned_movie["marked"]["codec"]
        movie_to_update.marked_edition = scanned_movie["marked"]["edition"]
        movie_to_update.marked_resolution = scanned_movie["marked"]["resolution"]
        movie_to_update.marked_sample = scanned_movie["marked"]["sample"]
        movie_to_update.marked_source = scanned_movie["marked"]["source"]
        movie_to_update.marked_title = scanned_movie["marked"]["title"]
        movie_to_update.marked_year = scanned_movie["marked"]["year"]


def check_movie_exists(movies, movie):
    return os.path.join(movie["path"], movie["marked"]["original_filename"]) in movies


def compute_movie_hash(movie):
    return compute_hash(movie["path"], movie["marked"]["original_filename"], movie["marked"]["codec"],
                        movie["marked"]["edition"], movie["marked"]["resolution"], movie["marked"]["sample"],
                        movie["marked"]["source"], movie["marked"]["title"], movie["marked"]["year"])


if __name__ == '__main__':
    with create_app().app_context():
        # Movie.query.delete()
        # db.session.commit()

        scan_and_store(*Source.query.all())
