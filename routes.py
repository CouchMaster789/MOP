from flask import jsonify, render_template, redirect, url_for, request, Blueprint, current_app

from tmdb import get_movie_data
from utils import get_directory_structure, process_files, get_movie_names

bp = Blueprint('movies', __name__, url_prefix="/")


@bp.route("/")
def index():
    return redirect(url_for("movies"))


@bp.route("/movies", methods=["GET", "POST"])
def movies():
    if request.method == "GET":
        return render_template("movies.html")

    files = get_directory_structure(current_app.config["MOVIE_DIR"])
    process_files(files)

    movie_list = sorted(get_movie_names(files))

    return jsonify({
        "movies": movie_list,
        "recordsTotal": len(movie_list),
    }), 200


@bp.route('/local_movies')
def local_movies():
    files = get_directory_structure(current_app.config["MOVIE_DIR"])
    process_files(files)

    movie_list = sorted(get_movie_names(files))

    return jsonify({"movies": movie_list, "raw_data": files}), 200


@bp.route('/remote_data')
def remote_data():
    files = get_directory_structure(current_app.config["MOVIE_DIR"])
    process_files(files)

    movies = []

    for movie in sorted(get_movie_names(files)):
        movies.append(get_movie_data(movie))

    return jsonify({"movies": movies}), 200
