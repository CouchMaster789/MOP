import os

from flask import jsonify, render_template, redirect, url_for, request, Blueprint

from app import db
from models import Source, Movie
from utils import get_directory_structure, process_files, flatten_movie_results

bp = Blueprint('movies', __name__, url_prefix="/")


@bp.route("/")
def index():
    return redirect(url_for("movies.movies"))


@bp.route("/movies", methods=["GET", "POST"])
def movies():
    if request.method == "GET":
        return render_template("movies.html")

    num_sources = Source.query.count()
    movies_dict = [
        {
            "id": movie.id,
            "img_path": os.path.join(movie.web_path, movie.files[0].name) if movie.files else "#",
            "title": movie.title,
            "overview": movie.overview,
            "year": movie.release_year,
            "runtime": movie.runtime,
            "vote_average": movie.vote_average,
            "vote_count": movie.vote_count,
        }
        for movie in Movie.query.order_by(Movie.vote_average.desc()).all()
    ]

    return jsonify({
        "movies": movies_dict,
        "movie_count": len(movies_dict),
        "source_count": num_sources,
    }), 200


@bp.route("/movie/<movie_id>", methods=["POST"])
def movie(movie_id):
    movie = Movie.query.filter_by(id=movie_id).first_or_404()

    return jsonify({
        "id": movie.id,
        "filename": movie.filename,
        "path": movie.path,
        "img_path": os.path.join(movie.web_path, movie.files[0].name) if movie.files else "#",
        "marked": {
            "title": movie.marked_title,
            "year": movie.marked_year,
            "source": movie.marked_source,
            "resolution": movie.marked_resolution,
            "edition": movie.marked_edition,
            "codec": movie.marked_codec,
        },
        "tmdb": {
            "tmdb_last_checked": movie.tmdb_last_checked,
            "tmdb_id": movie.tmdb_id,
            "imdb_id": movie.imdb_id,
            "title": movie.title,
            "original_title": movie.original_title,
            "overview": movie.overview,
            "adult": movie.adult,
            "popularity": movie.popularity,
            "release_date": movie.release_date,
            "release_year": movie.release_year,
            "revenue": movie.revenue,
            "runtime": movie.runtime,
            "status": movie.status,
            "tagline": movie.tagline,
            "vote_average": movie.vote_average,
            "vote_count": movie.vote_count}
    }), 200


@bp.route("sources")
def sources_page():
    return render_template("sources.html", sources=Source.query.all())


@bp.route("update_sources", methods=["POST"])
def update_sources():
    # deliberately taken a quicker approach in terms of front end to just submit all sources and reconcile changes on
    # server

    sources = Source.query.all()
    sources = {source.address: source for source in sources}

    new_address = request.form.getlist("sources[]")

    # add new addresses
    for address in new_address:
        if address and address not in sources:
            db.session.add(Source(address))

    # remove old addresses
    for source in sources:
        if source not in new_address:
            db.session.delete(sources[source])

    db.session.commit()

    return jsonify(), 200


@bp.route('/local_movies')
def local_movies():
    sources = Source.query.all()

    files = {}
    for source in sources:
        key = source.address[:source.address.rfind("\\")]
        if key not in files:
            files[key] = {}

        files[source.address[:source.address.rfind("\\")]].update(get_directory_structure(source.address))

    process_files(files)

    movie_list = sorted(flatten_movie_results(files), key=lambda key: key["marked"]["title"])

    return jsonify({"movies": movie_list, "raw_data": files}), 200
