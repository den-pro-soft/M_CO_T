# pylint: disable=W0611
"""Asynchronous tasks backed by Celery"""

import os
from celery import Celery
from flask_app import app as flask


QUEUE_NAME_PREFIX = os.environ['MINTAX_QUEUE_NAME_PREFIX'] \
                    if 'MINTAX_QUEUE_NAME_PREFIX' in os.environ \
                    else 'mintax-dev-'

# pylint: disable=C0103
app = Celery('celery_app',
             broker='sqs://',
             include=['tasks.refresh_employee_travel_history'])
app.conf.broker_transport_options = {'queue_name_prefix': QUEUE_NAME_PREFIX}

# https://stackoverflow.com/questions/16478048/celery-connection-broker-lost-makes-cpu-usage-go-to-100/16580863#16580863
app.conf.broker_heartbeat = 0
app.conf.broker_heartbeat_checkrate = 0


if __name__ == '__main__':
    with flask.app_context():
        app.start()
