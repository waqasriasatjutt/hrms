# booking_request_system/__init__.py
from . import models
from .data.post_init_demo import post_init_demo_records

def post_init_demo_records(cr, registry):
    # called automatically after install (using env inside function)
    from odoo.api import Environment
    env = Environment(cr, SUPERUSER_ID=1, context={})
    post_init_demo_records(env)
