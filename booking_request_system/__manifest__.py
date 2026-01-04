# booking_request_system/__manifest__.py
{
    "name": "Booking Request System",
    "summary": "Rooms + Booking Requests with Calendar & Gantt views",
    "version": "18.0.1.0.0",
    "author": "WAY4TECH",
    "website": "https://way4tech.com",
    "category": "Operations/Booking",
    "license": "OEEL-1",
    "depends": [
        "base",
        "web",          # core views/widgets
        "web_gantt",    # Enterprise Gantt (name may appear as 'web_enterprise' in some stacks)
    ],
    "data": [
        "security/booking_security.xml",
        "security/ir.model.access.csv",
        "views/booking_menus.xml",
        "views/booking_views.xml",
    ],
    "post_init_hook": "post_init_demo_records",
    "installable": True,
    "application": True,
}
