import os
from flask import Flask, jsonify
from flask_cors import CORS

from app.config import config
from app.extensions import db, migrate


def create_app(config_name: str = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config["default"]))

    # Allow frontend dev server
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes.ocr import bp as ocr_bp
    from app.routes.receipts import bp as receipts_bp
    app.register_blueprint(ocr_bp)
    app.register_blueprint(receipts_bp)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "version": "1.0.0"})

    # Ensure upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    return app
