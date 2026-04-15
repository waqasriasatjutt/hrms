# -*- coding: utf-8 -*-
{
    'name': 'WT ZKTeco ADMS Push',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Attendances',
    'summary': 'Receive real-time attendance punches from ZKTeco biometric devices via the ADMS push protocol',
    'description': """
WT ZKTeco ADMS Push
===================
Turns this Odoo instance into an ADMS (Push SDK) server for ZKTeco biometric
devices. Devices post attendance events to /iclock/cdata and they're written
straight to hr.attendance in real time — no LAN script, no cron, no PC.

Point the device's Cloud Server URL at:
    http://<your-odoo-host>[:8069]/iclock/

Features:
- /iclock/cdata — config handshake + ATTLOG + OPERLOG push endpoints
- /iclock/getrequest — command polling (stub — returns OK)
- /iclock/devicecmd — command result acknowledgement
- zk.device model — one record per physical device (by serial number)
- zk.device.punch model — raw punch log, idempotent on (device, pin, time)
- Auto-pair punches into hr.attendance (odd punch = check_in, next = check_out)
- hr.employee adds zk_user_id field (falls back to barcode if empty)
- Reprocess button on device to re-pair unmatched punches after mapping fix
""",
    'author': 'Waqas Riasat',
    'website': 'https://way4tech.com',
    'license': 'LGPL-3',
    'depends': ['hr', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/zk_device_views.xml',
        'views/zk_device_punch_views.xml',
        'views/hr_employee_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
