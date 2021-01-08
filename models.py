import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from app import db


class Source(db.Model):
    __tablename__ = "sources"

    id = db.Column(db.Integer, primary_key=True)

    address = db.Column(db.String(256))

    def __init__(self, address):
        self.address = address

    def __repr__(self):
        return f"<Source {self.id}>"


class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime)

    filename = db.Column(db.String(256))
    path = db.Column(db.String(2048))

    # marked means that the data has been inferred from the filename
    marked_codec = db.Column(db.String(16))
    marked_edition = db.Column(db.String(32))
    marked_resolution = db.Column(db.String(8))
    marked_sample = db.Column(db.Boolean)
    marked_source = db.Column(db.String(8))
    marked_title = db.Column(db.String(256))
    marked_year = db.Column(db.DateTime)

    def __init__(self, full_path, marked_codec=None, marked_edition=None, marked_resolution=None, marked_sample=None,
                 marked_source=None, marked_title=None, marked_year=None):
        self.created_at = datetime.datetime.now()

        self.filename = full_path[full_path.rfind("\\") + 1:]
        self.path = full_path[:full_path.rfind("\\") + 1]

        self.marked_codec = marked_codec
        self.marked_edition = marked_edition
        self.marked_resolution = marked_resolution
        self.marked_sample = marked_sample
        self.marked_source = marked_source
        self.marked_title = marked_title
        self.marked_year = marked_year

    def __repr__(self):
        return f"<Movie {self.id}>"

    @hybrid_property
    def file_type(self):
        return self.filename[self.filename.rfind("."):]
