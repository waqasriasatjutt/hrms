# Instructions for Adding Gantt view

You can add acs.webcam.mixin in your custom model and add acs_webcam_url in view and it will work without any further changes.

EG:

In PY
------
class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner','acs.webcam.mixin']


in View
---------
    <field name="acs_webcam_url" widget="url" text="Take Picture" class="oe_bold oe_inline" nolabel="1"/>
