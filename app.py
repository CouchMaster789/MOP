import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from routes import bp
    app.register_blueprint(bp)

    check_dirs()

    @app.shell_context_processor
    def make_shell_context():
        from models import Source, Movie, File

        return dict(app=app, db=db, Source=Source, Movie=Movie, File=File)

    return app


def check_dirs():
    if not os.path.isdir("static"):
        os.mkdir("static")
    media_dir = os.path.join("static", "media")
    if not os.path.isdir(media_dir):
        os.mkdir(media_dir)
    movies_dir = os.path.join("static", "media", "movies")
    if not os.path.isdir(movies_dir):
        os.mkdir(movies_dir)


if __name__ == '__main__':
    create_app().run()
