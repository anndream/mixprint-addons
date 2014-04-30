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

#import math
#import re

#from _common import rounding

from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _

#import openerp.addons.decimal_precision as dp

class ineco_product_category_stock(osv.osv):
    _name = 'ineco.product.category.stock'
    _auto = False

    _columns = {
        'category_id': fields.many2one('product.category','Category'),
        'category_child_id': fields.many2one('product.category','Child Category'),
        'product_id': fields.many2one('product.product','Product'),
        'virtual_available': fields.related('product_id', 'virtual_available', type='float', string='Forecast', readonly=True),
        'qty_available': fields.related('product_id', 'qty_available', type='float', string='On Hand', readonly=True),
    }
    
    _order = 'category_id desc, category_child_id'
        
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_product_category_stock')  
        cr.execute("""
            create or replace view ineco_product_category_stock as
            select 
              pp.id::integer as id, 
              pc2.id as category_id, 
              pc.id as category_child_id, 
              pp.id::integer as product_id 
            from product_category pc
            join product_category pc2 on pc2.id = pc.parent_id
            join product_template pt on pc.id = pt.categ_id
            join product_product pp on pt.id = pp.product_tmpl_id
            where 
               (pc.id in (41,42,43) or pc.parent_id in (41,42,43)) 
               and pc.parent_id <> 26
            order by
               pc2.id, pc.id, pt.name       
        """) 
        
class ineco_product_category_stock_option(osv.osv):
    _name = 'ineco.product.category.stock.option'
    _auto = False

    _columns = {
        'category_id': fields.many2one('product.category','Category'),
        'category_child_id': fields.many2one('product.category','Child Category'),
        'product_id': fields.many2one('product.product','Product'),
        'virtual_available': fields.related('product_id', 'virtual_available', type='float', string='Forecast', readonly=True),
        'qty_available': fields.related('product_id', 'qty_available', type='float', string='On Hand', readonly=True),
    }
    
    _order = 'category_id desc, category_child_id'
        
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_product_category_stock_option')  
        cr.execute("""
            create or replace view ineco_product_category_stock_option as
            select 
              pp.id::integer as id, 
              pc2.id as category_id, 
              pc.id as category_child_id, 
              pp.id::integer as product_id 
            from product_category pc
            join product_category pc2 on pc2.id = pc.parent_id
            join product_template pt on pc.id = pt.categ_id
            join product_product pp on pt.id = pp.product_tmpl_id
            where 
               (pc.id in (96,84,108) or pc.parent_id in (96,84,108)) 
               and pc.parent_id <> 26
            order by
               pc2.id, pc.id, pt.name       
        """) 
