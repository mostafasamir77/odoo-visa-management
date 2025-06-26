from odoo import fields,models,api


class hrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_visa_ids = fields.One2many('employee.visa', 'hr_employee_id')




class employeeVisa(models.Model):
    _name = 'employee.visa'
    hr_employee_id = fields.Many2one('hr.employee')

    visa_name = fields.Char(string="Approval No.")
    visa_type = fields.Many2one('visa.type')
    state = fields.Selection([
        ('used', 'Used'),
        ('not_used', 'Not Used'),
        ('expired', 'Expired'),
    ])