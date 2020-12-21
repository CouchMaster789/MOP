from flask import Flask, jsonify, render_template, redirect, url_for, request

from config import Config
from tmdb import get_movie_data
from utils import get_directory_structure, process_files, get_movie_names

app = Flask(__name__)
app.config.from_object(Config)

if not app.config["MOVIE_DIR"]:
    app.logger.critical("Please restart app with the MOVIE_DIR set")
    # TODO: add some redirect functionality in this case


@app.route("/")
def index():
    return redirect(url_for("movies"))


@app.route("/movies", methods=["GET", "POST"])
def movies():
    if request.method == "GET":
        return render_template("movies.html")

    files = get_directory_structure(app.config["MOVIE_DIR"])
    process_files(files)

    movie_list = sorted(get_movie_names(files))

    return jsonify({
        "movies": movie_list,
        "recordsTotal": len(movie_list),
    }), 200


@app.route('/local_movies')
def local_movies():
    files = get_directory_structure(app.config["MOVIE_DIR"])
    process_files(files)

    movie_list = sorted(get_movie_names(files))

    return jsonify({"movies": movie_list, "raw_data": files}), 200


@app.route('/remote_data')
def remote_data():
    files = get_directory_structure(app.config["MOVIE_DIR"])
    process_files(files)

    movies = []

    for movie in sorted(get_movie_names(files)):
        movies.append(get_movie_data(movie))

    return jsonify({"movies": movies}), 200


if __name__ == '__main__':
    app.run()
