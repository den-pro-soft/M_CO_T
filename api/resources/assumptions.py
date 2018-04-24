"""Assumptions data REST resource"""

from flask import Blueprint, request, jsonify
from error_handling import InvalidUsage
import security
import validation as val
from models.storage import db
from models.assumptions import Assumptions
import tasks.refresh_employee_travel_history
# pylint: disable=C0103
bp = Blueprint('assumptions', __name__)


@bp.route('', methods=['GET'])
def fetch():
    """Fetches assumptions settings"""
    user = security.authorize(request)

    assumptions = Assumptions.query.filter_by(customer_id=user.customer.id).first()
    if assumptions is None:
        return jsonify(None)

    return jsonify({
        "outboundFromUKWithoutInbound": assumptions.outbound_uk_without_inbound,
        "businessTravellersTreaty3159": assumptions.business_trav_treaty_3159,
        "businessTravellersTreaty60183": assumptions.business_trav_treaty_60183,
        "useDeminimusIncidentalWorkdays": 'Y' if assumptions.use_demin_incidental_workdays else 'N',
        "deminimusIncidentalWorkdays": assumptions.deminimus_incidental_workdays,
        "useDeminimusEEAA1Workdays": 'Y' if assumptions.use_demin_eeaa1_workdays else 'N',
        "deminimusEEAA1Workdays": assumptions.deminimus_eeaa1_workdays,
        "inboundToUKWithoutOutbound": assumptions.inbound_uk_without_outbound,
    })


@bp.route('', methods=['PUT'])
def update():
    """Receives company data and stores in the database"""
    user = security.authorize(request)

    data = request.get_json()
    if data is None:
        raise InvalidUsage('Invalid data')

    check_input(data)

    assumptions = Assumptions.query.filter_by(customer_id=user.customer.id).first()
    if assumptions is None:
        assumptions = Assumptions(user.customer.id,
                                  data['outboundFromUKWithoutInbound'],
                                  data['businessTravellersTreaty3159'],
                                  data['businessTravellersTreaty60183'],
                                  data['useDeminimusIncidentalWorkdays'] == 'Y',
                                  data['deminimusIncidentalWorkdays'],
                                  data['useDeminimusEEAA1Workdays'] == 'Y',
                                  data['deminimusEEAA1Workdays'],
                                  data['inboundToUKWithoutOutbound'])
        db.session.add(assumptions)
    else:
        assumptions.outbound_uk_without_inbound = data['outboundFromUKWithoutInbound']
        assumptions.business_trav_treaty_3159 = data['businessTravellersTreaty3159']
        assumptions.business_trav_treaty_60183 = data['businessTravellersTreaty60183']
        assumptions.use_demin_incidental_workdays = data['useDeminimusIncidentalWorkdays'] == 'Y'
        assumptions.deminimus_incidental_workdays = data['deminimusIncidentalWorkdays']
        assumptions.use_demin_eeaa1_workdays = data['useDeminimusEEAA1Workdays'] == 'Y'
        assumptions.deminimus_eeaa1_workdays = data['deminimusEEAA1Workdays']
        assumptions.inbound_uk_without_outbound = data['inboundToUKWithoutOutbound']

    db.session.commit()

    tasks.refresh_employee_travel_history.schedule(user.customer.id)

    return ('', 204)


def check_input(data):
    """Check the validity of input data"""
    errors = []

    check_question1(data, errors)
    check_question3(data, errors)
    check_question4(data, errors)
    check_question5(data, errors)
    check_question6(data, errors)

    if errors:
        raise InvalidUsage(errors)


def check_question1(data, errors):
    """Check the validity of question 1 input data"""
    if 'outboundFromUKWithoutInbound' not in data \
            or data['outboundFromUKWithoutInbound'] is None \
            or data['outboundFromUKWithoutInbound'] == '':
        errors.append('Question 1: Please provide an answer')
    elif data['outboundFromUKWithoutInbound'] not in ['1', '2', '3']:
        errors.append('Question 1: Please provide a valid answer')


def check_question2(data, errors):
    """Check the validity of question 2 input data"""
    if 'inboundToUKWithoutOutbound' not in data \
            or data['inboundToUKWithoutOutbound'] is None \
            or data['inboundToUKWithoutOutbound'] == '':
        errors.append('Question 2: Please provide an answer')
    elif data['inboundToUKWithoutOutbound'] not in ['1', '2']:
        errors.append('Question 2: Please provide a valid answer')


def check_question3(data, errors):
    """Check the validity of question 3 input data"""
    if 'businessTravellersTreaty3159' not in data \
            or data['businessTravellersTreaty3159'] is None \
            or data['businessTravellersTreaty3159'] == '':
        errors.append('Question 3: Please provide an answer')
    elif data['businessTravellersTreaty3159'] not in ['1', '2']:
        errors.append('Question 3: Please provide a valid answer')


def check_question4(data, errors):
    """Check the validity of question 4 input data"""
    if 'businessTravellersTreaty60183' not in data \
            or data['businessTravellersTreaty60183'] is None \
            or data['businessTravellersTreaty60183'] == '':
        errors.append('Question 4: Please provide an answer')
    elif data['businessTravellersTreaty60183'] not in ['1', '2']:
        errors.append('Question 4: Please provide a valid answer')


def check_question5(data, errors):
    """Check the validity of question 5 input data"""
    dem_incidental_key = 'useDeminimusIncidentalWorkdays'
    if dem_incidental_key not in data or data[dem_incidental_key] is None:
        errors.append('Question 5: Please provide an answer')
    elif data['useDeminimusIncidentalWorkdays'] not in ['Y', 'N']:
        errors.append('Question 5: Invalid boolean answer')
    if 'deminimusIncidentalWorkdays' not in data \
        or data['deminimusIncidentalWorkdays'] is None \
        or data['deminimusIncidentalWorkdays'] == '':
        errors.append('Question 5: Number of days is required')
    else:
        val.check_posi_integer(errors, data['deminimusIncidentalWorkdays'],
                               'Question 5: Number of days')


def check_question6(data, errors):
    """Check the validity of question 6 input data"""
    if 'useDeminimusEEAA1Workdays' not in data or data['useDeminimusEEAA1Workdays'] is None:
        errors.append('Question 6: Please provide an answer')
    elif data['useDeminimusEEAA1Workdays'] not in ['Y', 'N']:
        errors.append('Question 6: Invalid boolean answer')

    if 'deminimusEEAA1Workdays' not in data \
        or data['deminimusEEAA1Workdays'] is None \
        or data['deminimusEEAA1Workdays'] == '':
        errors.append('Question 6: Number of days is required')
    else:
        val.check_posi_integer(errors, data['deminimusEEAA1Workdays'],
                               'Question 6: Number of days')
