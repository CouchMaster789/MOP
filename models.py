from app import db


class Source(db.Model):
    __tablename__ = "sources"

    id = db.Column(db.Integer, primary_key=True)

    address = db.Column(db.String(256))

    def __init__(self, address):
        self.address = address
