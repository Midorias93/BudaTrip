from flask import Blueprint

def register_blueprints(app):
    from .endpointAuth import auth_bp
    from .endpointUsers import users_bp
    from .endpointLocalisation import location_bp
    from .endpointsInteneraray import itinerary_bp
    from .endpointWeather import weather_bp
    from .endpointBKK import bkk_bp
    from .endpointPasses import passes_bp
    from .endpointTravels import travels_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(itinerary_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(bkk_bp)
    app.register_blueprint(passes_bp)
    app.register_blueprint(travels_bp)