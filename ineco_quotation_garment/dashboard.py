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
                         and date_part('year',now()) = date_part('year',so.date_sale_close)
                         and so.state <> 'cancel'
                  ) as so1,
                  (select coalesce(sum(amount_untaxed),0) from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.date_sale_close)
                         and date_part('year',now()) = date_part('year',so.date_sale_close)
                         and so.state <> 'cancel'
                  ) as so2,
                  (select count(*)::numeric  from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.garment_order_date)
                        and date_part('year',now()) = date_part('year',so.garment_order_date)
                        and so.state <> 'cancel'
                  ) as mo1,
                  (select coalesce(sum(amount_untaxed),0) from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.garment_order_date)
                        and date_part('year',now()) = date_part('year',so.garment_order_date)
                        and so.state <> 'cancel'
                  ) as mo2,
                  (select count(*)::numeric from crm_lead cl  
                   where user_id = ru.id and stage_id = 8  and type = 'opportunity' and date_closed is not null
                     and date_part('month',now()) = date_part('month',cl.date_closed)
                     and date_part('year',now()) = date_part('year',cl.date_closed) 
                  ) as lose1,  
                  (select coalesce(sum(planned_revenue),0) from crm_lead cl  
                   where user_id = ru.id and stage_id = 8  and type = 'opportunity' and date_closed is not null
                     and date_part('month',now()) = date_part('month',cl.date_closed)
                     and date_part('year',now()) = date_part('year',cl.date_closed) 
                  ) as lose2,  
                  (select count(*)::numeric from crm_lead cl  
                   where user_id = ru.id and stage_id = 1 and type = 'opportunity'
                  ) as percent101, 
                  (select coalesce(sum(planned_revenue),0) from crm_lead cl  
                   where user_id = ru.id and stage_id = 1 and type = 'opportunity'
                  ) as percent102, 
                  (select count(*)::numeric from crm_lead cl  
                   where user_id = ru.id and stage_id = 3   
                  ) as percent501, 
                  (select coalesce(sum(planned_revenue),0) from crm_lead cl  
                   where user_id = ru.id and stage_id = 3   
                  ) as percent502,               
                  (select count(*)::numeric   from crm_lead cl  
                   where user_id = ru.id and stage_id = 5  
                  ) as percent901,
                  (select coalesce(sum(planned_revenue),0) from crm_lead cl  
                   where user_id = ru.id and stage_id = 5  
                  ) as percent902,
                  ru.nickname as nickname,
                  (select count(*)::numeric from crm_lead cl  
                   where user_id = ru.id and stage_id = 10   
                  ) as percent301, 
                  (select coalesce(sum(planned_revenue),0) from crm_lead cl  
                   where user_id = ru.id and stage_id = 10   
                  ) as percent302,
                  (
                  select count(*) from crm_lead where type = 'opportunity'
                      and user_id = ru.id
                      and stage_id in (1,3,5,10)
                  ) as total_opportunity   
                      
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
        'total_opportunity': fields.integer('Total Opp',),
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
        
class ineco_sale_summary5_query(osv.osv):
    _name = "ineco.sale.summary5.query"
    _auto = False
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_summary5_query')
        cr.execute("""
        CREATE OR REPLACE VIEW ineco_sale_summary5_query AS (
                select 
                  ru.id as user_id,
                  ru.nickname,
                  /*(select count(*) from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.date_sale_close)
                         and so.state <> 'cancel'
                  ) as so1,*/
                  (select coalesce(sum(amount_untaxed),0) from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.date_sale_close)
                         and date_part('year',now()) = date_part('year',so.date_sale_close)
                         and so.state <> 'cancel'
                  ) as so2,
                  /*
                  (select count(*)::numeric  from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.garment_order_date)
                        and date_part('year',now()) = date_part('year',so.garment_order_date)
                        and so.state <> 'cancel'
                  ) as mo1,*/
                  (select coalesce(sum(amount_untaxed),0) from sale_order so 
                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.garment_order_date)
                        and date_part('year',now()) = date_part('year',so.garment_order_date)
                        and so.state <> 'cancel'
                  ) as mo2,
                  (
                    select coalesce(count(*),0) from res_partner 
                    where user_id = ru.id
                  ) as total_customer,
                  (
                    select coalesce(count(*),0) from res_partner 
                    where user_id = ru.id and is_company = true
                  ) as total_customer_company,            
                  (
                    select coalesce(count(*),0) from res_partner 
                    where user_id = ru.id and date_part('month',now()) = date_part('month', res_partner.create_date)
                        and date_part('year',now()) = date_part('year', res_partner.create_date)
                  ) as total_customer_new,
                  (select coalesce(count(*),0) from crm_phonecall cp
            left join crm_case_categ ccc on cp.categ_id = ccc.id
            where ccc.id = 9 and date_part('month',now()) = date_part('month', cp.create_date)
                        and date_part('year',now()) = date_part('year', cp.create_date)  
                        and cp.user_id = ru.id
                  ) as logcall_inbound,
                  (select coalesce(count(*),0) from crm_phonecall cp
            --left join crm_case_categ ccc on cp.categ_id = ccc.id
            where (cp.categ_id is null or cp.categ_id = 10) and date_part('month',now()) = date_part('month', cp.create_date)
                        and date_part('year',now()) = date_part('year', cp.create_date)  
                        and cp.user_id = ru.id
                  ) as logcall_outbound,
                  (select coalesce(count(*),0) from crm_phonecall cp
            left join crm_case_categ ccc on cp.categ_id = ccc.id
            where cp.visit = true and date_part('month',now()) = date_part('month', cp.create_date)
                        and date_part('year',now()) = date_part('year', cp.create_date)  
                        and cp.user_id = ru.id
                  ) as logcall_visit,
                  (
                    select count(*) from sale_order where state <> 'cancel'  and user_id = ru.id
                        and date_part('month',now()) = date_part('month', sale_order.date_sale_close)
                        and date_part('year',now()) = date_part('year', sale_order.date_sale_close)  
                  ) as total_quotation,
                  (
                    select count(*) from sale_order where state in ('manual','send')  and user_id = ru.id
                        and date_part('month',now()) = date_part('month', sale_order.date_sale_close)
                        and date_part('year',now()) = date_part('year', sale_order.date_sale_close)  
                  ) as total_quotation_saleorder,
                  (
                    select count(*) from stock_picking sp
                  where stock_journal_id = 1 and state = 'done' and sp.create_uid = ru.id
                  and date_part('month',now()) = date_part('month', sp.create_date)
                         and date_part('year',now()) = date_part('year', sp.create_date)  
                  ) as total_picking_pc,
                  (
                    select count(*) from stock_picking sp
                  where stock_journal_id = 2 and state = 'done' and sp.create_uid = ru.id
                  and date_part('month',now()) = date_part('month', sp.create_date)
                         and date_part('year',now()) = date_part('year', sp.create_date)  
                  ) as total_picking_ds,
                  (
                    select count(*) from stock_picking sp
                  where stock_journal_id = 3 and state = 'done' and sp.create_uid = ru.id
                  and date_part('month',now()) = date_part('month', sp.create_date)
                         and date_part('year',now()) = date_part('year', sp.create_date)  
                  ) as total_picking_rp,
                  (
                    select count(*) from stock_picking sp
                  where stock_journal_id = 4 and state = 'done' and sp.create_uid = ru.id
                  and date_part('month',now()) = date_part('month', sp.create_date)
                         and date_part('year',now()) = date_part('year', sp.create_date)  
                  ) as total_picking_mp,
                  (
                    select count(*) from stock_picking sp
                  where stock_journal_id = 5 and state = 'done' and sp.create_uid = ru.id
                  and date_part('month',now()) = date_part('month', sp.create_date)
                         and date_part('year',now()) = date_part('year', sp.create_date)  
                  ) as total_picking_fr
                from 
                  res_users ru
                left join res_partner rp on ru.partner_id = rp.id
                where ru.active = true and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                   signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
                order by rp.name      
        )    
        """)
        
class ineco_sale_summary5(osv.osv):
    _name = 'ineco.sale.summary5'
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'nickname': fields.char('Nick Name', size=32),
        'so2': fields.integer('SO',),
        'mo2': fields.integer('MO',),
        'total_customer': fields.integer('Total',),
        'total_customer_company': fields.integer('Company',),
        'total_customer_new': fields.integer('New',),
        'logcall_inbound': fields.integer('In',),
        'logcall_outbound': fields.integer('Out',),
        'logcall_visit': fields.integer('Visit',),
        'total_quotation': fields.integer('QO',),
        'total_quotation_saleorder': fields.integer('SO',),
        'total_picking_pc': fields.integer('PC',),
        'total_picking_ds': fields.integer('DS',),
        'total_picking_rp': fields.integer('PR',),
        'total_picking_mp': fields.integer('PM',),
        'total_picking_fr': fields.integer('PF',),
    }     
    
    def init(self, cr):

        """
            CRM Lead Report
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'ineco_sale_summary5')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_summary5 AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_summary5_query from ineco_sale_summary5_query

                            ) as a
                    ) b
                ) c
            )""")        
        
class ineco_sale_qty_amount_temp(osv.osv):
    _name = "ineco.sale.qty.amount.temp"
    _auto = False
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_qty_amount_query')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_qty_amount_query AS (
                select
                    ru.id as user_id,
                    '1. SO' as type,
                    (select coalesce(count(*),0) from sale_order so 
                                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.date_sale_close)
                             and date_part('year',now()) = date_part('year',so.date_sale_close)
                                         and so.state not in ('cancel','draft') ) as qty,
                    (select coalesce(sum(amount_untaxed),0.00) from sale_order so 
                                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.date_sale_close)
                             and date_part('year',now()) = date_part('year',so.date_sale_close)
                                         and so.state not in ('draft', 'cancel') ) as amount,
                    (select coalesce(count(*),0) from sale_order so 
                                   where user_id = ru.id 
                             and date_part('year',now()) = date_part('year',so.date_sale_close)
                                         and so.state not in ('draft','cancel') ) as ytd_qty,
                    (select coalesce(sum(amount_untaxed),0.00) from sale_order so 
                                   where user_id = ru.id 
                             and date_part('year',now()) = date_part('year',so.date_sale_close)
                                         and so.state not in ('draft','cancel') ) as ytd_amount
                from 
                    res_users ru
                left join res_partner rp on ru.partner_id = rp.id
                where ru.active = true and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'                
                union
                select
                    ru.id as user_id,
                    '2. MO' as type,
                    (select coalesce(count(*),0) from sale_order so 
                                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.garment_order_date)
                             and date_part('year',now()) = date_part('year',so.garment_order_date)
                                         and so.state <> 'cancel') as qty,
                    (select coalesce(sum(amount_untaxed),0.00) from sale_order so 
                                   where user_id = ru.id and date_part('month',now()) = date_part('month',so.garment_order_date)
                             and date_part('year',now()) = date_part('year',so.garment_order_date)
                                         and so.state <> 'cancel') as amount,
                    (select coalesce(count(*),0) from sale_order so 
                                   where user_id = ru.id 
                             and date_part('year',now()) = date_part('year',so.garment_order_date)
                                         and so.state <> 'cancel') as ytd_qty,
                    (select coalesce(sum(amount_untaxed),0.00) from sale_order so 
                                   where user_id = ru.id 
                             and date_part('year',now()) = date_part('year',so.garment_order_date)
                                         and so.state <> 'cancel') as ytd_amount
                from 
                    res_users ru
                left join res_partner rp on ru.partner_id = rp.id
                where ru.active = true and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
                    
                order by user_id, type      
            )               
            """)
    
class ineco_sale_qty_amount(osv.osv):
    _name = 'ineco.sale.qty.amount'
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'type': fields.char('Type',size=32),
        'qty': fields.integer('Qty',),
        'amount': fields.integer('Amount',),
        'ytd_qty': fields.integer('Year Qty',),
        'ytd_amount': fields.integer('Year Amount',),
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_qty_amount')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_qty_amount AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_qty_amount_query from ineco_sale_qty_amount_query
                            ) as a
                    ) b
                ) c
            )""")     
        
