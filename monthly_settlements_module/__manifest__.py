{
    'name': 'Monthly Settlements Module ',
    'version': '1.2',
    'summary': 'Monthly Settlements Module Sw',
    'sequence': 10,
    'description': """
Invoicing & Payments
====================
The specific and easy-to-use Invoicing system in Odoo allows you to keep track of your accounting, even when you are not an accountant. It provides an easy way to follow up on your vendors and customers.

You could use this simplified accounting in case you work with an (external) account to keep your books, and you still want to keep track of payments. This module also offers you an easy method of registering payments, without having to encode complete abstracts of account.
    """,
    'category': 'Accounting/Accounting',
    'website': 'https://www.odoo.com/app/invoicing',
    'images': [],
    'post_init_hook': 'test_post_init_hook',
    'depends': ['base', 'hr', 'purchase', 'mail', 'hr_payroll'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/monthly_settlements_view.xml',
        'views/monthly_settlements_stage_type_view.xml',
        # 'views/monthly_settlements_requests.xml'
        # 'views/monthly_settlements_pay_slips.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
