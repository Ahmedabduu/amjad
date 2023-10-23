from odoo import fields, models, api

from dateutil.relativedelta import relativedelta


class MonthlySettlementsLines(models.Model):
    _name = "monthly.settlements.lines"
    _description = "Monthly Settlements Lines Sys"

    total_from_payslip = fields.Float(string='Total from Payslip')
    date_lines = fields.Date(string='Date Of Settlement')
    description_lines = fields.Char(string='Description')
    total_amount_lines = fields.Float(string='Total Amount Lines')
    monthly_settlements_lines_id = fields.Many2one('monthly.settlements', string="Monthly Settlements Lines")
    delay = fields.Boolean(string="Delay")

    @api.onchange('delay')
    def delay_on(self):
        if self.delay == True:
            print(self.delay)
            last_record = self.env['monthly.settlements.lines'].search([
                ('monthly_settlements_lines_id', '=', self.monthly_settlements_lines_id.ids),
            ], order='date_lines desc', limit=1)
            print(last_record)
            next_date = fields.Date.from_string(last_record.date_lines) + relativedelta(months=1)
            print(next_date)
            next_date_str = fields.Date.to_string(next_date)
            print(next_date_str)
            new_record = self.env['monthly.settlements.lines'].create({
                'date_lines': next_date_str,
                'description_lines': self.description_lines,
                'total_amount_lines': self.total_amount_lines,
                'monthly_settlements_lines_id': last_record.monthly_settlements_lines_id.id,
                'delay': False,
            })
            print(new_record.delay, new_record.monthly_settlements_lines_id, new_record.date_lines)


#