# Copyright 2018 SYLEAM Info Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models, _, SUPERUSER_ID


class CheckUserAccess(models.TransientModel):
    _name = 'check.user.access'
    _description = 'User Access Check'
    _rec_name = 'user_id'

    user_id = fields.Many2one(
        comodel_name='res.users', string='User to check',
        required=True, help='User you want to check accesses.')
    check_user_right_ids = fields.One2many(
        comodel_name='check.user.right', inverse_name='check_access_id',
        string='Rights', help='List of user applied rights.')
    check_user_rule_ids = fields.One2many(
        comodel_name='check.user.rule', inverse_name='check_access_id',
        string='Rules', help='List of user applied rules.')
    model_ids = fields.Many2many(
        comodel_name='ir.model', string='Models',
        help='Models to check for access rights and rules.')

    @api.model
    def default_get(self, fields_list):
        """
        Forbid users other than the superuser to launch this wizard
        """
        if self.env.uid != SUPERUSER_ID:
            raise exceptions.UserError(
                _('Please connect with admin to use this wizard!'))

        return super().default_get(fields_list)

    def compute_check_user_access(self):
        """
        Populate the access and rules lines
        """
        if self.env.uid != SUPERUSER_ID:
            raise exceptions.UserError(
                _('Please connect with admin to use this wizard!'))

        self.write({
            'check_user_right_ids': [(5,)],
            'check_user_rule_ids': [(5,)],
        })

        for wizard in self:
            ir_models = wizard.model_ids
            if not ir_models:
                ir_models = self.env['ir.model'].search([], order='model')

            modes = ('read', 'write', 'create', 'unlink')
            check_rights = []
            check_rules = []
            for ir_model in ir_models:
                checked_model = self.env[ir_model.model]

                # Access rights are not checked on TransientModels
                if isinstance(checked_model, models.TransientModel):
                    continue

                rights = {}
                rules = {}
                for mode in modes:
                    rights[mode] = self.env['ir.model.access'].sudo(
                        user=wizard.user_id).check(
                            ir_model.model, mode=mode, raise_exception=False)
                    rules[mode] = self.env['ir.rule'].sudo(
                        user=wizard.user_id).domain_get(
                            ir_model.model, mode=mode)

                    if rules[mode][0] or rules[mode][1]:
                        where = ' AND '.join(rules[mode][0])
                        where = self.env.cr.mogrify(
                            where, tuple(rules[mode][1]))

                        check_rules.append((0, 0, {
                            'ir_model_id': ir_model.id,
                            'mode': mode,
                            'rule': where,
                            'access_id': wizard.id,
                        }))

                check_rights.append((0, 0, {
                    'ir_model_id': ir_model.id,
                    'perm_read': rights['read'],
                    'perm_create': rights['create'],
                    'perm_write': rights['write'],
                    'perm_unlink': rights['unlink'],
                    'access_id': wizard.id,
                }))

            wizard.write({
                'check_user_right_ids': check_rights,
                'check_user_rule_ids': check_rules,
            })

        return True


class CheckUserAccessLine(models.TransientModel):
    _name = 'check.user.right'
    _description = 'User Applied Right'
    _rec_name = 'ir_model_id'

    check_access_id = fields.Many2one(
        comodel_name='check.user.access', string='User access check')
    ir_model_id = fields.Many2one(
        comodel_name='ir.model', string='Model',
        help='Model affected by this access right.')
    model = fields.Char(
        related='ir_model_id.model', string='Model Name',
        help='Name of the model affected by this access right.')
    perm_read = fields.Boolean(
        string='Read Access', help='Read permission.')
    perm_create = fields.Boolean(
        string='Create Access', help='Creation permission.')
    perm_write = fields.Boolean(
        string='Write Access', help='Write permission.')
    perm_unlink = fields.Boolean(
        string='Unlink Access', help='Deletion permission.')


class CheckUserRule(models.TransientModel):
    _name = 'check.user.rule'
    _description = 'User Applied Rule'
    _rec_name = 'ir_model_id'

    check_access_id = fields.Many2one(
        comodel_name='check.user.access', string='User access check')
    ir_model_id = fields.Many2one(
        comodel_name='ir.model', string='Model Name',
        help='Model affected by this rule.')
    model = fields.Char(
        related='ir_model_id.model', string='Model',
        help='Name of the model affected by this rule.')
    rule = fields.Text(
        string='Rules', help='Rule applied for this model.')
    mode = fields.Selection(
        selection=[
            ('read', 'Read'),
            ('create', 'Create'),
            ('write', 'Write'),
            ('unlink', 'Unlink'),
        ], string='Mode',
        help='Mode on which this rule is applied')
