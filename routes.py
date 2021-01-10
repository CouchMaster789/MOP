from flask import jsonify, render_template, redirect, url_for, request, Blueprint, current_app

from app import db
from models import Source, Movie
from tmdb import get_movie_data
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
            "filename": movie.filename,
            "path": movie.path,
            "marked": {
                "title": movie.marked_title,
                "year": movie.marked_year,
                "source": movie.marked_source,
                "resolution": movie.marked_resolution,
                "edition": movie.marked_edition,
                "codec": movie.marked_codec,
            }
        }
        for movie in Movie.query.order_by(Movie.marked_title).all()
    ]

    return jsonify({
        "movies": movies_dict,
        "movie_count": len(movies_dict),
        "source_count": num_sources,
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
