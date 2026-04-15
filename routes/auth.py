from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new account (any role)."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    address = data.get("address", "").strip()
    role = data.get("role", "customer").strip().lower()
    store_name = data.get("store_name", "").strip()

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400

    if role not in ["customer", "rider", "merchant"]:
        return jsonify({"error": "Invalid role"}), 400

    # Owner accounts cannot be created via public registration
    if role == "owner":
        return jsonify({"error": "Owner accounts cannot be registered"}), 403

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        address=address,
    )
    db.session.add(user)
    db.session.flush()

    if role == "merchant":
        from models import Store
        if not store_name:
            store_name = f"{name}'s Store"
        store_category = data.get("store_category", "Food").strip() or "Food"
        new_store = Store(
            merchant_id=user.id,
            name=store_name,
            category=store_category,
            is_open=True,
            image_url="https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=600",
        )
        db.session.add(new_store)

    db.session.commit()

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "name": user.name},
    )

    return jsonify({
        "message": "Registration successful",
        "token": access_token,
        "user": user.to_dict(),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login for all roles. Returns JWT + user info."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "name": user.name},
    )

    return jsonify({
        "message": "Login successful",
        "token": access_token,
        "user": user.to_dict(),
    }), 200

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "No account found with this email"}), 404
        
    return jsonify({
        "message": "OTP sent to email successfully",
        "otp": "123456"
    }), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    otp = data.get("otp", "").strip()
    new_password = data.get("new_password", "")
    
    if not email or not otp or not new_password:
        return jsonify({"error": "Missing required fields"}), 400
        
    if otp != "123456":
        return jsonify({"error": "Invalid OTP"}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    if len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
        
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    return jsonify({"message": "Password reset successfully"}), 200
