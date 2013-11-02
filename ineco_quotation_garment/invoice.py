# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from lxml import etree
import openerp.addons.decimal_precision as dp

from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class account_invoice(osv.osv):

    def _get_mo(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            sql = """
                select 
                  so.name,
                  ai.origin,
                  so.garment_order_no as garment_order_no
                from account_invoice ai
                left join sale_order_invoice_rel soi on soi.invoice_id = ai.id
                left join sale_order so on soi.order_id = so.id
                where ai.id = %s            
            """
            cr.execute(sql % order.id)
            output = cr.fetchone()
            if output:
                res[order.id] = output[2]
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()
    
    def _find_partner(self, inv):
        '''
        Find the partner for which the accounting entries will be created
        '''
        #if the chosen partner is not a company and has a parent company, use the parent for the journal entries 
        #because you want to invoice 'Agrolait, accounting department' but the journal items are for 'Agrolait'
        part = inv.partner_id
#         if part.parent_id and not part.is_company:
#             part = part.parent_id
        return part
        
    _inherit = 'account.invoice'
    _columns = {
        'garment_order_no': fields.function(_get_mo, type='char', size=32, string='Germent Order No',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'account.invoice.line': (_get_order, [], 10),
            },
        ),

    }
    
