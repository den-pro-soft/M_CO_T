"""Password recovery resource"""

from flask import Blueprint, request
from error_handling import InvalidUsage
import security
import emails
from models.storage import db
from models.users import User
# pylint: disable=C0103
bp = Blueprint('password-recovery', __name__)


@bp.route('', methods=['POST'])
def recover():
    """Processes password recovery attempts"""
    attempt = request.get_json()
    if attempt is None:
        raise InvalidUsage('Invalid data')

    errors = []
    if not 'email' in attempt or not attempt['email']:
        errors.append('E-mail is required')
    if errors:
        raise InvalidUsage(errors)

    if not 'captchaToken' in attempt or not attempt['captchaToken']:
        raise InvalidUsage('Please provide a captcha token')
    elif not security.check_captcha(attempt['captchaToken']):
        raise InvalidUsage('Invalid captcha token')

    user = User.query.filter_by(email=attempt['email']).first()
    if not user:
        # for security concerns it is not advisable to
        # tell the potential attacker if the e-mail was valid
        return ('', 204)

    new_password = security.generate_password()
    hashed_password = security.strong_hash(new_password)

    emails.send(to_address=attempt['email'],
                subject='MinTax - Password Recovery',
                body='''We received your password recovery request.
                Please find below your new password:<br/>
                <br/>
                <p style="margin-left: 25px; font-style: italic;">{0}</p><br/>
                <br/>
                We advise you to change your password on your next sign in.
                You can do that on the settings page
                available on the rightmost top menu.<br/>'''.format(new_password))

    user.password = hashed_password
    user.unsucessful_login_attemps = 0
    db.session.commit()

    return ('', 204)
