from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from app.database import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for all routes (important for Angular frontend)
    CORS(app)

    # Initialize extensions
    db.init_app(app)

    # Import blueprints / controllers to avoid circular dependencies
    from app.controllers.cliente_controller import cliente_bp
    from app.controllers.equipo_controller import equipo_bp
    from app.controllers.ticket_controller import ticket_bp
    from app.controllers.chat_incidencia_controller import chat_bp
    from app.controllers.historial_controller import historial_bp

    # Register blueprints
    app.register_blueprint(cliente_bp, url_prefix='/api/clientes')
    app.register_blueprint(equipo_bp, url_prefix='/api/equipos')
    app.register_blueprint(ticket_bp, url_prefix='/api/tickets')
    app.register_blueprint(chat_bp, url_prefix='/api/chats')
    app.register_blueprint(historial_bp, url_prefix='/api/historial')

    @app.route('/')
    def index():
        return jsonify({
            "message": "Python MVC Backend is running!",
            "status": "success"
        })

    # Create tables automatically for ease of development/testing
    with app.app_context():
        db.create_all()

    return app
