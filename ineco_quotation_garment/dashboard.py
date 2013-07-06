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

class ineco_sale_summary2(osv.osv):
    _name = 'ineco.sale.summary2'
    _auto = False
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_summary2')

        cr.execute(""" CREATE VIEW ineco_sale_summary2 AS (
            select 
              ru.id as user_id,
              (select count(*)::numeric || '/' || ltrim(to_char(sum(amount_untaxed),'999,999,990.00')) from sale_order so 
               where user_id = ru.id and date_part('month',now()) = date_part('month',so.date_sale_close)
                     and so.state <> 'cancel'
              ) as so,
              (select count(*)::numeric || '/' || ltrim(to_char(sum(amount_untaxed),'999,999,990.00')) from sale_order so 
               where user_id = ru.id and date_part('month',now()) = date_part('month',so.garment_order_date)
                     and so.state <> 'cancel'
              ) as mo,
              (select count(*)::numeric || '/' || ltrim(to_char(sum(planned_revenue),'999,999,990.00'))  from crm_lead cl  
               where user_id = ru.id and stage_id = 8  and type = 'opportunity' and date_closed is not null
               and date_part('month',now()) = date_part('month', date_closed)  
              ) as lose,  
              (select count(*)::numeric || '/' || ltrim(to_char(sum(planned_revenue),'999,999,990.00'))  from crm_lead cl  
               where user_id = ru.id and stage_id = 1 
               and date_part('month',now()) = date_part('month', coalesce(date_lead_to_opportunity, create_date))  
              ) as percent10, 
              (select count(*)::numeric || '/' || ltrim(to_char(sum(planned_revenue),'999,999,990.00'))  from crm_lead cl  
               where user_id = ru.id and stage_id = 3   
               and date_part('month',now()) = date_part('month', coalesce(date_lead_to_opportunity, create_date))  
              ) as percent50, 
              (select count(*)::numeric || '/' || ltrim(to_char(sum(planned_revenue),'999,999,990.00'))  from crm_lead cl  
               where user_id = ru.id and stage_id = 5  
               and date_part('month',now()) = date_part('month', coalesce(date_lead_to_opportunity, create_date))  
              ) as percent90     
            from 
              res_users ru
            left join res_partner rp on ru.partner_id = rp.id
            where ru.active = true and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60)
            order by rp.name        
        )
        """)    
        
class ineco_sale_summary(osv.osv):
    _name = 'ineco.sale.summary'
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users'),
        'so': fields.char('SO', size=32),
        'mo': fields.char('MO', size=32),
        'lose': fields.char('Lose', size=32),
        'percent10': fields.char('10 Percents', size=32),
        'percent50': fields.char('50 Percents', size=32),
        'percent90': fields.char('9O Percents', size=32),
    }     
    
    def init(self, cr):

        """
            CRM Lead Report
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'ineco_sale_summary')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_summary AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_summary2 from ineco_sale_summary2

                            ) as a
                    ) b
                ) c
            )""")
