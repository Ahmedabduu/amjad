from odoo import fields, models


class MonthlySettlementsOrderUserAccept(models.Model):
    _name = "monthly.settlements.order.user.pending"
    user = fields.Many2one('res.users', string='user')
    monthly_settlements_id = fields.Many2one('monthly.settlements', string='M.S Order')
    state = fields.Char(string='Stage')
    status = fields.Selection(selection=[
            ('approve', 'Approve'),
        ('decline', 'Decline'),
        ('queue', 'Queue'),
        ('waiting', 'Waiting'),
    ], default='waiting')
    user_order = fields.Integer(string='User Order', default=0)


