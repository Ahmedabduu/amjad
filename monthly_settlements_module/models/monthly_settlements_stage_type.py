from odoo import fields, models, api


# purchase.order = monthly.settlements
class MonthlySettlementsStageType(models.Model):
    _name = "monthly.settlements.stage.type"

    name = fields.Char(string='M.S Template', required=True)
    stages = fields.One2many('monthly.settlements.stage', 'monthly_settlements_template', string='stages')
    min_range = fields.Float(string='From')
    max_range = fields.Float(string='To')
    currency = fields.Many2one('res.currency', string='Currency', required=False)

    def get_stage_list(self):
        lst = []
        for rec in self.stages:
            lst.append(rec.code)
        print("list is ", lst)
        return lst
