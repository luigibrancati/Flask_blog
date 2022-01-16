from flask import render_template, Blueprint, current_app
from myblog import db


bp = Blueprint('error', __name__)


@bp.app_errorhandler(404)
def not_found_error(e):
    current_app.logger.warning("Error 404 called")
    return render_template('404.html'), 404


@bp.app_errorhandler(500)
def internal_error(e):
    current_app.logger.warning("Error 500 called, executing rollback")
    db.session.rollback()
    return render_template('500.html'), 500
