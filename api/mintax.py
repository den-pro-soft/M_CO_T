"""MinTax main module"""
import flask
from flask import jsonify
from flask_cors import CORS
from flask_sse import sse
from sqlalchemy.exc import IntegrityError
from flask_app import app
from error_handling import BaseApiError, InvalidUsage
from resources.login import bp as login_bp
from resources.company import bp as company_bp
from resources.employees import bp as employees_bp
from resources.countries import bp as countries_bp
from resources.assumptions import bp as assumptions_bp
from resources.password_recovery import bp as password_recovery_bp
from resources.admin import bp as admin_bp
from resources.traveller_data import bp as traveller_data_bp
from resources.applications import bp as applications_bp
from resources.report_results import bp as report_results_bp
from resources.additional_clarifications import bp as additional_clarifications_bp



CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(sse, url_prefix="/stream")
app.register_blueprint(login_bp, url_prefix="/login")
app.register_blueprint(company_bp, url_prefix="/company")
app.register_blueprint(employees_bp, url_prefix="/employees")
app.register_blueprint(countries_bp, url_prefix="/countries")
app.register_blueprint(assumptions_bp, url_prefix="/assumptions")
app.register_blueprint(password_recovery_bp, url_prefix="/password-recovery")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(traveller_data_bp, url_prefix="/traveller-data")
app.register_blueprint(applications_bp, url_prefix="/applications")
app.register_blueprint(report_results_bp, url_prefix="/report-results")
app.register_blueprint(additional_clarifications_bp, url_prefix="/additional-clarifications")



@app.after_request
def add_cors(resp):
    """ Ensure all responses have the CORS headers. This ensures any failures are also accessible
        by the client. """
    resp.headers['Access-Control-Allow-Origin'] = flask.request.headers.get('Origin','*')
    resp.headers['Access-Control-Allow-Credentials'] = True
    resp.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, PUT'
    resp.headers['Access-Control-Allow-Headers'] = flask.request.headers.get( 'Access-Control-Request-Headers', 'Authorization' )
    # set low for debugging
    if app.debug:
        resp.headers['Access-Control-Max-Age'] = '1'
    return resp

@app.errorhandler(BaseApiError)
def handle_invalid_usage(error):
    """Captures exceptions of type BaseApiError
    and returns the proper http response"""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(IntegrityError)
def handle_integrity_error(error):
    """Captures integrity errors and returns a
    better http response"""

    custom_message = None
    if error.orig and error.orig.diag:
        if error.orig.diag.constraint_name == 'users_email_key':
            custom_message = 'E-mail address already exists in the database'

    if custom_message:
        return handle_invalid_usage(InvalidUsage(custom_message))

    raise error
