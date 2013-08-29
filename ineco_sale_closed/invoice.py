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

from openerp.osv import fields, osv

#from datetime import datetime, timedelta
#from dateutil.relativedelta import relativedelta
import time
#import pooler
from openerp.tools.translate import _
#from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
#import decimal_precision as dp
#import netsvc
import re

class account_invoice(osv.osv):
    
    _inherit = "account.invoice"
    
    def button_close_sale(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        for id in ids:
            invoice = self.browse(cr,uid,[id])[0]
            if invoice.origin:
                docs = re.findall(r':[\w-]+[\w_]+[\w/]+',invoice.origin) or [invoice.origin]
                for doc in docs:
                    sale_no = doc.replace(':','')
                    sale_ids = self.pool.get('sale.order').search(cr, uid, [('name','=',sale_no)])
                    if sale_ids:
                        sale_obj = self.pool.get('sale.order').browse(cr, uid, sale_ids)[0]
                        if not sale_obj.sale_close_no:
                            next_no = self.pool.get('ir.sequence').get(cr, uid, 'ineco.sale.close') or False                      
                            sale_obj.write({'sale_close_no':next_no})
        return True    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: