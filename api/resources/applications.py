"""Applications domain REST resource"""

from flask import Blueprint, request, jsonify
import security
from models.applications import Application
# pylint: disable=C0103
bp = Blueprint('applications', __name__)


@bp.route('', methods=['GET'])
def fetch():
    """Fetches applications"""
    security.authorize(request)

    apps = Application.query \
                      .order_by(Application.name) \
                      .all()

    return jsonify(list(map(lambda app: {
        "id": app.id,
        "name": app.name,
    }, apps)))
