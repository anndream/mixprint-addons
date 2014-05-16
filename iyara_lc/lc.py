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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import time
from openerp.osv import fields, osv
#import openerp.decimal_precision as dp
from openerp.tools.translate import _

class iyara_lc(osv.osv):
    _name = 'iyara.lc'
    _description = "LC Table"
    _columns = {
        'name': fields.char('LC Number', size=32, required=True),
        'proforma_invoice_no': fields.char('Proforma Invoice No', size=32, ),
        'date': fields.date('Date'),
        'bank_name': fields.char('Bank', size=64, required=True),
        'total': fields.float('USD'),
        'currency_id': fields.many2one('res.currency','Currency',required=True),
        'available': fields.float('Available'),
        'date_tr': fields.date('Date TR'),
        'date_due': fields.date('Date Due'),
        'date_import': fields.date('Date Import'),
        'gen_name': fields.char('Gen. Name'),
        'line_ids': fields.one2many('iyara.lc.line','lc_id','Line Data'),
    }
    
class ineco_lc_line(osv.osv):
    _name = 'iyara.lc.line'
    _description = 'LC Line'
    _columns = {
        'model_name': fields.char('Model Name'),
        'quantity': fields.integer('Quantity'),
        'project_id': fields.many2one('account.analytic.account','Project',),
        'status': fields.char('Status'),
        'lc_id': fields.many2one('iyara.lc', 'LC')
    }
    