class ineco_sale_qty_customer_temp(osv.osv):
    _name = "ineco.sale.qty.customer.temp"
    _auto = False
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_qty_customer_query')
        cr.execute("""
        CREATE OR REPLACE VIEW ineco_sale_qty_customer_query AS (        
select 
  ru.id as user_id,
  '1. New' as type,
  (select coalesce(count(*),0) from res_partner 
                    where user_id = ru.id and date_part('month',now()) = date_part('month', res_partner.create_date)
                        and date_part('year',now()) = date_part('year', res_partner.create_date)
  ) as customer_total 
from 
    res_users ru
    left join res_partner rp on ru.partner_id = rp.id
where ru.active = true and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
union
select 
  ru.id as user_id,
  '3. Total' as type,
  (select count(*) from res_partner where user_id = ru.id and active = true) as customer_total 
from 
    res_users ru
    left join res_partner rp on ru.partner_id = rp.id
where ru.active = true and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
union
select 
  ru.id as user_id,
  '2. Company' as type,
  (select count(*) from res_partner where user_id = ru.id and active = true and is_company = true) as customer_total 
from 
    res_users ru
    left join res_partner rp on ru.partner_id = rp.id 
where ru.active = true and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'

order by user_id, type        
           )
        """)
        
class ineco_sale_qty_customer(osv.osv):
    _name = "ineco.sale.qty.customer"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'type': fields.char('Type',size=32),
        'customer_total': fields.integer('Quantity',),        
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_qty_customer')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_qty_customer AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_qty_customer_query from ineco_sale_qty_customer_query
                            ) as a
                    ) b
                ) c
        )""")

class ineco_sale_mytop_opportunity_temp(osv.osv):
    _name = "ineco.sale.mytop.opportunity.temp"
    _auto = False
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_mytop_opportunity_temp')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_mytop_opportunity_temp AS (
                select 
                  cl.user_id, 
                  cl.partner_id, 
                  stage_id, 
                  planned_revenue, 
                  cl.last_date_count, 
                  rp.last_date_count as last_contact_date 
                from crm_lead cl
                left join res_users ru on ru.id = user_id
                left join res_partner rp on rp.id = cl.partner_id
                where 
                    cl.type = 'opportunity' and ru.active = true
                    and cl.state not in ('done','cancel')            
        )""")

#                select user_id, cl.partner_id, stage_id, planned_revenue, last_date_count, last_contact_date 
#                from crm_lead cl
#                left join res_users ru on ru.id = user_id
#                where type = 'opportunity' and ru.active = true
#                  and state not in ('done','cancel')                        

class ineco_sale_mytop_opportunity(osv.osv):
    _name = "ineco.sale.mytop.opportunity"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'partner_id': fields.many2one('res.partner','Customer'),
        'stage_id': fields.many2one('crm.case.stage','Stage'),
        'planned_revenue': fields.integer('Revenue',),        
        'last_date_count': fields.integer('Age',), 
        'last_contact_date': fields.integer('Update',), 
    }
    _order = 'planned_revenue desc'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_mytop_opportunity')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_mytop_opportunity AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_mytop_opportunity_temp from ineco_sale_mytop_opportunity_temp
                            ) as a
                    ) b
                ) c
        )""")
    
class ineco_sale_all_opportunity(osv.osv):
    _name = "ineco.sale.all.opportunity"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'partner_id': fields.many2one('res.partner','Customer'),
        'stage_id': fields.many2one('crm.case.stage','Stage'),
        'planned_revenue': fields.integer('Revenue',),        
        'last_date_count': fields.integer('Age',), 
        'last_contact_date': fields.integer('Update',), 
        'cost_opportunity': fields.float('Cost'),
    }
    _order = 'user_id'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_all_opportunity')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_all_opportunity AS
                select t1.id, t1.user_id, t1.partner_id, stage_id, planned_revenue, t1.last_date_count, 
                       rp.last_date_count as last_contact_date,
               coalesce((select
              sum(sp2.shiping_cost) +
              (select coalesce( sum(ipc.cost * ipc.quantity), 0.00) from ineco_picking_cost ipc
               join stock_picking sp3 on sp3.id = ipc.picking_id
               where sp3.opportunity_id = cl2.id) +
              (select coalesce(sum(icc.quantity * icc.cost), 0.00) from ineco_crm_cost icc
               join crm_lead cl on cl.id = icc.lead_id
               where cl.id = cl2.id) as cost_opportunity
            from crm_lead cl2
            left join stock_picking sp2 on sp2.opportunity_id = cl2.id
            where sp2.state <> 'cancel' and cl2.id = t1.id
            group by cl2.id),0.00) as cost_opportunity                               
                from crm_lead t1
            left join res_partner rp on t1.partner_id = rp.id
                left join res_users ru on t1.user_id = ru.id
                where (t1.user_id, t1.partner_id, planned_revenue) in
                  (select user_id, partner_id, planned_revenue from crm_lead b
                   where b.user_id = t1.user_id
                     and b.type = 'opportunity'
                     and b.state not in ('done','cancel')
                   order by planned_revenue desc limit 50)
                   and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
                   and t1.state not in ('done','cancel') and ru.active = true
                order by user_id, planned_revenue desc;      
        """)
        
