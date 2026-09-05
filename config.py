import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration for Afya Kijiji.

    SECRET_KEY should always be overridden via the AFYA_SECRET_KEY
    environment variable in any real deployment -- the fallback here is
    only for local development.
    """

    SECRET_KEY = os.environ.get("AFYA_SECRET_KEY", "dev-only-change-me")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "AFYA_DATABASE_URI", f"sqlite:///{os.path.join(BASE_DIR, 'afyakijiji.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # If True, seed_data() in afya/__init__.py will (re)populate sample
    # facility records the first time the app runs against an empty table.
    SEED_SAMPLE_FACILITIES = True
