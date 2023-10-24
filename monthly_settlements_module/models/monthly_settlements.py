from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

from datetime import date
from dateutil.relativedelta import relativedelta


class MonthlySettlements(models.Model):
    _name = "monthly.settlements"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Monthly Settlements Sys"

    employee_name = fields.Many2one('hr.employee', string='Employee Name', required=True)
    type = fields.Many2one('hr.payslip.input.type', string='Type')
    total_result = fields.Float(string='Total Result', compute="compute_total_result")
    description = fields.Char(string='Description')
    amount_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage')
    ], string='Amount Type', required=True, default='fixed')
    total_amount = fields.Monetary(string='Total Amount Percentage', currency_field='currency_id',
                                   compute="compute_total_amount")
    percentage_of = fields.Many2one('hr.salary.rule', string='Percentage Of',
                                    help='Percentage calculated on Basic or Gross Salary',
                                    domain="[('category_id.name', 'in', ['Gross', 'Basic'])]"
                                    )
    percentage = fields.Float(string='Percentage')
    num_of_month = fields.Integer(
        string='Number of Months', required=True
    )
    current_user_to_approve = fields.Integer(string='Admin')
    fixed_field = fields.Float(string='Total Amount Fixed')
    date = fields.Date(string='Date of Settlement', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
    monthly_settlements_lines_ids = fields.One2many('monthly.settlements.lines', 'monthly_settlements_lines_id',
                                                    string="Monthly Settlements Lines")
    result = fields.Float(string='Result', compute="compute_result", store=True)
    result_to_type = fields.Float(string='Result', compute="compute_result")

    state = fields.Selection(selection=lambda self: self.get_stages(), string='Status',
                             readonly=True, copy=False, index=True, tracking=3, default='draft')
    monthly_settlements_type = fields.Many2one('monthly.settlements.stage.type', string='M.S Type',
                                               compute='_calc_stage',
                                               # compute='test',
                                               inverse='_get_type', tracking=3,
                                               store=True)
    min_range = fields.Float(string="From", store=True)
    max_range = fields.Float(string="To", store=True)
    clicked_m_s = fields.Boolean(string="For Compute")
    current_user_id = fields.Many2one('res.users', string='Current User')
    show = fields.Boolean(compute="compute_show")

    # @api.depends('amount_total', 'currency_id') hahahah
    # def _calc_stage(self):
    #     tot = 0
    #     currid = 0
    #     for rec in self:
    #         tot += rec.amount_total
    #         currid = rec.currency_id.id
    #
    #     ret_type = self.env['tanmya.purchase.stage.type'].search([('currency', '=', currid),
    #                                                               ('minrange', '<=', tot),
    #                                                               ('maxrange', '>=', tot)], limit=1)
    #     if not ret_type:
    #         ret_type = self.env['tanmya.purchase.stage.type'].search([('currency', '=', False), ('minrange', '<=', tot),
    #                                                                   ('maxrange', '>=', tot)], limit=1)
    #     self.purchasetype = ret_type
    #

    # def show_pending_status(self):
    #     ret = False
    #     print("monthly type1", self.monthly_settlements_type)
    #     if self.monthly_settlements_type:
    #         print("monthly type",self.monthly_settlements_type)
    #         if self.state in self.monthly_settlements_type.get_stage_list:
    #             print("state is ",self.state, self.monthly_settlements_type.get_stage_list())
    #             if self.env['monthly.settlements.order.user.pending'].search_count([('user', '=', self.env.uid)
    #                                                                                    , ('state', '=', self.state)
    #                                                                                    , ('monthly_settlements_id', '=',
    #                                                                                       self.id)
    #                                                                                    , ('status', '=', 'waiting')]):
    #                 ret = True
    #                 print("show pending ", ret)
    #     self.show_pending = ret
    @api.onchange('num_of_month')
    def test_test(self):
        for rec in self:
            x = self._context.get('active_id')
            print("any", x)

    """
        def test : 
        Use this method to check if res is within the domain or not    
    """

    @api.depends('total_result', 'min_range', 'max_range', 'monthly_settlements_type')
    def test(self):
        for rec in self:
            stage_domain = self.env["monthly.settlements.stage.type"].search([])
            for stage_domain_type in stage_domain:
                res = rec.total_result
                mi = stage_domain_type.min_range
                ma = stage_domain_type.max_range
                if mi <= res <= ma:
                    rec.min_range = mi
                    rec.max_range = ma
                    rec.monthly_settlements_type = stage_domain_type.name

    @api.depends('total_result', 'min_range', 'max_range', 'monthly_settlements_type')
    def _calc_stage(self):

        tot = 0
        currid = 0

        for rec in self:
            stage_domain = self.env["monthly.settlements.stage.type"].search([])
            for stage_domain_type in stage_domain:
                mi = stage_domain_type.min_range
                ma = stage_domain_type.max_range
                tot = rec.fixed_field
                currid = rec.currency_id.id
                ret_type = self.env['monthly.settlements.stage.type'].search([
                    ('min_range', '<=', tot),
                    ('max_range', '>=', tot)], limit=1)
                if ret_type:
                    rec.min_range = ret_type.min_range
                    rec.max_range = ret_type.max_range

                print("ret type ", ret_type)
                if not ret_type:
                    ret_type = self.env['monthly.settlements.stage.type'].search(
                        [('currency', '=', False), ('min_range', '<=', tot),
                         ('max_range', '>=', tot)], limit=1)
                    print(" ret typr in false ", ret_type)
                self.monthly_settlements_type = ret_type
                print("momnththhthly typeee ------- ", self.monthly_settlements_type)

    def check_stage(self, ascending=True):
        count_approve = self.env['monthly.settlements.order.user.pending'].search_count([('state', '=', self.state)
                                                                                            , (
                                                                                             'monthly_settlements_id',
                                                                                             '=',
                                                                                             self.id)
                                                                                            ,
                                                                                         ('status', '=', 'approve')])
        current_stage = self.env['monthly.settlements.stage'].sudo().search([('code', '=', self.state)], limit=1)

        # print("monthely type ", self.monthly_settlements_type)
        # print("monthely type stage ", self.monthly_settlements_type.stages)
        newlist = sorted(self.monthly_settlements_type.stages, key=lambda x: x.stage_order)
        # print("new list ", newlist)
        # print("current stage is  ", current_stage)
        # print("count approve stage is  ", count_approve)

        if len(current_stage.stage_users) == count_approve:
            # print("current is ", current_stage.code)
            # print("current is ", current_stage.stage_users)
            # print("current is ", current_stage.stage_users)
            if current_stage.code == newlist[len(newlist) - 1].code:
                # print("################")
                #
                print("from here 1 ")
                salary_slips_to_pay = self.env['hr.payslip'].search([
                    ("employee_id", "=", self.employee_name.ids),
                    ("state", "=", "verify")
                ])
                self.clicked_m_s = True
                print("from here all we have in to pay 2", salary_slips_to_pay)
                salary_sorted = salary_slips_to_pay.sorted(key=lambda r: r.number, reverse=not ascending)
                print("from hereall we have in to pay with sorte 3 ", salary_sorted)
                record_created = False
                self.state = 'done'
                self.action_create_record(ascending=True)

                # super(MonthlySettlements, self).action_submit()
            else:
                # print("$$$$$$$$$$$$$$$$$$$")
                for x in range(0, len(newlist) - 1):
                    if newlist[x].code == current_stage.code:
                        self.state = newlist[x + 1].code
                        # print("state is sssssss", self.state)
                        current_stage = self.env['monthly.settlements.stage'].sudo().search([('code', '=', self.state)],
                                                                                            limit=1)
                        uorder = 0
                        rec_id = self.env['ir.model'].sudo().search([('model', '=', 'monthly.settlements')], limit=1)
                        # print(rec_id)
                        qquery = " select seq,res_users_id from monthly_settlements_stage_res_users_rel  where monthly_settlements_stage_id=" + str(
                            current_stage.id) + " order by seq"
                        self.env.cr.execute(qquery)
                        stage_users = self.env.cr.fetchall()
                        for user in stage_users:
                            # print("stage line is ", stages_line)

                            # print("user[1]", user)
                            uorder = uorder + 1
                            if uorder == 1:
                                # print("1")
                                self.env['monthly.settlements.order.user.pending'].create({
                                    'user': user[1],
                                    'monthly_settlements_id': self.id,
                                    'state': self.state,
                                    'status': 'waiting',
                                    'user_order': uorder
                                })
                                self.write({'current_user_id': user[1]})
                                self.env['mail.activity'].sudo().create({
                                    'activity_type_id': 4,
                                    'date_deadline': date.today(),
                                    'summary': 'Request to approve',
                                    'user_id': user[1],
                                    'res_model_id': rec_id.id,
                                    'res_id': self.id
                                })
                            else:
                                # print("0")
                                # print("user is ", user, uorder)
                                self.env['monthly.settlements.order.user.pending'].create({
                                    'user': user[1],
                                    'monthly_settlements_id': self.id,
                                    'state': self.state,
                                    'status': 'queue',
                                    'user_order': uorder
                                })
                        # self.action_submit()
                        break

    def find_next_user(self):
        # Define logic to find the next user who should approve
        # You can use user_order or any other criteria
        # print("find next ")
        next_rec = self.env['monthly.settlements.order.user.pending'].search([
            ('state', '=', self.state),
            ('monthly_settlements_id', '=', self.id),
            ('status', '=', 'queue')],
            order='user_order',
            limit=1
        )

        if next_rec:
            print("next is ", next_rec.user)
            self.show = True
            return next_rec.user
        else:
            return None

    @api.depends('current_user_id')
    def compute_show(self):
        for rec in self:
            # print(f"current_user_id: {rec.current_user_id}, logged-in user: {self.env.user}")
            rec.show = rec.current_user_id == self.env.user

    def get_stages(self):
        lst = []
        rec_set = self.env['monthly.settlements.stage'].search([], order='stage_order')
        for stg in rec_set:
            lst.append((stg.code, stg.name))
        return lst

    def _get_type(self):
        ret = False
        if self.state in ('draft', 'sent', 'monthly_settlements', 'done'):
            pass
        else:
            user0 = self.env['res.users'].browse(self.env.uid)
            ret = user0.has_group('monthly_settlements_approve.monthly.settlements.stage.type')
        if ret:
            self._change_type()

    @api.model
    def create(self, vals_list):
        res = super(MonthlySettlements, self).create(vals_list)
        stages = self.env["monthly.settlements.stage.type"].search([('min_range', '=', vals_list.get('min_range'))])
        # print(stages)
        vals_list['current_user_to_approve'] = stages.stages.stage_users[0]
        return res

    # this is to increase date in lines
    # @api.onchange('date')
    # def onchange_date(self):
    #     for rec in self:
    #         if rec.date:
    #             current_date = fields.Date.from_string(rec.date)
    #             for line in rec.monthly_settlements_lines_ids:
    #                 line.date_lines = fields.Date.to_string(current_date)
    #                 current_date += relativedelta(months=1)

    # this is to add default text in description
    @api.model
    def default_get(self, fields):
        res = super(MonthlySettlements, self).default_get(fields)
        res['description'] = 'Per Month'
        return res

    """ 
        def compute_total_amount: 
        We used the function to check the type of amount and perform the operation according to the type
        Note: In per we must take employee_contract.wage
    """

    @api.depends('employee_name', 'amount_type', 'num_of_month', 'fixed_field', 'result')
    def compute_total_amount(self):
        for rec in self:
            rec.total_amount = 0
            if rec.amount_type == 'percentage' and rec.employee_name:
                employee_contract = self.env['hr.contract'].search([('employee_id', '=', rec.employee_name.ids),
                                                                    ('state', '=', 'open')])

                if employee_contract:
                    rec.total_amount = (employee_contract.wage * rec.percentage) / 100
            else:
                print('')

            # this is to check total_result if its in range or not + create fields in request view

    @api.depends('min_range', 'max_range')
    def action_submit(self):
        if self.monthly_settlements_type:
            if self.state in ('draft', 'sent'):
                print("action submit ", self.monthly_settlements_type)
                newlist = sorted(self.monthly_settlements_type.stages, key=lambda x: x.stage_order)
                # print("action submit ", newlist, newlist)
                self.state = newlist[0].code
                # print("state is  ", self.state, "id for stage", newlist)
                # for rec in self:
                #     # print("submit in for ")
                #     check = rec.total_result
                #     range_min = rec.min_range
                #     range_max = rec.max_range
                #     if range_min <= check <= range_max:
                #         # print("i am heereeree")
                #         rec_id = self.env['ir.model'].sudo().search([('model', '=', 'monthly.settlements')])
                #         stages = self.env["monthly.settlements.stage.type"].search([('min_range', '=', self.min_range)])
                #         # users_to_notify = []
                #         uorder = 0
                current_stage = self.env['monthly.settlements.stage'].sudo().search([('code', '=', self.state)],
                                                                                    limit=1)
                uorder = 0
                rec_id = self.env['ir.model'].sudo().search([('model', '=', 'monthly.settlements')], limit=1)
                # print(rec_id)
                qquery = " select seq,res_users_id from monthly_settlements_stage_res_users_rel  where monthly_settlements_stage_id=" + str(
                    current_stage.id) + " order by seq"
                self.env.cr.execute(qquery)
                stage_users = self.env.cr.fetchall()
                for user in stage_users:
                    # print("stage line is ", stages_line)
                    # print("user[1]", user)
                    uorder = uorder + 1
                    if uorder == 1:
                        # print("1")
                        self.env['monthly.settlements.order.user.pending'].create({
                            'user': user[1],
                            'monthly_settlements_id': self.id,
                            'state': self.state,
                            'status': 'waiting',
                            'user_order': uorder
                        })
                        self.write({'current_user_id': user[1]})
                        self.env['mail.activity'].sudo().create({
                            'activity_type_id': 4,
                            'date_deadline': date.today(),
                            'summary': 'Request to approve',
                            'user_id': user[1],
                            'res_model_id': rec_id.id,
                            'res_id': self.id
                        })
                    else:
                        # print("0")
                        # print("user is ", user, uorder)
                        self.env['monthly.settlements.order.user.pending'].create({
                            'user': user[1],
                            'monthly_settlements_id': self.id,
                            'state': self.state,
                            'status': 'queue',
                            'user_order': uorder
                        })
            else:
                print("not in range")
        else:
            stages = self.env["monthly.settlements.stage.type"].search([('min_range', '=', self.min_range)])
            if stages:
                if self.state in ('draft', 'sent'):
                    # print("action submit 1  ")
                    newlist = sorted(stages.stages, key=lambda x: x.stage_order)
                    # print("action submit 1  ", newlist)
                    self.state = newlist[0].code
                    # print("stateee in elseee ----- :", self.state)
                    # print("state is  ", self.state, "id for stage", newlist)
                    # for rec in self:
                    #     # print("submit in for ")
                    #     check = rec.total_result
                    #     range_min = rec.min_range
                    #     range_max = rec.max_range
                    #     if range_min <= check <= range_max:
                    #         # print("i am heereeree")
                    #         rec_id = self.env['ir.model'].sudo().search([('model', '=', 'monthly.settlements')])
                    #         stages = self.env["monthly.settlements.stage.type"].search([('min_range', '=', self.min_range)])
                    #         # users_to_notify = []
                    #         uorder = 0
                    current_stage = self.env['monthly.settlements.stage'].sudo().search([('code', '=', self.state)],
                                                                                        limit=1)
                    # print("current stage is ", current_stage)
                    uorder = 0
                    rec_id = self.env['ir.model'].sudo().search([('model', '=', 'monthly.settlements')], limit=1)
                    # print(rec_id)
                    qquery = " select seq,res_users_id from monthly_settlements_stage_res_users_rel  where monthly_settlements_stage_id=" + str(
                        current_stage.id) + " order by seq"
                    self.env.cr.execute(qquery)
                    stage_users = self.env.cr.fetchall()
                    for user in stage_users:
                        # print("stage line is ", stages_line)
                        # print("user[1]", user)
                        uorder = uorder + 1
                        if uorder == 1:
                            # print("1")
                            self.env['monthly.settlements.order.user.pending'].create({
                                'user': user[1],
                                'monthly_settlements_id': self.id,
                                'state': self.state,
                                'status': 'waiting',
                                'user_order': uorder
                            })
                            self.write({'current_user_id': user[1]})
                            self.env['mail.activity'].sudo().create({
                                'activity_type_id': 4,
                                'date_deadline': date.today(),
                                'summary': 'Request to approve',
                                'user_id': user[1],
                                'res_model_id': rec_id.id,
                                'res_id': self.id
                            })
                        else:
                            # print("0")
                            # print("user is ", user, uorder)
                            self.env['monthly.settlements.order.user.pending'].create({
                                'user': user[1],
                                'monthly_settlements_id': self.id,
                                'state': self.state,
                                'status': 'queue',
                                'user_order': uorder
                            })

    @api.constrains('num_of_month')
    def _check_num_of_month(self):
        for record in self:
            if not 1 <= record.num_of_month <= 12:
                raise ValidationError(_("Number of months must be between 1 and 12."))

    """ 
        def _compute_result: 
        We used the function to compute result field
    """

    def unlink_line_if_found(self, vals):
        for rec in self:
            for line in rec.monthly_settlements_lines_ids:
                line.unlink()
            rec.create_record(vals)

    def action_calculate(self):
        for rec in self:
            vals = {
                'employee_name': self.employee_name.id,
                'type': self.type.id,
                'description': self.description,
                'amount_type': self.amount_type,
                'percentage_of': False,
                'percentage': self.percentage,
                'num_of_month': self.num_of_month,
                'current_user_to_approve': self.current_user_to_approve,
                'fixed_field': self.fixed_field,
                'date': self.date,
                'currency_id': self.currency_id.id,
                'min_range': self.min_range,
                'max_range': self.max_range,
                'clicked_m_s': self.clicked_m_s,
                'current_user_id': self.current_user_id.id,
                'input_ref': self.input_ref.id
            }
            if not rec.monthly_settlements_lines_ids:
                rec.create_record(vals)
            else:
                res = rec.unlink_line_if_found(vals)

    @api.depends('amount_type', 'total_amount', 'num_of_month', 'percentage')
    def compute_result(self):
        for rec in self:
            result = 0  # Default value
            if rec.num_of_month != 0:
                if rec.amount_type == 'percentage':
                    result = rec.total_amount / rec.num_of_month
                elif rec.amount_type == 'fixed':
                    result = rec.fixed_field / rec.num_of_month
                rec.result = result
                if rec.num_of_month:
                    num_of_lines = len(rec.monthly_settlements_lines_ids)
                    lines = rec.monthly_settlements_lines_ids
                    new_num_of_month = rec.num_of_month
                    current_date = rec.date or fields.Date.today()
                    if num_of_lines < new_num_of_month:
                        lines_to_create = new_num_of_month - num_of_lines

    """ 
        def compute_total_result: 
        We used the function to deal with final numbers according to their type
    """

    @api.depends('amount_type', 'total_amount', 'percentage', 'fixed_field', 'total_result')
    def compute_total_result(self):
        for rec in self:
            total_result1 = 0
            if rec.amount_type == 'percentage':
                total_result1 = rec.total_amount
            elif rec.amount_type == 'fixed':
                total_result1 = rec.fixed_field
            rec.total_result = total_result1

    def create_record(self, vals):
        for record in self:
            if 'date' in vals and 'num_of_month' in vals:
                current_date = vals['date']
                # vals['sent'] = 'sent'
                for i in range(vals['num_of_month']):
                    self.env['monthly.settlements.lines'].create({
                        'date_lines': current_date,
                        'description_lines': record.description,
                        'total_amount_lines': record.result,
                        # 'delay': 0,
                        'monthly_settlements_lines_id': record.id,
                    })
                    current_date = fields.Date.to_string(
                        fields.Date.from_string(current_date) + relativedelta(months=1))

    input_ref = fields.Many2one(
        comodel_name='hr.payslip.input',
        string='input ref',
        required=False
    )

    def unlink_last_record(self, obj):
        for rec in obj:
            res = rec.unlink()
            return res

    def action_pass_values(self):
        for rec in self:
            salary_slips_to_pay = rec.env['hr.payslip'].search([
                ("employee_id", "=", self.employee_name.id),
                ("state", "=", "verify")], limit=1)
            total_amount = sum(rec.monthly_settlements_lines_ids.mapped('total_amount_lines'))
            # print("total", total_amount/rec.num_of_month)
            description = rec.description
            new_lines = [({
                'payslip_id': salary_slips_to_pay.id,
                'input_type_id': rec.type.id,
                'name': description,
                'amount': total_amount,
                'sequence': 10,
            })]
            obj_input = self.env['hr.payslip.input']

            if rec.input_ref:
                # print("if")
                action = obj_input.create(new_lines)
            else:
                rec.unlink_last_record(rec.input_ref)
                # print("else",rec.unlink_last_record(rec.input_ref))
                action = obj_input.create(new_lines)
            rec.write({'input_ref': action.id})

    def action_create_record(self, ascending=True):
        # self.clicked_m_s = True
        for rec in self:
            salary_slips_to_pay = self.env['hr.payslip'].search([
                ("employee_id", "=", self.employee_name.id),
                ("state", "=", "verify"),
                # ('date_from', '<=', rec.date),
                # ('date_to', '>=', rec.date)
            ])
            # print("all we have in to pay", salary_slips_to_pay)

            for payslip in salary_slips_to_pay:
                mo = self.env['monthly.settlements'].search([("employee_name", "=", self.employee_name.id),
                                                             ('monthly_settlements_lines_ids.date_lines', '>=',
                                                              payslip.date_from),
                                                             ('monthly_settlements_lines_ids.date_lines', '<=',
                                                              payslip.date_to),

                                                             ])
                type_totals = {}
                for mo_record in mo:
                    # print("moo is ", mo_record)
                    for line in mo_record.monthly_settlements_lines_ids:
                        # print("date", line.date_lines, payslip.date_from, payslip.date_to)
                        if mo_record.type.id in type_totals:
                            if payslip.date_from <= line.date_lines <= payslip.date_to:
                                # print("###################", type_totals)
                                # If it is, add the total_amount_lines to the existing sum
                                type_totals[mo_record.type.id] += line.total_amount_lines
                                # print("type total >>>>>>>>>>>>>>>>>>>", type_totals)
                        else:
                            # print("@@@@@@@@@@@@@@@@@@@@@")
                            # If it's not, initialize the sum with the current total_amount_lines
                            type_totals[mo_record.type.id] = line.total_amount_lines

                        # print("typeee --------------", type_totals)
                for type_id, total_amount in type_totals.items():
                    for contract in payslip.contract_id:
                        for lines in rec.monthly_settlements_lines_ids:
                            # print("date from is : ", payslip.date_from)
                            # print("date to is : ", payslip.date_to)
                            if contract.state == 'open' and lines.date_lines >= payslip.date_from and lines.date_lines <= payslip.date_to:
                                x = ([{
                                    'payslip_id': payslip.id,
                                    'input_type_id': type_id,
                                    'name': lines.description_lines,
                                    'amount': total_amount,
                                }])
                                payslip.env['hr.payslip.input'].create(x)

                    # print("monthley adjustment is ", total_amount)
                    # self.state='done'

        # print(" payslip is ", payslip)
        # for contract in payslip.contract_id:
        #     # print(" lines is ", contract.state)
        #     for lines in rec.monthly_settlements_lines_ids:
        #         print("date from is : ", payslip.date_from)
        #         print("date to is : ", payslip.date_to)
        #         if contract.state == 'open' and lines.date_lines >= payslip.date_from and lines.date_lines <= payslip.date_to:
        #             print("hello open ")
        #             input_type_id = self.type.id
        #             description_lines = lines.description_lines
        #             total_amount_lines = lines.total_amount_lines
        #
        #             # Create a unique key for aggregation based on input type
        #             key = (payslip.id, input_type_id, description_lines)
        #
        #             if key in aggregated_lines:
        #                 # If the key exists, update the total amount
        #                 aggregated_lines[key]['amount'] += total_amount_lines
        #             else:
        #                 # If the key doesn't exist, create a new entry
        #                 aggregated_lines[key] = {
        #                     'payslip_id': payslip.id,
        #                     'input_type_id': input_type_id,
        #                     'name': description_lines,
        #                     'amount': total_amount_lines,
        #                 }
        #             # x = ([{
        #             #     'payslip_id': payslip.id,
        #             #     'input_type_id': self.type.id,
        #             #     'name': lines.description_lines,
        #             #     'amount': lines.total_amount_lines,
        #             # }])
        #             # payslip.env['hr.payslip.input'].create(x)
        #             print("done",aggregated_lines)

    # def action_create_record(self, ascending=True):
    #     salary_slips_to_pay = self.env['hr.payslip'].search([
    #         ("employee_id", "=", self.employee_name.id),
    #         ("state", "=", "verify"),
    #         ('date_from', '<=', self.monthly_settlements_lines_ids.date_lines),
    #         ('date_to', '>=', self.monthly_settlements_lines_ids.date_lines)
    #     ])
    #     # self.clicked_m_s = True
    #     print("all we have in to pay", salary_slips_to_pay)
    #     type_aggregations = defaultdict(float)
    #     records_by_type = {}
    #
    #     for rec in self:
    #
    #         mo = self.env['monthly.settlements'].search([])
    #         for record in mo:
    #             type_id = record.type.id
    #             if type_id not in records_by_type:
    #                 records_by_type[type_id] = []
    #             records_by_type[type_id].append(record)
    #
    #         # Now, you can iterate over the grouped records
    #         for type_id, records in records_by_type.items():
    #             print("records is ", type_id, records)
    #             records_with_same_date = rec.env['monthly.settlements.lines'].search([
    #                 ('date_lines', '=', self.date)  # Filter by the same date
    #             ])
    #             print("records with dat is ", records_with_same_date)
    #             for record in records :
    #
    #                 total_amount_sum = 0.0
    #
    #                 # for same_date in records_with_same_date:
    #                 #     # Accumulate the total_amount_lines
    #                 #     total_amount_sum += same_date.total_amount_lines
    #                 #     print("total is ", total_amount_sum)
    #
    #             # Do something with records that have the same type
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #         for payslip in salary_slips_to_pay:
    #             print(" payslip is ", payslip)
    #             for contract in payslip.contract_id:
    #                 print(" lines is ", contract.state)
    #                 for lines in rec.monthly_settlements_lines_ids:
    #                     print("date from is : " ,payslip.date_from)
    #                     print("date to is : " ,payslip.date_to)
    #                     if contract.state == 'open' and lines.date_lines >= payslip.date_from and lines.date_lines <= payslip.date_to:
    #
    #                         type_aggregations[rec.type.id] += lines.total_amount_lines
    #
    #                         # Sum total_amount_lines for the same type
    #
    #                         # x = {
    #                         #     'payslip_id': payslip.id,
    #                         #     'input_type_id': rec.type.id,
    #                         #     'name': lines.description_lines,
    #                         #     'amount': lines.total_amount_lines,
    #                         # }
    #                         # existing_input = lines
    #                         # if existing_input:
    #                         #     existing_input.amount += x['total_amount_lines']
    #                         #     print("existing input ", existing_input, x)
    #                         # else:
    #                         #     # rec.create(x)
    #                         #     print("records is ", x)
    #                         # print("done")
    #
    #
    #
    #                         # x = ([{
    #                         #     'payslip_id': payslip.id,
    #                         #     'input_type_id': self.type.id,
    #                         #     'name': lines.description_lines,
    #                         #     'amount': lines.total_amount_lines,
    #                         # }])
    #                         # payslip.env['hr.payslip.input'].create(x)
    #                         # print("done")
    #
    #                 # salary_line_values = {
    #                 #     'input_type_id': self.payslip.input_line_ids,
    #                 #     'name': self.description_lines,
    #                 #     'amount': self.total_amount_lines,
    #                 #     'payslip_id': payslip.id
    #                 # }
    #         for type_id, total_amount in type_aggregations.items():
    #             print("total amount is ", total_amount)
    #             # x = ([{
    #             #     'payslip_id': payslip.id,
    #             #     'input_type_id': self.type.id,
    #             #     'name': lines.description_lines,
    #             #     'amount': lines.total_amount_lines,
    #             # }])
    #             # payslip.env['hr.payslip.input'].create(x)

    def confirm(self, ascending=True):
        rec = self.env['monthly.settlements.order.user.pending'].search([
            ('user', '=', self.env.uid)
            , ('state', '=', self.state)
            , ('monthly_settlements_id', '=', self.id)
            , ('status', '=', 'waiting')
        ])
        if rec:
            oldstate = self.state
            rec.update({'status': 'approve'})
            next_user = self.find_next_user()  # Define this method to find the next user
            self.write({'current_user_id': next_user.id if next_user else False})
            for act in self.activity_ids:
                if act.activity_type_id.id == 4 and act.res_id == self.id and act.user_id.id == self.env.uid:
                    act.action_feedback('Request is approved')
            self.check_stage()
            if oldstate == self.state:
                rec_next = self.env['monthly.settlements.order.user.pending'].search([('state', '=', self.state)
                                                                                         , (
                                                                                          'monthly_settlements_id', '=',
                                                                                          self.id)
                                                                                         , ('status', '=', 'queue')]
                                                                                     , order='user_order'
                                                                                     , limit=1)
                # print("rec next is--------> ", rec_next)
                if rec_next:
                    rec_next[0].update({'status': 'waiting'})
                rec_id = self.env['ir.model'].sudo().search([('model', '=', 'monthly.settlements')], limit=1)
                # print(" user id in rec next is ", rec_next.user.id)
                if rec_next.user.id:
                    # print("i am heeereerererererrerererer354657890-----------------------------", rec_next)
                    x = self.env['mail.activity'].sudo().create({
                        'activity_type_id': 4,
                        'date_deadline': date.today(),
                        'summary': 'Request to approve',
                        'user_id': rec_next.user.id,
                        'res_model_id': rec_id.id,
                        'res_id': self.id
                    })
                    # print("rec nextttt --------", rec_next)
                if rec_next.status == False:
                    print("exxxxxxittt")

                # the code after me is to do compute if we have the last approve
                # salary_slips_to_pay = self.env['hr.payslip'].search([
                #     ("employee_id", "=", self.employee_name.ids),
                #     ("state", "=", "verify")
                # ])
                # print("all we have in to pay", salary_slips_to_pay)
                # salary_sorted = salary_slips_to_pay.sorted(key=lambda r: r.number, reverse=not ascending)
                # print("all we have in to pay with sorte", salary_sorted)
                # record_created = False
                # for salary in salary_sorted:
                #     salary_line_values = {
                #         'input_type_id': self.type.id,
                #         'name': self.description,
                #         'amount': self.result,
                #         'payslip_id': salary.id
                #     }
                #     if not record_created:
                #         self.env['hr.payslip.input'].create(salary_line_values)
                #         record_created = True
                #         break
                # self.state = 'done'
        else:
            print("no record")

    def decline(self):
        rec = self.env['monthly.settlements.order.user.pending'].search([
            ('user', '=', self.env.uid)
            , ('state', '=', self.state)
            , ('status', '=', 'waiting')
        ], limit=1)
        if rec:
            rec[0].update({'status': 'decline'})
            self.state = 'cancel'

    @api.onchange('result')
    def update_total_amount_lines(self):
        for record in self:
            for line in record.monthly_settlements_lines_ids:
                line.total_amount_lines = record.result
