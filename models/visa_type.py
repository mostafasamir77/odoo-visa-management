from odoo import fields,models,api


class visaType(models.Model) :
    _name = 'visa.type'
    _inherit = ['mail.thread', 'mail.activity.mixin'] #for the chatter don't forget to add it in the view
    name = fields.Char()
    vendor = fields.Many2one('res.partner')
    journal = fields.Many2one('account.journal', domain=[('type', '=', 'purchase')])
    visa_expense = fields.Many2one('account.account',  domain=[('account_type', '=', 'expense')])
    prepaid = fields.Many2one('account.account',  domain=[('account_type', '=', 'asset_prepayments')] )
    cost = fields.Float()


