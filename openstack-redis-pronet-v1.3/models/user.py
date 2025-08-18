# models/user.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    profile_pic = db.Column(db.String(256), nullable=True)
    password = db.Column(db.String(256), nullable=True)
    confirmed = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    credits = db.Column(db.Integer, default=100)

    openstack_user_id = db.Column(db.String(128), nullable=True)
    openstack_project_id = db.Column(db.String(128), nullable=True)
    openstack_network_id = db.Column(db.String(128), nullable=True)
    openstack_subnet_id = db.Column(db.String(128), nullable=True)
    openstack_router_id = db.Column(db.String(128), nullable=True)

    vm_quota = db.Column(db.Integer, default=5)
    ram_quota_gb = db.Column(db.Integer, default=16)
    disk_quota_gb = db.Column(db.Integer, default=100)

    def __repr__(self):
        return f"<User {self.email}>"

class OAuth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)
    provider_user_id = db.Column(db.String(256), unique=True, nullable=False)
    token = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("oauth", lazy=True))