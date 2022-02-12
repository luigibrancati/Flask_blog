import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import Config


db = SQLAlchemy()
login = LoginManager()


def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # LOGGER
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/myblog.log',
                                       maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(file_handler)
    if app.debug:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)
    app.logger.info('myblog startup')

    # CONFIG
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.logger.debug("Config from object")
        app.config.from_object(Config)
    else:
        # Load the test config if passed in
        app.logger.debug("Config from test_config")
        app.config.from_mapping(test_config)

    app.logger.debug(app.config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate = Migrate(app, db)
    login.init_app(app)
    login.login_view = 'auth.login'

    from . import db_commands
    db_commands.init_commands(app)

    from .blueprints import auth, comment, index, post, user_profile
    app.register_blueprint(auth.bp)
    app.register_blueprint(index.bp)
    app.register_blueprint(user_profile.bp)
    app.register_blueprint(post.bp)
    app.register_blueprint(comment.bp)
    app.add_url_rule('/', endpoint='index')

    from . import models
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': models.User, 'Post': models.Post,
                'Comment': models.Comment}

    @app.errorhandler(404)
    def not_found_error(e):
        return render_template('error/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('error/500.html'), 500

    return app
