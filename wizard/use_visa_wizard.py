# from email.policy import default
from email.policy import default

from odoo import fields,models,api
from odoo.exceptions import UserError


class useVisa(models.TransientModel):
    _name = 'use.visa'

    visa_management_wizard_id = fields.Many2one('visa.management')


    assigned_employee = fields.Many2one('hr.employee',string="Employee")
    assigned_visa = fields.Many2one('visa.management.line',domain="[('visa_management_id', '=', visa_management_wizard_id)]")


    def action_confirm(self):
        for rec in self:
            if rec.assigned_visa and rec.assigned_employee:
                rec.assigned_visa.employee = rec.assigned_employee.id
                rec.assigned_visa.assigning_date = fields.Date.today()

                journal_entries = self.env['account.move'].create({
                    'move_type': 'entry',
                    'ref': rec.assigned_visa.name,
                    'date': rec.assigned_visa.assigning_date,
                    'line_ids': [
                        (0, 0, {
                            'account_id': rec.assigned_visa.visa_type.visa_expense.id,
                            'name': rec.assigned_visa.name,
                            'debit': rec.assigned_visa.visa_type.cost,
                            'credit': 0.0,
                        }),
                        (0, 0, {
                            'account_id': rec.assigned_visa.visa_type.prepaid.id,
                            'name': rec.assigned_visa.name,
                            'credit': rec.assigned_visa.visa_type.cost,
                            'debit': 0.0,
                        }),
                    ],
                })

                employee_visa_rec = self.env['employee.visa'].create({

                    'hr_employee_id': rec.assigned_visa.employee.id,
                    'visa_name': rec.assigned_visa.visa_management_id.ref,
                    'visa_type': rec.assigned_visa.visa_type.id,
                    'state': rec.assigned_visa.state,
                })




            else:
                raise UserError("you have to fill all fields")