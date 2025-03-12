from datetime import datetime, timezone
from app.extensions import db
from slugify import slugify

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True) 
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    published = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(255), nullable=True)
    views = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500), nullable=True)

    def save(self):
        """Generate slug and save the blog post."""
        if not self.slug:
            self.slug = slugify(self.title)
        db.session.add(self)
        db.session.commit()