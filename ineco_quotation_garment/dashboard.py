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
                     and so.state <> 'cancel' and left(so.name,2) = 'SO'
              ) as so,
              (select count(*)::numeric || '/' || ltrim(to_char(sum(amount_untaxed),'999,999,990.00')) from sale_order so 
               where user_id = ru.id and date_part('month',now()) = date_part('month',so.garment_order_date)
                     and so.state <> 'cancel' and left(so.name,2) = 'SO'
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
        'user_id': fields.many2one('res.users', 'Sale'),
        'so': fields.char('SO', size=32),
        'mo': fields.char('MO', size=32),
        'lose': fields.char('Opp Lost', size=32),
        'percent10': fields.char('Opp 10%', size=32),
        'percent50': fields.char('Opp 50%', size=32),
        'percent90': fields.char('Opp 90%', size=32),
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

class ineco_sale_summary3(osv.osv):
    _name = "ineco.sale.summary3"
    _auto = False
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_summary3')
        cr.execute("""
            CREATE VIEW ineco_sale_summary3 AS (
                select 
                  ru.id as user_id,
                  (select count(*) from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.date_sale_close)
                         and so.state <> 'cancel'
                  ) as so1,
                  (select coalesce(sum(amount_untaxed),0) from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.date_sale_close)
                         and so.state <> 'cancel'
                  ) as so2,
                  (select count(*)::numeric  from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.garment_order_date)
                         and so.state <> 'cancel'
                  ) as mo1,
                  (select coalesce(sum(amount_untaxed),0) from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.garment_order_date)
                         and so.state <> 'cancel'
                  ) as mo2,
                  (select count(*)::numeric from crm_lead cl  
                   where user_id = ru.id and stage_id = 8  and type = 'opportunity' and date_closed is not null
                   and date_part('month',now()) = date_part('month', date_closed)  
                  ) as lose1,  
                  (select coalesce(sum(planned_revenue),0) from crm_lead cl  
                   where user_id = ru.id and stage_id = 8  and type = 'opportunity' and date_closed is not null
                   and date_part('month',now()) = date_part('month', date_closed)  
                  ) as lose2,  
                  (select count(*)::numeric from crm_lead cl  
                   where user_id = ru.id and stage_id = 1 and type = 'opportunity'
                   --and date_part('month',now()) = date_part('month', coalesce(date_lead_to_opportunity, create_date))  
                  ) as percent101, 
                  (select coalesce(sum(planned_revenue),0) from crm_lead cl  
                   where user_id = ru.id and stage_id = 1 and type = 'opportunity'
                   --and date_part('month',now()) = date_part('month', coalesce(date_lead_to_opportunity, create_date))  
                  ) as percent102, 
                  (select count(*)::numeric from crm_lead cl  
                   where user_id = ru.id and stage_id = 3   
                   --and date_part('month',now()) = date_part('month', coalesce(date_lead_to_opportunity, create_date))  
                  ) as percent501, 
                  (select coalesce(sum(planned_revenue),0) from crm_lead cl  
                   where user_id = ru.id and stage_id = 3   
                   --and date_part('month',now()) = date_part('month', coalesce(date_lead_to_opportunity, create_date))  
                  ) as percent502,               
                  (select count(*)::numeric   from crm_lead cl  
                   where user_id = ru.id and stage_id = 5  
                   --and date_part('month',now()) = date_part('month', coalesce(date_lead_to_opportunity, create_date))  
                  ) as percent901,
                  (select coalesce(sum(planned_revenue),0) from crm_lead cl  
                   where user_id = ru.id and stage_id = 5  
                   --and date_part('month',now()) = date_part('month', coalesce(date_lead_to_opportunity, create_date))  
                  ) as percent902,
                  ru.nickname as nickname,
                  (select count(*)::numeric from crm_lead cl  
                   where user_id = ru.id and stage_id = 10   
                   --and date_part('month',now()) = date_part('month', coalesce(date_lead_to_opportunity, create_date))  
                  ) as percent301, 
                  (select coalesce(sum(planned_revenue),0) from crm_lead cl  
                   where user_id = ru.id and stage_id = 10   
                   --and date_part('month',now()) = date_part('month', coalesce(date_lead_to_opportunity, create_date))  
                  ) as percent302           
                      
                from 
                  res_users ru
                left join res_partner rp on ru.partner_id = rp.id
                where ru.active = true and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                   signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
                order by rp.name                
            )    
        """)
        
class ineco_sale_summary4(osv.osv):
    _name = 'ineco.sale.summary4'
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'so1': fields.integer('SO',),
        'so2': fields.integer('SO',),
        'mo1': fields.integer('MO',),
        'mo2': fields.integer('MO',),
        'lose1': fields.integer('Opp Lost',),
        'lose2': fields.integer('Opp Lost',),
        'percent101': fields.integer('10%',),
        'percent102': fields.integer('10%',),
        'percent501': fields.integer('50%',),
        'percent502': fields.integer('50%',),
        'percent901': fields.integer('90%',),
        'percent902': fields.integer('90%',),
        'nickname': fields.char('Nick Name', size=32),
        'percent301': fields.integer('30%',),
        'percent302': fields.integer('30%',),
    }     
    
    def init(self, cr):

        """
            CRM Lead Report
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'ineco_sale_summary4')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_summary4 AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_summary3 from ineco_sale_summary3

                            ) as a
                    ) b
                ) c
            )""")
        