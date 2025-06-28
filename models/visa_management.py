import datetime
from email.policy import default

from odoo import models,fields,api
from odoo.exceptions import UserError


class visaManagement(models.Model):
    _name = 'visa.management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    visa_application_ids = fields.One2many('visa.application', 'visa_management_id')
    visa_usage_ids = fields.One2many('visa.management.line','visa_management_id')

    ref = fields.Char(default='New', readonly=1)
    application_date = fields.Date(tracking=1)
    visa_application_no = fields.Char(tracking=1)
    expire_date = fields.Date()

    states = fields.Selection([
        ('draft','Draft'),
        ('hr_manager','HR Manager'),
        ('fiance_approval','Fiance Approval'),
        ('approved','Approved'),
        ('expired','Expired'),
        ('rejected','Rejected'),
    ],default='draft')


    has_hr_group = fields.Boolean(compute='_compute_has_hr_group')
    has_finance_group = fields.Boolean(compute='_compute_has_finance_group')
    vendor_bill_count = fields.Integer(compute='_compute_vendor_bill_count')



    # automated action
    def check_expire_date(self):
        visa_recs =  self.search([])
        for rec in visa_recs:
            if rec.expire_date and rec.expire_date <= fields.date.today():
                rec.states = 'expired'
                for line in rec.visa_usage_ids:
                    line.expired_visa = True



    def _compute_has_hr_group(self):
        for rec in self :
            rec.has_hr_group = self.env.user.has_group('visa_management.visa_hr_manager_group')

    def _compute_has_finance_group(self):
        for rec in self :
            rec.has_finance_group = self.env.user.has_group('visa_management.visa_finance_group')


    def _compute_vendor_bill_count(self):
        for rec in self :
            bills_count_for_smart = self.env['account.move'].search([
                ('move_type', '=', 'in_invoice'),
                ('visa_management_id', '=', self.id),
            ])

            rec.vendor_bill_count = len(bills_count_for_smart)  


    @api.model
    def create(self,vals): #for the sequence
        res = super(visaManagement,self).create(vals)
        if res.ref == 'New' :
            res.ref = self.env['ir.sequence'].next_by_code('visa_management_seq')
        return res


    def action_sumit(self):
        for rec in self :

            rec.states = 'hr_manager'

            # for the notification
            group = self.env.ref('visa_management.visa_hr_manager_group')
            users_in_group = self.env['res.users'].search([
                ('groups_id', 'in', group.id),
                ('active', '=', True)
            ])
            for user in users_in_group:
                self.activity_schedule(
                    'mail.mail_activity_data_todo',  # Activity type XML ID
                    summary='Change the state to HR Manager',
                    note='This notification is for all users in the group HR Manager',
                    user_id=user.id,
                    date_deadline=fields.Date.today()
                )

    def action_hr_approve(self):
        for rec in self:
            rec.states = 'fiance_approval'

            for record in rec.visa_application_ids :

                # creating the vendor bill
                vendor_bill = self.env['account.move'].create({
                    'move_type': 'in_invoice',
                    'partner_id': record.visa_type.vendor.id,
                    'visa_management_id': self.id,
                    'journal_id': record.visa_type.journal.id,
                    'invoice_date': rec.application_date,

                })

                vendor_bill_lines = self.env['account.move.line'].create({
                    'move_id' : vendor_bill.id,
                    'name' : rec.ref,
                    'account_id' : record.visa_type.prepaid.id,
                    'quantity' : record.total,
                    'price_unit' : record.visa_type.cost,

                })



            group = self.env.ref('visa_management.visa_finance_group')
            # this gives me a list of users that have this group
            users_in_group = self.env['res.users'].search([
                ('groups_id', 'in', group.id),
                ('active', '=', True)
            ])

            # for the notification to the users that have the visa finance group
            for user in users_in_group:
                self.activity_schedule(
                    'mail.mail_activity_data_todo',  # Activity type XML ID
                    summary='Change the state to finance approval',
                    note='This notification is for all users in the group finance',
                    user_id=user.id,
                    date_deadline=fields.Date.today()
                )


    def action_hr_refuse(self):
        for rec in self:
            rec.states = 'rejected'



    def action_finance_approve(self):

        for rec in self:



            all_bills = self.env['account.move'].search([
                ('move_type', '=', 'in_invoice'),
                ('visa_management_id', '=', self.id),
            ])
            count = 0
            for bill in all_bills :
                if bill.state == 'posted' :
                    count += 1

            if count != len(all_bills) :
                raise UserError("All Bill have to be confirmed")

            else:
                rec.states = 'approved'

            # create visa usage records

            for visa_application in rec.visa_application_ids:
                var = 0
                while var < visa_application.total:
                    var += 1
                    visa_usage_rec = self.env['visa.management.line'].create({
                            'visa_management_id': self.id,
                            'nationality' : visa_application.nationality.id,
                            'profession' : visa_application.profession.id,
                            'gander' : visa_application.gander,
                            'visa_type' : visa_application.visa_type.id,
                            'total_rec_related_to_create' : visa_application.id,
                        })







    def action_finance_refuse(self):
        for rec in self:
            rec.states = 'rejected'


    def action_view_vendor_bills(self):
        # Action to open related vendor bills
        self.ensure_one()

        # Search for related vendor bills
        bills = self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('visa_management_id', '=', self.id),
        ])



        # If only one bill, open form view
        if len(bills) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Vendor Bill',
                'res_model': 'account.move',
                'res_id': bills.id,
                'view_mode': 'form',
                'target': 'current',
            }

        # If multiple bills, open list view
        return {
            'type': 'ir.actions.act_window',
            'name': 'Related Vendor Bills',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [
                ('move_type', '=', 'in_invoice'),
                ('visa_management_id', '=', self.id),
            ],
            'context': {
                'default_move_type': 'in_invoice',
                'default_visa_management_id': self.id,
            },
            'target': 'current',
        }




    def action_use_visa(self):
        action = self.env['ir.actions.actions']._for_xml_id('visa_management.use_visa_wizard_action')
        action['context'] = {'default_visa_management_wizard_id' : self.id}
        return action



    def action_visa_return(self):
        print("hallo world")


