# booking_request_system/models/hotel_room.py
from odoo import models, fields

class HotelRoom(models.Model):
    _name = "hotel.room"
    _description = "Room"

    name = fields.Char("Room Name", required=True)
