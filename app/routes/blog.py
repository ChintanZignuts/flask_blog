from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.blog import BlogPost
from app.models.user import User
from app.models.category import Category
from datetime import datetime, timezone
from slugify import slugify


blog_bp = Blueprint("blog", __name__)

# 📝 Create a new blog post
@blog_bp.route("/create", methods=["POST"])
@jwt_required()
def create_blog():
    data = request.get_json()
    user_id = get_jwt_identity()

    if not data.get("title") or not data.get("content"):
        return jsonify({"error": "Title and content are required"}), 400

    # Use provided slug if available; otherwise, generate one
    slug = data.get("slug") or slugify(data["title"], lowercase=True, separator="-")

    # Check if the slug already exists to prevent duplicates
    if BlogPost.query.filter_by(slug=slug).first():
        return jsonify({"error": "Slug already exists, please choose a different one"}), 409

    blog_post = BlogPost(
        title=data["title"],
        slug=slug,
        content=data["content"],
        author_id=user_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        published=data.get("published", False),
        category_id=data.get("category_id"),
        tags=",".join(data.get("tags", [])),
        image_url=data.get("image_url")
    )

    db.session.add(blog_post)
    db.session.commit()

    return jsonify({"message": "Blog post created successfully", "blog": {"id": blog_post.id, "title": blog_post.title, "slug": blog_post.slug}}), 201

# 📌 Get all published blog posts
@blog_bp.route("/all", methods=["GET"])
def get_all_blogs():
    blogs = BlogPost.query.filter_by(published=True).all()
    blog_list = [
        {
            "id": blog.id,
            "title": blog.title,
            "slug": blog.slug,
            "content": blog.content,
            "author": User.query.get(blog.author_id).username,
            "created_at": blog.created_at,
            "views": blog.views,
        }
        for blog in blogs
    ]
    return jsonify(blog_list)

# 🔍 Get a single blog post by ID
@blog_bp.route("/<int:blog_id>", methods=["GET"])
def get_blog(blog_id):
    blog = BlogPost.query.get(blog_id)
    if not blog or not blog.published:
        return jsonify({"error": "Blog not found"}), 404

    blog.views += 1
    db.session.commit()

    return jsonify({
        "id": blog.id,
        "title": blog.title,
        "slug": blog.slug,
        "content": blog.content,
        "author": User.query.get(blog.author_id).username,
        "created_at": blog.created_at,
        "views": blog.views,
    })

@blog_bp.route("/update/<int:blog_id>", methods=["PUT"])
@jwt_required()
def update_blog(blog_id):
    blog = BlogPost.query.get(blog_id)
    if not blog:
        return jsonify({"error": "Blog not found"}), 404

    user_id = get_jwt_identity()
    print("User ID:",  int(user_id))

    if blog.author_id != int(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    blog.title = data.get("title", blog.title)
    blog.content = data.get("content", blog.content)
    blog.published = data.get("published", blog.published)
    blog.category_id = data.get("category_id", blog.category_id)
    blog.tags = ",".join(data.get("tags", blog.tags.split(","))) 
    blog.image_url = data.get("image_url", blog.image_url)
    blog.updated_at = datetime.now(timezone.utc)

    db.session.commit()
    return jsonify({"message": "Blog post updated successfully"})

# 🗑️ Delete a blog post (only author or admin can delete)
@blog_bp.route("/delete/<int:blog_id>", methods=["DELETE"])
@jwt_required()
def delete_blog(blog_id):
    blog = BlogPost.query.get(blog_id)
    if not blog:
        return jsonify({"error": "Blog not found"}), 404

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if blog.author_id != user_id and not user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(blog)
    db.session.commit()
    return jsonify({"message": "Blog post deleted successfully"})