from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Category(db.Model):
    __tablename__ = "category"
    id = db.Column('category_id',db.Integer(), primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    price = db.Column(db.Float())
    image_name = db.Column(db.String(255),default="robe_defaut.jpg")
    size = db.Column(db.String)
    products = db.relationship("Product", backref="categories", lazy='dynamic')
    def __repr__(self):
        return self.name

    @property
    def url(self):
        from run import images

        return images.url(self.image_name)

    @property
    def filepath(self):
        from run import images

        if self.image_name is None:
            return
        return images.path(self.image_name)


class Product(db.Model):
    __tablename__ = "product"
    id = db.Column("id", db.Integer(), primary_key=True)
    name = db.Column("name", db.String(255), nullable=False)
    price = db.Column(db.Float())
    size = db.Column(db.String)
    image_name = db.Column(db.String(255),default="robe_defaut.jpg")
    created_at = db.Column(db.Date, nullable=True, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'))
    category = db.relationship('Category')

    def __repr__(self):
        return self.name

    @property
    def url(self):
        from run import images

        return images.url(self.image_name)

    @property
    def filepath(self):
        from run import images

        if self.image_name is None:
            return
        return images.path(self.image_name)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column("id", db.Integer(), primary_key=True)
    name = db.Column("name", db.String(255))
    phone = db.Column("phone", db.String(255))
    email = db.Column("email", db.String(255), unique=True)
    password = db.Column("password", db.String(255))
    created_at = db.Column(db.Date, nullable=True, default=datetime.utcnow)

    def __repr__(self):
        return self.name

