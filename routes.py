from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, bcrypt
from models import User, Project, ProjectMember, Task
from datetime import date, datetime

main_routes = Blueprint("main_routes", __name__)


# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────

def get_member_role(project, user):
    """Return the role of `user` in `project`, or None if not a member."""
    m = ProjectMember.query.filter_by(project_id=project.id, user_id=user.id).first()
    return m.role if m else None


def require_project_admin(project):
    role = get_member_role(project, current_user)
    if role != "admin":
        abort(403)


# ─────────────────────────────────────────
# Auth
# ─────────────────────────────────────────

@main_routes.route("/")
def home():
    return redirect(url_for("main_routes.login"))


@main_routes.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main_routes.dashboard"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("main_routes.dashboard"))
        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


@main_routes.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main_routes.dashboard"))

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            return render_template("signup.html", error="Email already registered")

        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(name=name, email=email, password=hashed, role="member")
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("main_routes.login"))

    return render_template("signup.html")


@main_routes.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("main_routes.login"))


# ─────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────

@main_routes.route("/dashboard")
@login_required
def dashboard():
    today = date.today()

    # All projects this user is in
    memberships = ProjectMember.query.filter_by(user_id=current_user.id).all()
    project_ids = [m.project_id for m in memberships]

    all_tasks = Task.query.filter(Task.project_id.in_(project_ids)).all() if project_ids else []
    my_tasks   = [t for t in all_tasks if t.assigned_to_id == current_user.id]

    stats = {
        "total":       len(my_tasks),
        "todo":        sum(1 for t in my_tasks if t.status == "todo"),
        "in_progress": sum(1 for t in my_tasks if t.status == "in_progress"),
        "done":        sum(1 for t in my_tasks if t.status == "done"),
        "overdue":     sum(1 for t in my_tasks if t.due_date and t.due_date < today and t.status != "done"),
    }

    recent_tasks = sorted(my_tasks, key=lambda t: t.created_at, reverse=True)[:8]
    projects     = Project.query.filter(Project.id.in_(project_ids)).order_by(Project.created_at.desc()).all() if project_ids else []

    return render_template("dashboard.html",
                           stats=stats,
                           recent_tasks=recent_tasks,
                           projects=projects,
                           today=today,
                           page="dashboard")


# ─────────────────────────────────────────
# Projects
# ─────────────────────────────────────────

@main_routes.route("/projects")
@login_required
def projects():
    memberships = ProjectMember.query.filter_by(user_id=current_user.id).all()
    project_ids = [m.project_id for m in memberships]
    user_projects = Project.query.filter(Project.id.in_(project_ids)).order_by(Project.created_at.desc()).all() if project_ids else []
    return render_template("projects.html", projects=user_projects, page="projects")


@main_routes.route("/projects/create", methods=["POST"])
@login_required
def create_project():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    if not name:
        return redirect(url_for("main_routes.projects"))

    project = Project(name=name, description=description, created_by_id=current_user.id)
    db.session.add(project)
    db.session.flush()  # get project.id before commit

    # Creator is automatically admin
    member = ProjectMember(project_id=project.id, user_id=current_user.id, role="admin")
    db.session.add(member)
    db.session.commit()
    return redirect(url_for("main_routes.project_detail", project_id=project.id))


@main_routes.route("/projects/<int:project_id>")
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    my_role = get_member_role(project, current_user)
    if not my_role:
        abort(403)

    members = ProjectMember.query.filter_by(project_id=project.id).all()
    tasks   = Task.query.filter_by(project_id=project.id).order_by(Task.created_at.desc()).all()
    all_users = User.query.all()
    today = date.today()

    return render_template("project_detail.html",
                           project=project,
                           my_role=my_role,
                           members=members,
                           tasks=tasks,
                           all_users=all_users,
                           today=today,
                           page="projects")


@main_routes.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    require_project_admin(project)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for("main_routes.projects"))


# ─────────────────────────────────────────
# Members
# ─────────────────────────────────────────

@main_routes.route("/projects/<int:project_id>/members/add", methods=["POST"])
@login_required
def add_member(project_id):
    project = Project.query.get_or_404(project_id)
    require_project_admin(project)

    email = request.form.get("email", "").strip()
    role  = request.form.get("role", "member")
    user  = User.query.filter_by(email=email).first()

    if not user:
        return redirect(url_for("main_routes.project_detail", project_id=project_id))

    existing = ProjectMember.query.filter_by(project_id=project_id, user_id=user.id).first()
    if not existing:
        db.session.add(ProjectMember(project_id=project_id, user_id=user.id, role=role))
        db.session.commit()

    return redirect(url_for("main_routes.project_detail", project_id=project_id))


@main_routes.route("/projects/<int:project_id>/members/<int:user_id>/remove", methods=["POST"])
@login_required
def remove_member(project_id, user_id):
    project = Project.query.get_or_404(project_id)
    require_project_admin(project)
    m = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first_or_404()
    db.session.delete(m)
    db.session.commit()
    return redirect(url_for("main_routes.project_detail", project_id=project_id))


# ─────────────────────────────────────────
# Tasks
# ─────────────────────────────────────────

@main_routes.route("/projects/<int:project_id>/tasks/create", methods=["POST"])
@login_required
def create_task(project_id):
    project = Project.query.get_or_404(project_id)
    my_role = get_member_role(project, current_user)
    if not my_role:
        abort(403)

    title       = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    priority    = request.form.get("priority", "medium")
    due_date_str= request.form.get("due_date", "")
    assigned_id = request.form.get("assigned_to_id", type=int)

    if not title:
        return redirect(url_for("main_routes.project_detail", project_id=project_id))

    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date() if due_date_str else None

    task = Task(
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
        status="todo",
        project_id=project_id,
        assigned_to_id=assigned_id,
        created_by_id=current_user.id,
    )
    db.session.add(task)
    db.session.commit()
    return redirect(url_for("main_routes.project_detail", project_id=project_id))


@main_routes.route("/tasks/<int:task_id>/status", methods=["POST"])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    my_role = get_member_role(task.project, current_user)
    if not my_role:
        abort(403)

    # Members can only update tasks assigned to them
    if my_role == "member" and task.assigned_to_id != current_user.id:
        abort(403)

    new_status = request.form.get("status")
    if new_status in ("todo", "in_progress", "done"):
        task.status = new_status
        db.session.commit()

    return redirect(url_for("main_routes.project_detail", project_id=task.project_id))


@main_routes.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.project
    require_project_admin(project)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("main_routes.project_detail", project_id=project.id))