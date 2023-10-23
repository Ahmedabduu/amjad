from odoo import api, SUPERUSER_ID


def test_post_init_hook(cr, registry):

    env = api.Environment(cr, SUPERUSER_ID, {})
    env['monthly.settlements.stage'].create({'code': 'draft', 'name': 'To Submit', 'stage_order': -20, 'is_system': True})
    env['monthly.settlements.stage'].create({'code': 'sent', 'name': 'Submitted', 'stage_order': -10, 'is_system': True})
    env['monthly.settlements.stage'].create({'code': 'cancel', 'name': 'Cancelled', 'stage_order': 1200, 'is_system': True})
    env['monthly.settlements.stage'].create({'code': 'done', 'name': 'Done', 'stage_order': 1100, 'is_system': True})

    cr.execute(""" DROP SEQUENCE IF EXISTS seq_monthly_settlements_pstage_users
    """)
    cr.execute(""" CREATE SEQUENCE seq_monthly_settlements_pstage_users INCREMENT 1 START 1
    """)
    cr.execute(""" ALTER TABLE IF EXISTS monthly_settlements_stage_res_users_rel
    ADD COLUMN seq integer DEFAULT nextval('seq_monthly_settlements_pstage_users'::regclass)
    """)