class ineco_sale_fix_temp(osv.osv):
    _name = "ineco.sale.fix.temp"
    _auto = False

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_fix_temp')
        cr.execute("""
            create or replace view ineco_sale_fix_temp as 
            select 
              sp.id as property_id,
              slp.name as name,
              sol.product_id,
              sol.price_unit,
              sol.product_uom_qty,
              sol.product_uom,
              so.id as order_id,
              so.garment_order_no,
              so.note,
              so.date_order,
              so.garment_order_date,
              so.partner_id
            from sale_line_property slp
            join sale_property sp on slp.property_id = sp.id
            join sale_order_line sol on slp.sale_line_id = sol.id
            join sale_order so on sol.order_id = so.id
            join product_product pp on pp.id = sol.product_id
            join product_template pt on pt.id = pp.product_tmpl_id
            where so.state not in ('draft','cancel') 
              and (sp.name like '%ซ่อม%' or sp.name like '%แผนก   %')
              and so.shop_id = 2
          """)
        
class ineco_sale_fix(osv.osv):
    _name = "ineco.sale.fix"
    _auto = False
    _columns = {
        'property_id': fields.many2one('sale.property','Property',readonly=True),
        'name': fields.char('Description',size=254,readonly=True),
        'product_id': fields.many2one('product.product','Product',readonly=True),
        'price_unit': fields.float('Price Unit',readonly=True),
        'product_uom_qty': fields.float('Quantity',readonly=True),
        'product_uom': fields.many2one('product.uom','UOM',readonly=True),
        'order_id': fields.many2one('sale.order','Sale Order', readonly=True),
        'garment_order_no': fields.char('MO No', size=64, readonly=True),
        'note': fields.text('Note',readonly=True),
        'date_order': fields.date('Date Order',readonly=True),
        'garment_order_date': fields.date('Date Mo', readonly=True),
        'partner_id': fields.many2one('res.partner','Customer',readonly=True),
    }
    _order = 'garment_order_no desc'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_fix')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_fix AS (
                select id, (a[id]).*
                from (
                    select a, generate_series(1, array_upper(a,1)) as id
                        from (
                            select array (
                                select ineco_sale_fix_temp from ineco_sale_fix_temp
                            ) as a
                    ) b
                ) c
        )""")
        
        
class ineco_sale_lose_opportunity(osv.osv):
    _name = "ineco.sale.lose.opportunity"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'partner_id': fields.many2one('res.partner','Customer'),
        'stage_id': fields.many2one('crm.case.stage','Stage'),
        'planned_revenue': fields.integer('Revenue',),        
        'last_date_count': fields.integer('Age',), 
        'last_contact_date': fields.integer('Update',), 
        'cost_opportunity': fields.float('Cost'),
    }
    _order = 'user_id'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_lose_opportunity')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_lose_opportunity AS
                select t1.id, t1.user_id, t1.partner_id, stage_id, planned_revenue, extract(days from date_lose - t1.create_date) as last_date_count, 
                       rp.last_date_count as last_contact_date,
               coalesce((select
              sum(sp2.shiping_cost) +
              (select coalesce( sum(ipc.cost * ipc.quantity), 0.00) from ineco_picking_cost ipc
               join stock_picking sp3 on sp3.id = ipc.picking_id
               where sp3.opportunity_id = cl2.id) +
              (select coalesce(sum(icc.quantity * icc.cost), 0.00) from ineco_crm_cost icc
               join crm_lead cl on cl.id = icc.lead_id
               where cl.id = cl2.id) as cost_opportunity
            from crm_lead cl2
            left join stock_picking sp2 on sp2.opportunity_id = cl2.id
            where sp2.state <> 'cancel' and cl2.id = t1.id
            group by cl2.id),0.00) as cost_opportunity                               
                from crm_lead t1
            left join res_partner rp on t1.partner_id = rp.id
                left join res_users ru on t1.user_id = ru.id
                where (t1.user_id, t1.partner_id, planned_revenue) in
                  (select user_id, partner_id, planned_revenue from crm_lead b
                   where b.user_id = t1.user_id
                     and b.type = 'opportunity'
                     and b.state in ('cancel')
              and extract(year from b.date_lose) = extract(year from now())
              and extract(month from b.date_lose) = extract(month from now())
                   order by planned_revenue desc limit 200)
                   and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
                   and t1.state in ('cancel') 
                   and ru.active = true
               and extract(year from t1.date_lose) = extract(year from now())
               and extract(month from t1.date_lose) = extract(month from now())
                order by user_id, planned_revenue desc;       
        """)
        
