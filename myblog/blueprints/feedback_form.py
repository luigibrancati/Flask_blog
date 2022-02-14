from flask import Blueprint, redirect, request
from flask_login import current_user
from ..config import FEEDBACK_FORM_PREFILL_LINK


bp = Blueprint('feedback_form', __name__)


@bp.route('/provide_feedback', methods=('GET',))
def provide_feedback():
    """Build prefill URL for feedback form."""
    if not current_user.is_anonymous:
        final_url = FEEDBACK_FORM_PREFILL_LINK.format(request.referrer, current_user.email)
    else:
        final_url = FEEDBACK_FORM_PREFILL_LINK.format(request.referrer, "")
    return redirect(final_url)
