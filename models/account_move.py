from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    visa_management_id = fields.Many2one('visa.management')