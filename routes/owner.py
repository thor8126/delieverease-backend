from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import db, User, Store, MenuItem, Order, Review


owner_bp = Blueprint("owner", __name__, url_prefix="/owner")


def _require_owner():
    """Helper to verify the current user has the 'owner' role."""
    claims = get_jwt()
    if claims.get("role") != "owner":
        return jsonify({"error": "Owner access required"}), 403
    return None


# ── Dashboard aggregate stats ────────────────────────────────────────────────

@owner_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    """Platform-wide aggregate statistics."""
    err = _require_owner()
    if err:
        return err

    total_users = User.query.count()
    total_customers = User.query.filter_by(role="customer").count()
    total_riders = User.query.filter_by(role="rider").count()
    total_merchants = User.query.filter_by(role="merchant").count()
    total_stores = Store.query.count()
    total_orders = Order.query.count()

    all_orders = Order.query.all()
    total_revenue = sum(
        o.total for o in all_orders if o.status in ["accepted", "picked_up", "delivered"]
    )

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    today_orders = Order.query.filter(Order.created_at >= today_start).all()
    today_revenue = sum(
        o.total for o in today_orders if o.status in ["accepted", "picked_up", "delivered"]
    )

    pending_orders = Order.query.filter_by(status="pending").count()
    delivered_orders = Order.query.filter_by(status="delivered").count()

    total_reviews = Review.query.count()
    all_reviews = Review.query.all()
    avg_rating = (
        round(sum(r.rating for r in all_reviews) / total_reviews, 1)
        if total_reviews > 0
        else 0.0
    )

    return jsonify({
        "total_users": total_users,
        "total_customers": total_customers,
        "total_riders": total_riders,
        "total_merchants": total_merchants,
        "total_stores": total_stores,
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "today_orders": len(today_orders),
        "today_revenue": round(today_revenue, 2),
        "pending_orders": pending_orders,
        "delivered_orders": delivered_orders,
        "total_reviews": total_reviews,
        "avg_rating": avg_rating,
    }), 200


# ── All users ─────────────────────────────────────────────────────────────────

@owner_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    """List all users. Optional filter: ?role=customer|rider|merchant"""
    err = _require_owner()
    if err:
        return err

    role_filter = request.args.get("role", "").strip().lower()

    query = User.query
    if role_filter and role_filter in ["customer", "rider", "merchant", "owner"]:
        query = query.filter_by(role=role_filter)

    users = query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200


# ── All stores ────────────────────────────────────────────────────────────────

@owner_bp.route("/stores", methods=["GET"])
@jwt_required()
def list_stores():
    """List all stores with their merchant info."""
    err = _require_owner()
    if err:
        return err

    stores = Store.query.all()
    result = []
    for s in stores:
        store_data = s.to_dict()
        merchant = User.query.get(s.merchant_id)
        store_data["merchant_name"] = merchant.name if merchant else "Unknown"
        store_data["merchant_email"] = merchant.email if merchant else ""
        # Item count and order count for extra insight
        store_data["item_count"] = MenuItem.query.filter_by(store_id=s.id).count()
        store_data["order_count"] = Order.query.filter_by(store_id=s.id).count()
        revenue = sum(
            o.total
            for o in Order.query.filter_by(store_id=s.id).all()
            if o.status in ["accepted", "picked_up", "delivered"]
        )
        store_data["revenue"] = round(revenue, 2)
        result.append(store_data)

    return jsonify(result), 200


# ── All orders ────────────────────────────────────────────────────────────────

@owner_bp.route("/orders", methods=["GET"])
@jwt_required()
def list_orders():
    """List all orders. Optional filter: ?status=pending|accepted|picked_up|delivered"""
    err = _require_owner()
    if err:
        return err

    status_filter = request.args.get("status", "").strip().lower()

    query = Order.query
    if status_filter and status_filter in ["pending", "accepted", "picked_up", "delivered", "rejected"]:
        query = query.filter_by(status=status_filter)

    orders = query.order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders]), 200
