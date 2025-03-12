from flask import Flask
from app.config import Config
from app.extensions import db, jwt, bcrypt,migrate, mail
from app.routes.auth import auth_bp
from app.routes import blog_bp,category_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(blog_bp, url_prefix="/api/blogs")
    app.register_blueprint(category_bp,url_prefix="/api/categories")
    return app