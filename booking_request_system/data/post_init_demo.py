# booking_request_system/data/post_init_demo.py
from datetime import datetime, timedelta
from odoo import fields

def _start_of_week(env_now):
    # Monday as start of the week
    return (env_now - timedelta(days=env_now.weekday())).replace(hour=9, minute=0, second=0, microsecond=0)

def post_init_demo_records(env):
    # Create 3 rooms if none
    Room = env["hotel.room"]
    if Room.search_count([]) == 0:
        rooms = Room.create([
            {"name": "Room A"},
            {"name": "Room B"},
            {"name": "Room C"},
        ])
    else:
        rooms = Room.search([], limit=3)

    # Create 6-8 bookings this week if none
    Booking = env["booking.request"]
    if Booking.search_count([]) == 0:
        now = fields.Datetime.context_timestamp(env.user, fields.Datetime.now())
        week_start = _start_of_week(now)

        data = [
            # room, customer, start offset (days,hours), duration hours, status
            (rooms[0].id, "Alice",   (0, 0),  4, "draft"),
            (rooms[0].id, "Bob",     (1, 2),  6, "confirmed"),
            (rooms[1].id, "Carla",   (2, 1),  8, "draft"),
            (rooms[1].id, "Diego",   (3, 0),  3, "canceled"),
            (rooms[2].id, "Elena",   (3, 5),  5, "confirmed"),
            (rooms[2].id, "Farhan",  (4, 2),  6, "draft"),
            (rooms[0].id, "Gina",    (5, 1),  3, "confirmed"),
        ]

        records = []
        for room_id, customer, (d_off, h_off), hours, status in data:
            start_dt = week_start + timedelta(days=d_off, hours=h_off)
            stop_dt = start_dt + timedelta(hours=hours)
            records.append({
                "room_id": room_id,
                "customer": customer,
                "check_in": fields.Datetime.to_string(start_dt),
                "check_out": fields.Datetime.to_string(stop_dt),
                "status": status,
            })
        Booking.create(records)
