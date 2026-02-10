# PURPOSE: Flask application factory for Prusa XL troubleshooting API.
# DEPENDENCIES: flask, flask_limiter, flask_caching
# MODIFICATION NOTES: v0.1 - Initial app scaffolding.

"""Flask app factory and extensions."""

from __future__ import annotations

from flask import Flask
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.api.troubleshoot import troubleshoot_bp

cache = Cache(config={"CACHE_TYPE": "RedisCache", "CACHE_REDIS_URL": "redis://redis:6379/0"})
limiter = Limiter(get_remote_address, default_limits=["60 per minute"])


# PURPOSE: Create Flask app with extensions and blueprints.
# DEPENDENCIES: Flask, Cache, Limiter
# MODIFICATION NOTES: v0.1 - Register troubleshooting blueprint.
def create_app() -> Flask:
    """Create and configure the Flask app."""
    app = Flask(__name__)
    cache.init_app(app)
    limiter.init_app(app)
    app.register_blueprint(troubleshoot_bp, url_prefix="/api")
    return app
