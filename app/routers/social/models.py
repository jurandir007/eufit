# EUFit/app/routers/social/models.py
from app.extensions import db
from datetime import datetime


class SocialUser(db.Model):
    __bind_key__ = "social"
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    profile_pic = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    posts = db.relationship("SocialPost", backref="author", lazy=True, cascade="all, delete-orphan")
    comments = db.relationship("SocialComment", backref="author", lazy=True, cascade="all, delete-orphan")
    likes = db.relationship("SocialLike", backref="user", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SocialUser {self.username}>"


class SocialPost(db.Model):
    __bind_key__ = "social"
    __tablename__ = "posts"

    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    comments = db.relationship("SocialComment", backref="post", lazy=True, cascade="all, delete-orphan")
    likes = db.relationship("SocialLike", backref="post", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SocialPost {self.post_id} by user {self.user_id}>"


class SocialComment(db.Model):
    __bind_key__ = "social"
    __tablename__ = "comments"

    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<SocialComment {self.comment_id}>"


class SocialLike(db.Model):
    __bind_key__ = "social"
    __tablename__ = "likes"
    __table_args__ = (
        db.UniqueConstraint("user_id", "post_id", name="uq_likes_user_post"),
    )

    like_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class SocialFollow(db.Model):
    __bind_key__ = "social"
    __tablename__ = "follows"
    __table_args__ = (
        db.UniqueConstraint("follower_id", "following_id", name="uq_follows_pair"),
        db.CheckConstraint("follower_id <> following_id", name="chk_no_self_follow"),
    )

    follow_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    follower_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
