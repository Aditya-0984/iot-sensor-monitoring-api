from flask import Flask
from .extensions import db, migrate
from config import Config


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Import model supaya SQLAlchemy mengenali seluruh tabel untuk create_all/migration.
    from . import models  # noqa: F401
    from .controllers.health import health_bp
    from .controllers.sites import sites_bp
    from .controllers.devices import devices_bp
    from .controllers.sensors import sensors_bp
    from .controllers.readings import readings_bp
    from .controllers.alerts import alerts_bp
    from .controllers.maintenance import maintenance_bp

    for blueprint in (health_bp, sites_bp, devices_bp, sensors_bp, readings_bp, alerts_bp, maintenance_bp):
        app.register_blueprint(blueprint)

    @app.errorhandler(404)
    def not_found(_exc):
        from .utils import error
        return error("Endpoint atau data tidak ditemukan.", 404)

    @app.errorhandler(405)
    def method_not_allowed(_exc):
        from .utils import error
        return error("HTTP method tidak diizinkan untuk endpoint ini.", 405)

    @app.errorhandler(500)
    def internal_error(_exc):
        db.session.rollback()
        from .utils import error
        return error("Terjadi kesalahan internal pada server.", 500)

    return app
