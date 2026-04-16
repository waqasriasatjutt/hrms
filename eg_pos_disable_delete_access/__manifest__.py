{
    "name": "POS Order Delete Restriction",
    "version": "18.0",
    "category": "Point of Sale",
    "summary": "POS Restrict Order Deletion is a security-focused Odoo Point of Sale module that helps businesses control and restrict the deletion of POS orders. By providing a centralized system-level setting along with user-based permissions, the module allows administrators to define clear rules for who can and cannot delete POS orders. This prevents accidental or unauthorized deletions and ensures consistent enforcement of POS security policies across all sessions. The module enhances data accuracy and accountability by safeguarding sales records from unintended modifications. When deletion access is restricted, the delete option is automatically hidden from the POS interface, ensuring users cannot attempt unauthorized actions while continuing their regular sales operations without disruption. Odoo POS restrict order deletion, POS order delete control, Odoo POS security module, POS order deletion restriction, Odoo Point of Sale access control, POS user permission management, POS order protection, prevent POS order delete, Odoo POS order security, POS delete access management, POS order safety, POS role based access, pos Disable Delete Access, POS Order Delete Restriction, Delete Access.",
    "author": "INKERP",
    "website": "www.inkerp.com",
    "depends": [
        "point_of_sale",
        "eg_app_base"
    ],
    "data": [
        "views/pos_config_view.xml",
        "views/res_users_view.xml"
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "eg_pos_disable_delete_access/static/src/js/**/*",
            "eg_pos_disable_delete_access/static/src/xml/**/*"
        ]
    },
    "images": [
        "static/description/banner.gif"
    ],
    "license": "OPL-1",
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": "0.0",
    "currency": "EUR",
    "description": "POS Restrict Order Deletion is a security-focused Point of Sale module that enables administrators to manage and restrict POS order deletion through centralized system settings and user-based permissions. By preventing accidental or unauthorized removal of POS orders"
}