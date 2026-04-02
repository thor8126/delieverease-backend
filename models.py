from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer")  # customer | rider | merchant
    address = db.Column(db.String(256), default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    stores = db.relationship("Store", backref="merchant", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "address": self.address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Store(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False, default="Food")
    is_open = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(256), default="")

    menu_items = db.relationship("MenuItem", backref="store", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "merchant_id": self.merchant_id,
            "name": self.name,
            "category": self.category,
            "is_open": self.is_open,
            "image_url": self.image_url,
        }


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "store_id": self.store_id,
            "name": self.name,
            "price": self.price,
            "is_available": self.is_available,
        }


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), nullable=False)
    rider_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="pending")  # pending | accepted | picked_up | delivered
    total = db.Column(db.Float, nullable=False, default=0.0)
    address = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    customer = db.relationship("User", foreign_keys=[customer_id], backref="customer_orders")
    store = db.relationship("Store", backref="orders")
    rider = db.relationship("User", foreign_keys=[rider_id], backref="rider_orders")
    items = db.relationship("OrderItem", backref="order", lazy=True)
    reviews = db.relationship("Review", backref="order", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "store_id": self.store_id,
            "rider_id": self.rider_id,
            "status": self.status,
            "total": self.total,
            "address": self.address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "store_name": self.store.name if self.store else None,
            "customer_name": self.customer.name if self.customer else None,
            "rider_name": self.rider.name if self.rider else None,
            "items": [item.to_dict() for item in self.items],
            "review": self.reviews[0].to_dict() if self.reviews else None,
        }


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=True)
    item_name = db.Column(db.String(120), nullable=False)
    qty = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "item_id": self.item_id,
            "item_name": self.item_name,
            "qty": self.qty,
            "price": self.price,
        }


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    customer = db.relationship("User", backref="reviews")

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
