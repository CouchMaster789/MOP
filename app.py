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

    @app.shell_context_processor
    def make_shell_context():
        from models import Source

        return dict(app=app, db=db, Source=Source)

    return app


if __name__ == '__main__':
    create_app().run()
