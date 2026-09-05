from flask import Blueprint, render_template, request

from .models import Facility

facilities_bp = Blueprint("facilities", __name__)


@facilities_bp.route("/")
def list_facilities():
    county = request.args.get("county") or ""
    query = Facility.query
    if county:
        query = query.filter_by(county=county)
    facilities = query.order_by(Facility.county, Facility.name).all()

    counties = sorted({f.county for f in Facility.query.all() if f.county})

    return render_template(
        "page.html",
        page="facilities",
        facilities=facilities,
        counties=counties,
        selected_county=county,
    )
