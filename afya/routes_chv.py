from functools import wraps

from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

from .models import ContentPage, Facility

chv_bp = Blueprint("chv", __name__)


def chv_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ("chv", "admin"):
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@chv_bp.route("/")
@login_required
@chv_required
def home():
    resources = ContentPage.query.filter_by(audience="chv").all()
    referral_facilities = Facility.query.filter_by(is_national_referral=True).all()
    return render_template(
        "page.html", page="chv_home", resources=resources, referral_facilities=referral_facilities
    )


@chv_bp.route("/resource/<slug>")
@login_required
@chv_required
def resource_detail(slug):
    resource = ContentPage.query.filter_by(slug=slug, audience="chv").first()
    if resource is None:
        abort(404)
    return render_template("page.html", page="chv_resource", resource=resource)
