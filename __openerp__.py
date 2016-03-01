# -*- coding: utf-8 -*-
##############################################################################
#
#    check_user_access module for OpenERP, Allows to easily check users' access rights
#    Copyright (C) 2016 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
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

{
    'name': 'Check User Access',
    'version': '1.0',
    'category': 'Custom',
    'description': """Allows to easily check users' access rights""",
    'author': 'SYLEAM',
    'website': 'http://www.syleam.fr/',
    'depends': ['base'],
    'update_xml': [
        'wizard/check_user_access.xml',
    ],
    'installable': True,
    'active': False,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
