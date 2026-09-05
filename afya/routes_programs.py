from flask import Blueprint, render_template, redirect, url_for, abort, request
from flask_login import login_required, current_user

from .extensions import db
from .models import CareProgram, ProgramStep, UserStepProgress

programs_bp = Blueprint("programs", __name__)


@programs_bp.route("/")
def index():
    programs = CareProgram.query.all()
    return render_template("page.html", page="programs", programs=programs)


@programs_bp.route("/<slug>")
def detail(slug):
    program = CareProgram.query.filter_by(slug=slug).first()
    if program is None:
        abort(404)

    completed_step_ids = set()
    if current_user.is_authenticated:
        completed_step_ids = {
            p.step_id for p in UserStepProgress.query.filter_by(user_id=current_user.id).all()
        }

    return render_template(
        "page.html", page="program_detail", program=program, completed_step_ids=completed_step_ids
    )


@programs_bp.route("/<slug>/step/<int:step_id>/toggle", methods=["POST"])
@login_required
def toggle_step(slug, step_id):
    step = ProgramStep.query.get(step_id)
    if step is None:
        abort(404)

    existing = UserStepProgress.query.filter_by(user_id=current_user.id, step_id=step_id).first()
    if existing:
        db.session.delete(existing)
    else:
        db.session.add(UserStepProgress(user_id=current_user.id, step_id=step_id))
    db.session.commit()

    return redirect(url_for("programs.detail", slug=slug))


@programs_bp.route("/mine")
@login_required
def my_path():
    completions = UserStepProgress.query.filter_by(user_id=current_user.id).all()
    completed_step_ids = {p.step_id for p in completions}

    # Group progress by program: only show programs the user has actually
    # touched (at least one step completed), each with a simple X / N tally.
    touched_program_ids = {c.step.program_id for c in completions if c.step}
    my_programs = []
    for program in CareProgram.query.filter(CareProgram.id.in_(touched_program_ids)).all():
        total = len(program.steps)
        done = sum(1 for s in program.steps if s.id in completed_step_ids)
        my_programs.append({"program": program, "done": done, "total": total})

    return render_template(
        "page.html", page="my_path", my_programs=my_programs, completed_step_ids=completed_step_ids
    )
