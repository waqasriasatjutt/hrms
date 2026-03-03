# -*- encoding: utf-8 -*-
from odoo import http
from odoo.http import request

class AcsWebcam(http.Controller):

    @http.route('/acs/webcam/<string:model>/<int:record_id>', type='http', auth="user", website=True)
    def acs_webcam(self, model, record_id, **kw):
        record = request.env[model].sudo().search([('id', '=', record_id)])
        values = { 'record': record.id, 
            'model': model, 
            'record_name': record.display_name}
        return request.render("acs_webcam.open_webcam", values)

    @http.route(['/acs/webcam/<string:model>/<int:record_id>/updateimage'], type="http", auth="public", methods=['post'], website=True)
    def submit_rating(self, model, record_id, **kwargs):
        record = request.env[model].sudo().browse([record_id])
        record.write({'image_1920': kwargs.get('image_data')})
        return request.render("acs_webcam.close_webcam")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