class ineco_sale_lose_opportunity_month1(osv.osv):
    _name = "ineco.sale.lose.opportunity.month1"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'partner_id': fields.many2one('res.partner','Customer'),
        'stage_id': fields.many2one('crm.case.stage','Stage'),
        'planned_revenue': fields.integer('Revenue',),        
        'last_date_count': fields.integer('Age',), 
        'last_contact_date': fields.integer('Update',), 
        'cost_opportunity': fields.float('Cost'),
    }
    _order = 'user_id'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_lose_opportunity_month1')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_lose_opportunity_month1 AS
                select t1.id, t1.user_id, t1.partner_id, stage_id, planned_revenue, extract(days from date_lose - t1.create_date) as last_date_count, 
                       rp.last_date_count as last_contact_date,
               coalesce((select
              sum(sp2.shiping_cost) +
              (select coalesce( sum(ipc.cost * ipc.quantity), 0.00) from ineco_picking_cost ipc
               join stock_picking sp3 on sp3.id = ipc.picking_id
               where sp3.opportunity_id = cl2.id) +
              (select coalesce(sum(icc.quantity * icc.cost), 0.00) from ineco_crm_cost icc
               join crm_lead cl on cl.id = icc.lead_id
               where cl.id = cl2.id) as cost_opportunity
            from crm_lead cl2
            left join stock_picking sp2 on sp2.opportunity_id = cl2.id
            where sp2.state <> 'cancel' and cl2.id = t1.id
            group by cl2.id),0.00) as cost_opportunity                               
                from crm_lead t1
            left join res_partner rp on t1.partner_id = rp.id
                left join res_users ru on t1.user_id = ru.id
                where (t1.user_id, t1.partner_id, planned_revenue) in
                  (select user_id, partner_id, planned_revenue from crm_lead b
                   where b.user_id = t1.user_id
                     and b.type = 'opportunity'
                     and b.state in ('cancel')
                     and b.date_lose between cast(date_trunc('month', current_date) as date) - interval '1 months' and cast(date_trunc('month', current_date) as date) - interval '1 days'
                   order by planned_revenue desc limit 200)
                   and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
                   and t1.state in ('cancel') 
                   and ru.active = true
                   and t1.date_lose between cast(date_trunc('month', current_date) as date) - interval '1 months' and cast(date_trunc('month', current_date) as date) - interval '1 days'
                order by user_id, planned_revenue desc;            
        """)     
        
class ineco_sale_lose_opportunity_month3(osv.osv):
    _name = "ineco.sale.lose.opportunity.month3"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'partner_id': fields.many2one('res.partner','Customer'),
        'stage_id': fields.many2one('crm.case.stage','Stage'),
        'planned_revenue': fields.integer('Revenue',),        
        'last_date_count': fields.integer('Age',), 
        'last_contact_date': fields.integer('Update',), 
        'cost_opportunity': fields.float('Cost'),
    }
    _order = 'user_id'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_lose_opportunity_month3')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_lose_opportunity_month3 AS
                select t1.id, t1.user_id, t1.partner_id, stage_id, planned_revenue, extract(days from date_lose - t1.create_date) as last_date_count, 
                       rp.last_date_count as last_contact_date,
               coalesce((select
              sum(sp2.shiping_cost) +
              (select coalesce( sum(ipc.cost * ipc.quantity), 0.00) from ineco_picking_cost ipc
               join stock_picking sp3 on sp3.id = ipc.picking_id
               where sp3.opportunity_id = cl2.id) +
              (select coalesce(sum(icc.quantity * icc.cost), 0.00) from ineco_crm_cost icc
               join crm_lead cl on cl.id = icc.lead_id
               where cl.id = cl2.id) as cost_opportunity
            from crm_lead cl2
            left join stock_picking sp2 on sp2.opportunity_id = cl2.id
            where sp2.state <> 'cancel' and cl2.id = t1.id
            group by cl2.id),0.00) as cost_opportunity                               
                from crm_lead t1
            left join res_partner rp on rp.id = t1.partner_id
                left join res_users ru on t1.user_id = ru.id
                where (t1.user_id, t1.partner_id, planned_revenue) in
                  (select user_id, partner_id, planned_revenue from crm_lead b
                   where b.user_id = t1.user_id
                     and b.type = 'opportunity'
                     and b.state in ('cancel')
                     and b.date_lose between cast(date_trunc('month', current_date) as date) - interval '3 months' and cast(date_trunc('month', current_date) as date) - interval '1 months'
                   order by planned_revenue desc limit 200)
                   and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
                   and t1.state in ('cancel') 
                   and ru.active = true
                   and t1.date_lose between cast(date_trunc('month', current_date) as date) - interval '3 months' and cast(date_trunc('month', current_date) as date) - interval '1 months'
                order by user_id, planned_revenue desc;            
        """)              

