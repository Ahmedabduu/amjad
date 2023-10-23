from odoo import fields, models


# purchase.order = monthly.settlements
class MonthlySettlementsStage(models.Model):
    _name = "monthly.settlements.stage"
    code = fields.Char(string='Stage code', required=True)
    name = fields.Char(string='Stage name', required=True)
    stage_users = fields.Many2many('res.users', string='Related users')
    monthly_settlements_template = fields.Many2one('monthly.settlements.stage.type', string='M.S Template',
                                                   required=False)
    stage_order = fields.Integer(string='Stage Rank', required=True)
    _sql_constraints = [
        ('approve_stage_code_unique', 'unique(code)', 'stage code already exists!')
    ]
    is_system = fields.Boolean(string='Internal', default=False, invisible=True)
    approve_type = fields.Selection([('sequence', 'sequence'), ('parallel', 'parallel')], string='Approve Mode',
                                    default='sequence')
