from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, Store, MenuItem, Order, User

merchant_bp = Blueprint("merchant", __name__, url_prefix="/merchant")


def _require_merchant():
    """Helper to verify merchant role and get their store."""
    claims = get_jwt()
    if claims.get("role") != "merchant":
        return None, None, (jsonify({"error": "Merchant access required"}), 403)
    merchant_id = int(get_jwt_identity())
    store = Store.query.filter_by(merchant_id=merchant_id).first()
    return merchant_id, store, None


@merchant_bp.route("/orders", methods=["GET"])
@jwt_required()
def incoming_orders():
    """Get all orders for the merchant's store."""
    merchant_id, store, err = _require_merchant()
    if err:
        return err
    if not store:
        return jsonify({"error": "No store found for this merchant"}), 404

    status_filter = request.args.get("status", "").strip()
    query = Order.query.filter_by(store_id=store.id)

    if status_filter:
        query = query.filter_by(status=status_filter)

    orders = query.order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders]), 200


@merchant_bp.route("/orders/<int:order_id>/accept", methods=["PUT"])
@jwt_required()
def accept_order(order_id):
    """Accept or reject an order."""
    merchant_id, store, err = _require_merchant()
    if err:
        return err
    if not store:
        return jsonify({"error": "No store found"}), 404

    data = request.get_json()
    action = data.get("action", "accept") if data else "accept"  # accept | reject

    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.store_id != store.id:
        return jsonify({"error": "This order doesn't belong to your store"}), 403

    if action == "reject":
        order.status = "rejected"
        db.session.commit()
        return jsonify({"message": "Order rejected", "order": order.to_dict()}), 200

    if order.status != "pending":
        return jsonify({"error": "Order is not pending"}), 400

    order.status = "accepted"
    db.session.commit()
    return jsonify({"message": "Order accepted", "order": order.to_dict()}), 200


@merchant_bp.route("/menu", methods=["GET"])
@jwt_required()
def get_menu():
    """Get all menu items for merchant's store."""
    merchant_id, store, err = _require_merchant()
    if err:
        return err
    if not store:
        return jsonify({"error": "No store found"}), 404

    items = MenuItem.query.filter_by(store_id=store.id).all()
    return jsonify([item.to_dict() for item in items]), 200


@merchant_bp.route("/menu", methods=["POST"])
@jwt_required()
def add_menu_item():
    """Add a new menu item."""
    merchant_id, store, err = _require_merchant()
    if err:
        return err
    if not store:
        return jsonify({"error": "No store found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name", "").strip()
    price = data.get("price", 0)

    if not name or price <= 0:
        return jsonify({"error": "Name and a positive price are required"}), 400

    item = MenuItem(
        store_id=store.id,
        name=name,
        price=float(price),
        image_url=data.get("image_url", "").strip() or "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400",
        is_available=data.get("is_available", True),
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({"message": "Item added", "item": item.to_dict()}), 201


@merchant_bp.route("/menu/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_menu_item(item_id):
    """Edit or toggle availability of a menu item."""
    merchant_id, store, err = _require_merchant()
    if err:
        return err
    if not store:
        return jsonify({"error": "No store found"}), 404

    item = MenuItem.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    if item.store_id != store.id:
        return jsonify({"error": "Item doesn't belong to your store"}), 403

    data = request.get_json()
    if data:
        if "name" in data:
            item.name = data["name"].strip()
        if "price" in data:
            item.price = float(data["price"])
        if "image_url" in data:
            item.image_url = data["image_url"].strip()
        if "is_available" in data:
            item.is_available = bool(data["is_available"])

    db.session.commit()
    return jsonify({"message": "Item updated", "item": item.to_dict()}), 200


@merchant_bp.route("/summary", methods=["GET"])
@jwt_required()
def summary():
    """Get today's order count and revenue."""
    merchant_id, store, err = _require_merchant()
    if err:
        return err
    if not store:
        return jsonify({"error": "No store found"}), 404

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    today_orders = Order.query.filter(
        Order.store_id == store.id,
        Order.created_at >= today_start,
    ).all()

    pending_count = sum(1 for o in today_orders if o.status == "pending")
    revenue = sum(o.total for o in today_orders if o.status in ["accepted", "picked_up", "delivered"])

    return jsonify({
        "store": store.to_dict(),
        "orders_today": len(today_orders),
        "revenue_today": revenue,
        "pending_orders": pending_count,
    }), 200


@merchant_bp.route("/store/toggle", methods=["PUT"])
@jwt_required()
def toggle_store():
    """Toggle store open/closed status."""
    merchant_id, store, err = _require_merchant()
    if err:
        return err
    if not store:
        return jsonify({"error": "No store found"}), 404

    data = request.get_json()
    if data and "is_open" in data:
        store.is_open = bool(data["is_open"])
    else:
        store.is_open = not store.is_open

    db.session.commit()
    return jsonify({"message": f"Store is now {'open' if store.is_open else 'closed'}", "store": store.to_dict()}), 200


@merchant_bp.route("/store", methods=["PUT"])
@jwt_required()
def update_store():
    """Update store details (name, category, image_url)."""
    merchant_id, store, err = _require_merchant()
    if err:
        return err
    if not store:
        return jsonify({"error": "No store found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "name" in data and data["name"].strip():
        store.name = data["name"].strip()
    if "category" in data and data["category"].strip():
        store.category = data["category"].strip()
    if "image_url" in data:
        store.image_url = data["image_url"].strip()

    db.session.commit()
    return jsonify({"message": "Store updated", "store": store.to_dict()}), 200
