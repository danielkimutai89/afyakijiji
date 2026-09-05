from datetime import datetime

from .extensions import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default="family")  # family, chv, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    step_completions = db.relationship(
        "UserStepProgress", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )


class ContentPage(db.Model):
    """A public 'house' in the village, or a CHV-only resource.

    audience='public' pages make up the houses directory anyone can browse.
    audience='chv' pages only appear in the CHV portal, gated to logged-in
    users with role='chv' (or 'admin').
    """

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    title_sw = db.Column(db.String(200))  # Kiswahili name, shown as a subtitle on cards
    body = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80))  # infectious, chronic, family, practical, training
    language = db.Column(db.String(10), default="en")  # en, sw
    audience = db.Column(db.String(10), default="public")  # public, chv
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class Facility(db.Model):
    """A health facility, tiered per Kenya's Level 1-6 system (MOH).

    level is stored as the descriptive tier label (e.g. "Level 5 - County
    Referral Hospital") rather than a bare number, so it's readable in
    listings without a lookup table.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    county = db.Column(db.String(100))
    ward = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    level = db.Column(db.String(80))  # e.g. "Level 2 - Dispensary"
    is_national_referral = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(30))


class CareProgram(db.Model):
    """A guided, step-by-step self-care journey (Terveyskylä-style)."""

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    house_slug = db.Column(db.String(120))  # links back to a ContentPage.slug, informally

    steps = db.relationship(
        "ProgramStep", backref="program", order_by="ProgramStep.order",
        cascade="all, delete-orphan"
    )


class ProgramStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey("care_program.id"), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    __tablename__ = "program_step"


# SQLAlchemy needs an explicit table name on CareProgram too, since the
# default (derived from the class name) is what ProgramStep's ForeignKey
# above points at ("care_program").
CareProgram.__tablename__ = "care_program"


class UserStepProgress(db.Model):
    """Marks one program step as completed by one user -- the data behind
    the 'My Path' personal portal. A step's absence here means not done yet;
    there's no separate 'enrollment' record, a program is 'started' the
    moment its first step is checked off.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    step_id = db.Column(db.Integer, db.ForeignKey("program_step.id"), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    step = db.relationship("ProgramStep")

    __table_args__ = (db.UniqueConstraint("user_id", "step_id", name="uq_user_step"),)
