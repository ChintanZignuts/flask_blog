from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.category import Category
from app.models.user import User

category_bp = Blueprint("category", __name__)

@category_bp.route("/create", methods=["POST"])
@jwt_required()
def create_category():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if not data.get("name"):
        return jsonify({"error": "Category name is required"}), 400

    category = Category(name=data["name"], description=data.get("description"))
    db.session.add(category)
    db.session.commit()

    return jsonify({"message": "Category created successfully"}), 201

@category_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_category(id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    category = Category.query.get(id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    data = request.get_json()
    category.name = data.get("name", category.name)
    category.description = data.get("description", category.description)

    db.session.commit()
    return jsonify({"message": "Category updated successfully"}), 200

@category_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_category(id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    category = Category.query.get(id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted successfully"}), 200

@category_bp.route("/", methods=["GET"])
def get_categories():
    categories = Category.query.all()
    return jsonify([{"id": cat.id, "name": cat.name, "description": cat.description} for cat in categories])