import logging
from flask import Flask
from .main_routes import main_blueprint
from .movie_routes import movie_blueprint
from .customer_routes import customer_blueprint
from .user_routes import user_blueprint
from .booking_routes import booking_blueprint
from .promotion_routes import promotion_blueprint
from .gift_card_routes import gift_card_blueprint
from .payment_routes import payment_blueprint
from .staff_routes import staff_blueprint
from .manager_routes import manager_blueprint
from .admin_routes import admin_blueprint

def create_app():
    app = Flask(__name__)
    logging.basicConfig(level=logging.DEBUG)

    app.config.from_pyfile('config.py')

 
    app.register_blueprint(main_blueprint)
    app.register_blueprint(movie_blueprint)
    app.register_blueprint(customer_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(booking_blueprint)
    app.register_blueprint(promotion_blueprint)
    app.register_blueprint(gift_card_blueprint)
    app.register_blueprint(payment_blueprint)
    app.register_blueprint(staff_blueprint)
    app.register_blueprint(manager_blueprint)
    app.register_blueprint(admin_blueprint)

    return app
