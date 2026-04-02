from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, Store, MenuItem, Order, OrderItem, Review, User

customer_bp = Blueprint("customer", __name__)


@customer_bp.route("/stores", methods=["GET"])
@jwt_required()
def list_stores():
    """List all open stores. Optional filter by category and search by name."""
    category = request.args.get("category", "").strip()
    search = request.args.get("search", "").strip()

    query = Store.query

    if category and category.lower() != "all":
        query = query.filter(Store.category.ilike(f"%{category}%"))

    if search:
        query = query.filter(Store.name.ilike(f"%{search}%"))

    stores = query.all()
    return jsonify([s.to_dict() for s in stores]), 200


@customer_bp.route("/stores/<int:store_id>/menu", methods=["GET"])
@jwt_required()
def get_store_menu(store_id):
    """Get menu items for a specific store."""
    store = Store.query.get(store_id)
    if not store:
        return jsonify({"error": "Store not found"}), 404

    items = MenuItem.query.filter_by(store_id=store_id).all()
    return jsonify({
        "store": store.to_dict(),
        "items": [item.to_dict() for item in items],
    }), 200


@customer_bp.route("/cart/checkout", methods=["POST"])
@jwt_required()
def checkout():
    """Place an order. Expects: { store_id, address, items: [{item_id, qty}] }"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    store_id = data.get("store_id")
    address = data.get("address", "").strip()
    cart_items = data.get("items", [])

    if not store_id or not cart_items:
        return jsonify({"error": "store_id and items are required"}), 400

    if not address:
        user = User.query.get(user_id)
        address = user.address if user else "Not provided"

    store = Store.query.get(store_id)
    if not store:
        return jsonify({"error": "Store not found"}), 404

    if not store.is_open:
        return jsonify({"error": "This store is currently closed"}), 400

    # Build order items and calculate total
    order_items = []
    subtotal = 0.0

    for ci in cart_items:
        menu_item = MenuItem.query.get(ci.get("item_id"))
        if not menu_item:
            continue
        qty = ci.get("qty", 1)
        item_total = menu_item.price * qty
        subtotal += item_total

        order_items.append(OrderItem(
            item_id=menu_item.id,
            item_name=menu_item.name,
            qty=qty,
            price=menu_item.price,
        ))

    delivery_fee = 30.0
    total = subtotal + delivery_fee

    order = Order(
        customer_id=user_id,
        store_id=store_id,
        status="pending",
        total=total,
        address=address,
    )
    db.session.add(order)
    db.session.flush()

    for oi in order_items:
        oi.order_id = order.id
        db.session.add(oi)

    db.session.commit()

    return jsonify({
        "message": "Order placed successfully",
        "order": order.to_dict(),
    }), 201


@customer_bp.route("/orders/my", methods=["GET"])
@jwt_required()
def my_orders():
    """Get all orders for the current customer, newest first."""
    user_id = int(get_jwt_identity())
    orders = Order.query.filter_by(customer_id=user_id).order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders]), 200


@customer_bp.route("/orders/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    """Get a single order detail."""
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order.to_dict()), 200


@customer_bp.route("/orders/<int:order_id>/review", methods=["POST"])
@jwt_required()
def submit_review(order_id):
    """Submit a review for a delivered order."""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.customer_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    if order.status != "delivered":
        return jsonify({"error": "Can only review delivered orders"}), 400

    existing = Review.query.filter_by(order_id=order_id, customer_id=user_id).first()
    if existing:
        return jsonify({"error": "You already reviewed this order"}), 409

    rating = data.get("rating", 5)
    comment = data.get("comment", "").strip()

    if rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    review = Review(
        order_id=order_id,
        customer_id=user_id,
        rating=rating,
        comment=comment,
    )
    db.session.add(review)
    db.session.commit()

    return jsonify({
        "message": "Review submitted",
        "review": review.to_dict(),
    }), 201
