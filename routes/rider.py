from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, Order, User

rider_bp = Blueprint("rider", __name__, url_prefix="/rider")


def _require_rider():
    """Helper to verify the current user is a rider."""
    claims = get_jwt()
    if claims.get("role") != "rider":
        return None, (jsonify({"error": "Rider access required"}), 403)
    return int(get_jwt_identity()), None


@rider_bp.route("/orders", methods=["GET"])
@jwt_required()
def available_orders():
    """Get orders that are pending (available for pickup)."""
    rider_id, err = _require_rider()
    if err:
        return err

    orders = Order.query.filter(
        Order.status.in_(["pending", "accepted"]),
        (Order.rider_id == None) | (Order.rider_id == rider_id)
    ).order_by(Order.created_at.desc()).all()

    return jsonify([o.to_dict() for o in orders]), 200


@rider_bp.route("/orders/<int:order_id>/accept", methods=["PUT"])
@jwt_required()
def accept_order(order_id):
    """Rider accepts a delivery."""
    rider_id, err = _require_rider()
    if err:
        return err

    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.status not in ["pending", "accepted"]:
        return jsonify({"error": "Order is not available for pickup"}), 400

    order.rider_id = rider_id
    order.status = "accepted"
    db.session.commit()

    return jsonify({"message": "Order accepted", "order": order.to_dict()}), 200


@rider_bp.route("/orders/<int:order_id>/status", methods=["PUT"])
@jwt_required()
def update_order_status(order_id):
    """Update order status to picked_up or delivered."""
    rider_id, err = _require_rider()
    if err:
        return err

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    new_status = data.get("status", "").strip()
    if new_status not in ["picked_up", "delivered"]:
        return jsonify({"error": "Status must be 'picked_up' or 'delivered'"}), 400

    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.rider_id != rider_id:
        return jsonify({"error": "This order is not assigned to you"}), 403

    order.status = new_status
    db.session.commit()

    return jsonify({"message": f"Order marked as {new_status}", "order": order.to_dict()}), 200


@rider_bp.route("/earnings", methods=["GET"])
@jwt_required()
def earnings():
    """Get rider earnings history."""
    rider_id, err = _require_rider()
    if err:
        return err

    # All delivered orders for this rider
    delivered = Order.query.filter_by(rider_id=rider_id, status="delivered").order_by(Order.created_at.desc()).all()

    # Earnings per delivery = flat ₹30 delivery fee
    delivery_fee = 30.0

    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())

    today_deliveries = [o for o in delivered if o.created_at and o.created_at >= today_start]
    week_deliveries = [o for o in delivered if o.created_at and o.created_at >= week_start]

    return jsonify({
        "today_total": len(today_deliveries) * delivery_fee,
        "today_count": len(today_deliveries),
        "week_total": len(week_deliveries) * delivery_fee,
        "week_count": len(week_deliveries),
        "all_time_total": len(delivered) * delivery_fee,
        "all_time_count": len(delivered),
        "deliveries": [{
            "order_id": o.id,
            "customer_name": o.customer.name if o.customer else "Unknown",
            "address": o.address,
            "amount": delivery_fee,
            "date": o.created_at.isoformat() if o.created_at else None,
        } for o in delivered],
    }), 200

@rider_bp.route("/summary", methods=["GET"])
@jwt_required()
def summary():
    """Get rider summary including overall rating."""
    rider_id, err = _require_rider()
    if err:
        return err

    from models import Review
    delivered_orders = Order.query.filter_by(rider_id=rider_id, status="delivered").all()
    
    total_rating = 0
    rating_count = 0
    
    for order in delivered_orders:
        for review in order.reviews:
            if review.rating:
                total_rating += review.rating
                rating_count += 1
                
    average_rating = total_rating / rating_count if rating_count > 0 else 5.0
    
    return jsonify({
        "average_rating": round(average_rating, 1),
        "review_count": rating_count,
        "total_deliveries": len(delivered_orders)
    }), 200
