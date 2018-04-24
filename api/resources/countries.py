"""Contries domain REST resource"""

from flask import Blueprint, request, jsonify
import security
from models.countries import Country
# pylint: disable=C0103
bp = Blueprint('countries', __name__)


@bp.route('', methods=['GET'])
def fetch():
    """Fetches countries"""
    security.authorize(request)

    query = request.args['query'].lower() if 'query' in request.args else ''
    countries = Country.query \
                       .filter(Country.name.ilike('%{0}%'.format(query)) | \
                               Country.code.ilike(query)) \
                       .order_by(Country.name) \
                       .all()

    return jsonify(list(map(lambda country: {
        "code": country.code,
        "name": country.name,
    }, countries)))
