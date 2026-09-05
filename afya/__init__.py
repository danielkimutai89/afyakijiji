import os

from flask import Flask

from .extensions import db, login_manager
from .routes_main import main_bp
from .routes_symptoms import symptoms_bp
from .routes_facilities import facilities_bp
from .routes_auth import auth_bp
from .routes_programs import programs_bp
from .routes_chv import chv_bp
from config import Config

# templates/ and static/ live at the project root (sibling to afya/), not
# inside the afya package -- Flask(__name__) alone would look for them
# inside afya/ instead, so point it at the project root explicitly.
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(_PROJECT_ROOT, "templates"),
        static_folder=os.path.join(_PROJECT_ROOT, "static"),
    )
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    # Flask-Login needs this to reload a user from the session on each
    # request. Without it, login_user() works but the session can't be
    # turned back into a User object on the next request.
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(main_bp)
    app.register_blueprint(symptoms_bp, url_prefix="/symptoms")
    app.register_blueprint(facilities_bp, url_prefix="/facilities")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(programs_bp, url_prefix="/programs")
    app.register_blueprint(chv_bp, url_prefix="/chv")

    # Display metadata (neighbourhood groupings, category icons, verified
    # national helpline numbers, About copy) lives in content_meta.py rather
    # than as model fields, so it can change without a migration. Registered
    # as Jinja globals so templates/page.html can use it directly.
    from . import content_meta

    app.jinja_env.globals["CATEGORY_ICONS"] = content_meta.CATEGORY_ICONS
    app.jinja_env.globals["DEFAULT_ICON"] = content_meta.DEFAULT_ICON
    app.jinja_env.globals["NEIGHBOURHOODS"] = content_meta.NEIGHBOURHOODS
    app.jinja_env.globals["CATEGORY_COLORS"] = content_meta.CATEGORY_COLORS
    app.jinja_env.globals["DEFAULT_COLOR"] = content_meta.DEFAULT_COLOR

    with app.app_context():
        db.create_all()

    return app
