from flask import Blueprint, render_template, redirect, url_for, request
from extensions import db, bcrypt
from models import User

main_routes = Blueprint("main_routes", __name__)

@main_routes.route("/")
def home():
    return redirect(url_for("main_routes.login"))


@main_routes.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return redirect(url_for("main_routes.home"))

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


@main_routes.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing = User.query.filter_by(email=email).first()

        if existing:
            return render_template("signup.html", error="Email already exists")

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User(
            name=name,
            email=email,
            password=hashed_password,
            role="member"
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("main_routes.login"))

    return render_template("signup.html")