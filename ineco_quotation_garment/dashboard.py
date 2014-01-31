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
                select user_id, partner_id, stage_id, planned_revenue, last_date_count, last_contact_date from crm_lead where type = 'opportunity'
                  --and date_part('month',now()) = date_part('month',date_closed)
                  --and date_part('year',now()) = date_part('year',date_closed)      
                  and state not in ('done','cancel')          
                --order by user_id, planned_revenue desc            
        )""")

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
    }
    _order = 'user_id'
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'ineco_sale_all_opportunity')
        cr.execute("""
        CREATE OR REPLACE VIEW ineco_sale_all_opportunity AS
            select t1.id, user_id, t1.partner_id, stage_id, planned_revenue, last_date_count, last_contact_date from crm_lead t1
            left join res_users ru on user_id = ru.id
            where (user_id, t1.partner_id, planned_revenue) in
              (select user_id, partner_id, planned_revenue from crm_lead b
               where b.user_id = t1.user_id
                 and b.type = 'opportunity'
                 and b.state not in ('done','cancel')
               order by planned_revenue desc limit 10)
               and ru.id not in (70,71,72,23,16,61,20,1,18,22,21,66,60) and
                signature like '%เจ้าหน้าที่งานฝ่ายขาย%'
               and t1.state not in ('done','cancel')
            order by user_id, planned_revenue desc;      
        """)
        