class visaApplication(models.Model):
    _name = 'visa.application'
    visa_management_id = fields.Many2one('visa.management')
    visa_usage_ids = fields.One2many('visa.management.line', 'total_rec_related_to_create')



    nationality = fields.Many2one('res.country', string="Country")
    profession = fields.Many2one('hr.job')
    gander = fields.Selection([
        ('male','Male'),
        ('female','Female'),
    ])
    total = fields.Integer()
    total_use = fields.Integer(compute='_compute_total_use')
    remaining  = fields.Integer(compute='_compute_remaining')
    visa_type = fields.Many2one('visa.type')

    states = fields.Selection(related='visa_management_id.states', store=True, readonly=True)





    def _compute_total_use(self):
        for rec in self:
            count = 0
            for line in rec.visa_usage_ids:

                if line.employee:
                    count  += 1

            rec.total_use = count



    @api.onchange('total','total_use')
    def _compute_remaining(self):
        for rec in self:
            rec.remaining = rec.total - rec.total_use

class visaUsage(models.Model):
    _name = 'visa.management.line'
    visa_management_id = fields.Many2one('visa.management')

    name = fields.Char(default='New', readonly=1)
    nationality = fields.Many2one('res.country', string="Country" , readonly=1)
    profession = fields.Many2one('hr.job', readonly=1)
    gander = fields.Selection([
        ('male','Male'),
        ('female','Female'),
    ],readonly=1)
    visa_type = fields.Many2one('visa.type',readonly=1)
    employee = fields.Many2one('hr.employee',readonly=1)
    state = fields.Selection([
        ('used','Used'),
        ('not_used','Not Used'),
        ('expired','Expired'),
    ],compute='_compute_state')
    assigning_date = fields.Date(readonly=1)
    expired_visa = fields.Boolean()

    total_rec_related_to_create = fields.Many2one('visa.application')


    def write(self, vals):
        for rec in self:
            employee_id = vals.get('employee', rec.employee.id)
            nationality_id = vals.get('nationality', rec.nationality.id)

            existing = self.search([
                ('employee', '=', employee_id),
                ('nationality', '=', nationality_id),
                ('id', '!=', rec.id),
            ], limit=1)
            if existing:
                raise UserError("You can't assign the same employee to more than one nationality")
        return super().write(vals)


    @api.model
    def create(self,vals): #for the sequence
        res = super(visaUsage,self).create(vals)
        if res.name == 'New' :
            res.name = self.env['ir.sequence'].next_by_code('visa_usage_seq')
        return res



    @api.depends('employee','expired_visa')
    def _compute_state(self):
        for rec in self:
            if rec.expired_visa:
                rec.state = 'expired'

            elif rec.employee :
                rec.state = 'used'

            else :
                rec.state = 'not_used'

