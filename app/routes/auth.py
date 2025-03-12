from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User
from flask_jwt_extended import create_access_token
import jwt
import datetime
from app.utils import send_email
from app.config import Config

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 409

    new_user = User(username=data["username"], email=data["email"])
    new_user.set_password(data["password"])
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()

    if user and user.check_password(data.get("password")):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": access_token})

    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """ Generate a password reset token and send it via email (Mailtrap) """
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)

    reset_token = jwt.encode(
        {"user_id": user.id, "exp": exp_time.timestamp()},
        Config.SECRET_KEY,
        algorithm="HS256"
    )

    reset_link = f"{request.host_url}reset-password?token={reset_token}"
    email_body = f"Click the link to reset your password: {reset_link}"

    send_email(user.email, "Password Reset Request", email_body)

    return jsonify({"message": "Password reset link sent to your email"}), 200

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """ Reset password using a valid token """
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("new_password")

    if not token or not new_password:
        return jsonify({"error": "Token and new password are required"}), 400

    try:
        decoded_token = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get("user_id")

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update user password
        user.set_password(new_password)
        db.session.commit()

        return jsonify({"message": "Password reset successfully"}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Reset token has expired"}), 400
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid reset token"}), 400