from flask import Flask, jsonify

from utils import get_directory_structure, process_files, get_movie_names

app = Flask(__name__)


@app.route('/')
def movies():
    files = get_directory_structure("M:\\Movies\\Movies")
    process_files(files)

    movie_list = sorted(get_movie_names(files)[1])

    return jsonify({"movies": movie_list, "raw_data": files}), 200


if __name__ == '__main__':
    app.run()
