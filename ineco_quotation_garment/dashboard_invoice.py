# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 - INECO PARTNERSHIP LIMITE (<http://www.ineco.co.th>).
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


#import datetime
#import math
#import openerp
from openerp.osv import osv, fields
from openerp import tools
#from openerp import SUPERUSER_ID
#import re
#import tools
#from tools.translate import _
#import logging
#import pooler
#import pytz
#from lxml import etree

class ineco_sale_invoice_balance(osv.osv):
    _name = "ineco.sale.invoice.balance"
    _auto = False
    _columns = {
        'so_id': fields.many2one('sale.order','Sale Order'),
        'garment_order_no': fields.char('MO', size=64),
        'garment_order_date': fields.date('MO Date',), 
        'sale_id': fields.many2one('res.users', 'Sale'),
        'partner_id': fields.many2one('res.partner','Customer'),
        'sale_amount': fields.integer('Sale Amount',),        
        'invoice_amount': fields.integer('Invoice Amount',),        
    }
    _order = 'garment_order_no'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_invoice_balance')
        cr.execute("""
        CREATE OR REPLACE VIEW ineco_sale_invoice_balance AS
            select 
              so.id,
              so.id as so_id,
              so.garment_order_no,
              so.garment_order_date,
              so.user_id as sale_id,
              partner_id, 
              so.amount_untaxed as sale_amount,
              coalesce((select sum(amount_untaxed) from account_invoice where origin like '%' || so.name || '%' and state not in ('cancel')),0) as invoice_amount
            from 
              sale_order so
              left join res_partner rp on rp.id = so.partner_id
            where
              so.create_date > '2013-10-31'
              and so.amount_untaxed <> coalesce((select sum(amount_untaxed) from account_invoice where origin like '%' || so.name || '%' and state not in ('cancel')),0) 
              and so.state not in ('draft','cancel')
              and so.garment_order_no is not null
            order by so.garment_order_no        
        """)
        