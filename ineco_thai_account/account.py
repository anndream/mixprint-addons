# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-Today INECO LTD,. PART. (<http://www.ineco.co.th>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################



from datetime import datetime
from dateutil.relativedelta import relativedelta

import time
from osv import fields, osv
import decimal_precision as dp
from openerp.tools.translate import _


class account_account(osv.osv):

    _inherit = "account.account"
    _columns = {
                'account_wht':fields.boolean('With Holding Tax'),
                'report_type': fields.selection([('owner','Balance Sheet (owner account)'),
                                                ('income', 'Profit & Loss (Income account)'),
                                                ('expense', 'Profit & Loss (Expense account)'),
                                                ('asset', 'Balance Sheet (Asset account)'),
                                                ('liability','Balance Sheet (Liability account)')], 'P&L / BS Category', )             
                                        
                }      
    _defaults = {
        'report_type': 'owner',
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: