from odoo import models, api


class MonthlySettlementsPaySlips(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def create(self, vals):
        payslip = super(MonthlySettlementsPaySlips, self).create(vals)
        print("employee is ", vals['employee_id'])
        if vals['employee_id']:
            employee_names = self.env['monthly.settlements'].search([
                ('employee_name', "=", vals['employee_id'])
            ], limit=1)
            for field in employee_names:
                print("fields is ", field.clicked_m_s)
                if field.clicked_m_s == True:

                    vals = {
                        'input_type_id': field.type.id,
                        'name': field.description,
                        'amount': field.result,
                        'payslip_id': payslip.id
                    }
                    self.env['hr.payslip.input'].create(vals)
                else:
                    print("NOT TO TO PAY")

            return payslip


