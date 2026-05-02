from flask import Flask, render_template, request, redirect, url_for, flash
from extensions import db, bcrypt, login_manager
from models import User
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "main_routes.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

from routes import main_routes
app.register_blueprint(main_routes)

if __name__ == "__main__":
    app.run(debug=True, port=5000)