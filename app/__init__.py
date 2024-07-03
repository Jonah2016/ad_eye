from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_uploads import configure_uploads

from app.schemes.forms import photos
from config import config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_mode):
    app = Flask(__name__)
    app.config.from_object(config[config_mode])

    db.init_app(app)
    migrate.init_app(app, db)

    configure_uploads(app, photos)  # Configure uploads here

    with app.app_context():
        # import blueprints
        from app.api.ads_recognition.urls import ar_bp
        from app.api.recognition_jobs.urls import rj_bp
        from app.routes import routes_bp
        from app.api.channels.urls import channels_bp

        # Register blueprints
        app.register_blueprint(ar_bp)  # ads recognition jobs
        app.register_blueprint(rj_bp)  # recognition jobs
        app.register_blueprint(routes_bp)
        app.register_blueprint(channels_bp)

    return app



