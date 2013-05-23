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

# from lxml import etree
# from datetime import datetime
# from dateutil.relativedelta import relativedelta
# import time
# from operator import itemgetter
# from itertools import groupby

from openerp.osv import fields, osv
#from tools.translate import _
#import netsvc
#import tools
#from tools import float_compare
import openerp.addons.decimal_precision as dp
# import logging
# _logger = logging.getLogger(__name__)

class ineco_delivery_type(osv.osv):
    _name = "ineco.delivery.type"
    _description = "Delivery Type"
    _columns = {
        'name': fields.char('Description', size=128),
    }
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Description must be unique !')
    ]

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _description = 'Add Sale Quantity'
    _columns = {
        'product_sale_qty': fields.float('Sale Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True),
        'color_id': fields.many2one('sale.color', 'Color'),
        'gender_id': fields.many2one('sale.gender', 'Gender'),
        'size_id': fields.many2one('sale.size', 'Size'),        
    }
    
class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    _columns = {
        'delivery_type_id': fields.many2one('ineco.delivery.type','Delivery Type'),
        'shiping_cost': fields.float('Shipping Cost', digits_compute=dp.get_precision('Account')),
    }
    
class stock_picking(osv.osv):
    
    _inherit = "stock.picking"
    
#     def name_get(self, cr, uid, ids, context=None):
#         if not ids:
#             return []
#         reads = self.read(cr, uid, ids, ['name'], context)
#         res = []
#         for record in reads:
#             name = record['name']
#             res.append((record['id'], name))
#         return res
    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]
            query_args = {'name': search_name}
            limit_str = ''
            if limit:
                limit_str = ' limit %(limit)s'
                query_args['limit'] = limit
            cr.execute('''
                select stock_picking.id from stock_picking
                join res_partner on stock_picking.partner_id = res_partner.id
                where            
                  (stock_picking.name ''' + operator +''' %(name)s
                  or res_partner.name ''' + operator +''' %(name)s) '''+ limit_str, query_args)
            ids = map(lambda x: x[0], cr.fetchall())
            if args:
                ids = self.search(cr, uid, [('id', 'in', ids)] + args, limit=limit, context=context)
            if ids:
                return self.name_get(cr, uid, ids, context)
        return super(stock_picking,self).name_search(cr, uid, name, args, operator=operator, context=context, limit=limit)    
    
    