class ineco_sale_lose_opportunity_month6(osv.osv):
    _name = "ineco.sale.lose.opportunity.month6"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Sale'),
        'partner_id': fields.many2one('res.partner','Customer'),
        'stage_id': fields.many2one('crm.case.stage','Stage'),
        'planned_revenue': fields.integer('Revenue',),        
        'last_date_count': fields.integer('Age',), 
        'last_contact_date': fields.integer('Update',), 
        'cost_opportunity': fields.float('Cost'),
    }
    _order = 'user_id'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_lose_opportunity_month6')
        cr.execute("""
            CREATE OR REPLACE VIEW ineco_sale_lose_opportunity_month6 AS
                select t1.id, t1.user_id, t1.partner_id, stage_id, planned_revenue, extract(days from date_lose - t1.create_date) as last_date_count, 
                       rp.last_date_count as last_contact_date,
               coalesce((select
              sum(sp2.shiping_cost) +
              (select coalesce( sum(ipc.cost * ipc.quantity), 0.00) from ineco_picking_cost ipc
               join stock_picking sp3 on sp3.id = ipc.picking_id
               where sp3.opportunity_id = cl2.id) +
              (select coalesce(sum(icc.quantity * icc.cost), 0.00) from ineco_crm_cost icc
               join crm_lead cl on cl.id = icc.lead_id
               where cl.id = cl2.id) as cost_opportunity
            from crm_lead cl2
            left join stock_picking sp2 on sp2.opportunity_id = cl2.id
            where sp2.state <> 'cancel' and cl2.id = t1.id
            group by cl2.id),0.00) as cost_opportunity                               
                from crm_lead t1
                left join res_partner rp on rp.id = t1.partner_id
                left join res_users ru on t1.user_id = ru.id
                where (t1.user_id, t1.partner_id, planned_revenue) in
                  (select user_id, partner_id, planned_revenue from crm_lead b
                   where b.user_id = t1.user_id
                     and b.type = 'opportunity'
                     and b.state in ('cancel')
                     and b.date_lose between cast(date_trunc('month', current_date) as date) - interval '6 months' and cast(date_trunc('month', current_date) as date) - interval '3 months'
                   order by planned_revenue desc limit 200)
                   and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                    signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
                   and t1.state in ('cancel') 
                   and ru.active = true
                   and t1.date_lose between cast(date_trunc('month', current_date) as date) - interval '6 months' and cast(date_trunc('month', current_date) as date) - interval '3 months'
                order by user_id, planned_revenue desc;         
        """)              
        