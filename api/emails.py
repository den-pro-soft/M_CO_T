"""Provides e-mail delivery capabilities"""

import os
import requests
from error_handling import InfrastructureError


if 'MINTAX_EMAIL_MAILGUN_URL' not in os.environ:
    raise Exception('MINTAX_EMAIL_MAILGUN_URL not specified')
if 'MINTAX_EMAIL_MAILGUN_API_KEY' not in os.environ:
    raise Exception('MINTAX_EMAIL_MAILGUN_API_KEY not specified')
if 'MINTAX_EMAIL_FROM_ADDRESS' not in os.environ:
    raise Exception('MINTAX_EMAIL_FROM_ADDRESS not specified')


def send(to_address, subject, body):
    """Sends an e-mail using a third-party service"""
    mailgun_url = os.environ['MINTAX_EMAIL_MAILGUN_URL']
    mailgun_api_key = os.environ['MINTAX_EMAIL_MAILGUN_API_KEY']
    from_address = os.environ['MINTAX_EMAIL_FROM_ADDRESS']
    mailgun_auth = requests.auth.HTTPBasicAuth('api', mailgun_api_key)
    payload = {
        "from": from_address,
        "to": to_address,
        "subject": subject,
        "html": """Dear MinTax customer,<br/>
                <br/>
                {0}<br/>
                Sincerely,<br/>
                MinTax Support Team.""".format(body)
    }
    req = requests.post(mailgun_url, auth=mailgun_auth, data=payload)
    req.raise_for_status()
    resp = req.json()
    if not resp or 'message' not in resp or resp['message'] != 'Queued. Thank you.':
        raise InfrastructureError('Unable to send e-mail')
