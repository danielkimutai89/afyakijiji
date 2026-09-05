from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from .extensions import db
from .models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("main.index"))
        error = "Incorrect email or password."
    return render_template("page.html", page="login", error=error)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = "chv" if request.form.get("is_chv") else "family"

        if not email or not password:
            error = "Email and password are required."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif User.query.filter_by(email=email).first():
            error = "An account with that email already exists."

        if not error:
            user = User(email=email, password_hash=generate_password_hash(password), role=role)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("main.index"))

    return render_template("page.html", page="register", error=error)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))
