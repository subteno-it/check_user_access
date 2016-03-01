# -*- coding: utf-8 -*-
##############################################################################
#
#    check_user_access module for OpenERP, Allows to easily check users' access rights
#    Copyright (C) 2016 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#              Sebastien LANGE <sebastien.lange@syleam.fr>
#
#    This file is a part of check_user_access
#
#    check_user_access is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    check_user_access is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
from openerp import SUPERUSER_ID
from tools.translate import _


class check_user_access(osv.TransientModel):
    _name = 'check.user.access'
    _description = 'User Access Check'
    _rec_name = 'user_id'

    _columns = {
        'user_id': fields.many2one('res.users', string='User to check', required=True, help='User you want to check accesses'),
        'check_user_right_ids': fields.one2many('check.user.right', 'check_access_id', string='Rights', help='List of user applied rights'),
        'check_user_rule_ids': fields.one2many('check.user.rule', 'check_access_id', string='Rules', help='List of user applied rules'),
        'model_ids': fields.many2many('ir.model', 'ir_model_check_user_rel', 'access_id', 'model_id', string='Models', help='Models to check for access rights and rules'),
    }

    def default_get(self, cr, uid, fields_list, context=None):
        """
        Forbid users other than the superuser to launch this wizard
        """
        if uid != SUPERUSER_ID:
            raise osv.except_osv(_('Not allowed'), _('Please connect with admin to use this wizard!'))

        return super(check_user_access, self).default_get(cr, uid, fields_list, context=context)

    def compute_check_user_access(self, cr, uid, ids, context=None):
        """
        Populate the access and rules lines
        """
        if uid != SUPERUSER_ID:
            raise osv.except_osv(_('Not allowed'), _('Please connect with admin to use this wizard!'))

        ir_model_obj = self.pool.get('ir.model')
        ir_model_access_obj = self.pool.get('ir.model.access')
        ir_rule_obj = self.pool.get('ir.rule')

        self.write(cr, uid, ids, {
            'check_user_right_ids': [(5,)],
            'check_user_rule_ids': [(5,)]
        }, context=context)

        for wizard in self.browse(cr, uid, ids, context=context):
            ir_model_ids = [model.id for model in wizard.model_ids]
            if not ir_model_ids:
                ir_model_ids = ir_model_obj.search(cr, uid, [], order='model', context=context)

            modes = ('read', 'write', 'create', 'unlink')
            check_rights = []
            check_rules = []
            for ir_model in ir_model_obj.browse(cr, uid, ir_model_ids, context=context):
                checked_model = self.pool.get(ir_model.model)

                # Skip deleted models
                if not checked_model:
                    continue

                # Access rights are not checked on TransientModels
                if isinstance(checked_model, osv.osv_memory):
                    continue

                rights = {}
                rules = {}
                for mode in modes:
                    rights[mode] = ir_model_access_obj.check(cr, wizard.user_id.id, ir_model.model, mode, False, context)
                    rules[mode] = ir_rule_obj.domain_get(cr, wizard.user_id.id, ir_model.model, mode='read', context=context)

                    if rules[mode][0] or rules[mode][1]:
                        where = ' AND '.join(rules[mode][0])
                        where = cr.mogrify(where, tuple(rules[mode][1]))

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


class check_user_access_line(osv.TransientModel):
    _name = 'check.user.right'
    _description = 'User Applied Right'
    _rec_name = 'ir_model_id'

    _columns = {
        'check_access_id': fields.many2one('check.user.access', string='User access check'),
        'ir_model_id': fields.many2one('ir.model', string='Model', help='Model affected by this access right'),
        'model': fields.related('ir_model_id', 'model', type='char', size=64, string='Model Name', help='Name of the model affected by this access right'),
        'perm_read': fields.boolean(string='Read Access', help='Read permission'),
        'perm_create': fields.boolean(string='Create Access', help='Creation permission'),
        'perm_write': fields.boolean(string='Write Access', help='Write permission'),
        'perm_unlink': fields.boolean(string='Unlink Access', help='Deletion permission'),
    }

    _defaults = {
        'perm_read': False,
        'perm_create': False,
        'perm_write': False,
        'perm_unlink': False,
    }


class check_user_rule(osv.TransientModel):
    _name = 'check.user.rule'
    _description = 'User Applied Rule'
    _rec_name = 'ir_model_id'

    _columns = {
        'check_access_id': fields.many2one('check.user.access', string='User access check'),
        'ir_model_id': fields.many2one('ir.model', string='Model Name', help='Model affected by this rule'),
        'model': fields.related('ir_model_id', 'model', type='char', size=64, string='Model', help='Name of the model affected by this rule'),
        'rule': fields.text(string='Rules', help='Rule applied for this model'),
        'mode': fields.selection([('read', 'Read'), ('create', 'Create'), ('write', 'Write'), ('unlink', 'Unlink')], 'Mode', help='Mode on which this rule is applied'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
