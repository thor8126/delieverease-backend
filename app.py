import os
import eventlet
eventlet.monkey_patch()

from datetime import timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

from models import db
from seed import seed_database
from socket_events import register_socket_events
from routes.auth import auth_bp
from routes.customer import customer_bp
from routes.rider import rider_bp
from routes.merchant import merchant_bp
from routes.owner import owner_bp

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = Flask(__name__)

# Configuration
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "deliverease-secret-key-change-in-production")

db_url = os.environ.get("DATABASE_URL", "sqlite:///deliverease.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url

from sqlalchemy.pool import NullPool
if db_url.startswith("sqlite"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {"check_same_thread": False},
        "poolclass": NullPool
    }

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "jwt-secret-change-in-production")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

# Extensions
CORS(app, resources={r"/*": {"origins": "*"}})
db.init_app(app)
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(rider_bp)
app.register_blueprint(merchant_bp)
app.register_blueprint(owner_bp)

# Register socket events
register_socket_events(socketio)


# Global Error Handling
from werkzeug.exceptions import HTTPException
import traceback

@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e
    
    # Send traceback to Render logs
    print("Unhandled Exception:", traceback.format_exc())
    
    # Return JSON so the frontend receives a proper error string instead of breaking CORS
    return jsonify({"error": "An internal server error occurred. Check the backend logs."}), 500

# Profile endpoint (all roles)
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User
from werkzeug.security import generate_password_hash


@app.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200


@app.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    from flask import request
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if data:
        if "name" in data:
            user.name = data["name"].strip()
        if "address" in data:
            user.address = data["address"].strip()
        if "password" in data and data["password"]:
            if len(data["password"]) < 6:
                return jsonify({"error": "Password must be at least 6 characters"}), 400
            user.password_hash = generate_password_hash(data["password"])

    db.session.commit()
    return jsonify({"message": "Profile updated", "user": user.to_dict()}), 200


# Health check
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "app": "DeliverEase API"}), 200


# ---------------------------------------------------------------------------
# Keep-alive: self-ping every 5 min to prevent Render free-tier spin-down
# ---------------------------------------------------------------------------
import threading
import urllib.request

def keep_alive():
    """Ping our own /health endpoint every 5 minutes."""
    url = os.environ.get("RENDER_EXTERNAL_URL", "")
    if not url:
        print("⏸️  RENDER_EXTERNAL_URL not set — keep-alive disabled (local dev).")
        return

    health_url = f"{url}/health"
    print(f"💓 Keep-alive started — pinging {health_url} every 5 min")

    def ping():
        while True:
            try:
                urllib.request.urlopen(health_url, timeout=10)
                print("💓 Keep-alive ping OK")
            except Exception as e:
                print(f"💓 Keep-alive ping failed: {e}")
            eventlet.sleep(300)  # 5 minutes

    t = threading.Thread(target=ping, daemon=True)
    t.start()


# ---------------------------------------------------------------------------
# Initialize DB and seed
# ---------------------------------------------------------------------------
with app.app_context():
    db.create_all()
    seed_database()

    # Ensure owner account exists (safe for existing production DBs)
    def ensure_owner():
        owner = User.query.filter_by(email="owner@deliverease.com").first()
        if not owner:
            owner = User(
                name="Platform Owner",
                email="owner@deliverease.com",
                password_hash=generate_password_hash("password123"),
                role="owner",
                address="DeliverEase HQ",
            )
            db.session.add(owner)
            db.session.commit()
            print("✅ Owner account created: owner@deliverease.com")
        else:
            print("✅ Owner account already exists.")

    ensure_owner()

# Start keep-alive after DB is ready
keep_alive()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    print(f"\n🚀 DeliverEase API running on http://localhost:{port}\n")
    socketio.run(app, host="0.0.0.0", port=port, debug=debug)

