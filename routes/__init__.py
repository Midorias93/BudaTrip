from flask import Blueprint

def register_blueprints(app):
    from .auth import auth_bp
    from .users import users_bp
    from .location import location_bp
    from .weather import weather_bp
    from .bkk import bkk_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(bkk_bp)