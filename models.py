from extensions import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="member")  # global role: admin / member
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships via backref from ProjectMember and Task


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    creator = db.relationship("User", foreign_keys=[created_by_id], backref="created_projects")
    members = db.relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    tasks = db.relationship("Task", back_populates="project", cascade="all, delete-orphan")


class ProjectMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="member")  # admin / member

    project = db.relationship("Project", back_populates="members")
    user = db.relationship("User", backref="project_memberships")

    __table_args__ = (db.UniqueConstraint("project_id", "user_id"),)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="todo")        # todo / in_progress / done
    priority = db.Column(db.String(20), nullable=False, default="medium")    # low / medium / high
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    project = db.relationship("Project", back_populates="tasks")
    assigned_to = db.relationship("User", foreign_keys=[assigned_to_id], backref="assigned_tasks")
    created_by = db.relationship("User", foreign_keys=[created_by_id], backref="created_tasks")
