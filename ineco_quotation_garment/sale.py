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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
#import pooler
from openerp.osv import fields, osv
#from tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc


class sale_property(osv.osv):
    _name = 'sale.property'
    _description = 'Property of Sale Line'
    _columns = {
        'name': fields.char('Description',size=64,required=True),
        'active': fields.boolean('Active'),
        'seq': fields.integer('Sequence',required=True),
    }
    _defaults = {
        'active': True,
        'seq': 0,
    }
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Description must be unique !')
    ]
    
class sale_gender(osv.osv):
    _name = 'sale.gender'
    _description = 'Gender of Sale'
    _columns = {
        'name': fields.char('Description',size=64,required=True),
        'code': fields.char('Code', size=10),
    }
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Description must be unique !')
    ]    

class sale_color(osv.osv):
    _name = 'sale.color'
    _description = 'Color of Product Sale'
    _columns = {
        'name': fields.char('Description',size=64,required=True)
    }
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Description must be unique !')
    ] 
    _order = 'name'
    
class sale_size(osv.osv):
    _name = 'sale.size'
    _description = 'Size of Product Sale'
    _columns = {
        'name': fields.char('Description',size=64,required=True),
        'seq': fields.integer('Sequence'),
        'code': fields.char('Code',size=10),
    }
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Description must be unique !')
    ]     
    _order = 'name desc'

class sale_style(osv.osv):
    _name = 'sale.style'
    _description = 'Style of Product Sale'
    _columns = {
        'name': fields.char('Description',size=64,required=True)
    }
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Description must be unique !')
    ] 
    _order = 'name'
    
class sale_line_property(osv.osv):

    _name = 'sale.line.property'
    _description = 'Property of Sale Line'
    _columns = {
        'name': fields.text('Description', required=True),
        'seq': fields.integer('Sequence'),
        'property_id': fields.many2one('sale.property', 'Property',  required=True, ondelete='cascade'),
        'sale_line_id': fields.many2one('sale.order.line', 'Order Line', ondelete='cascade'),
    }
    _sql_constraints = [
        ('name_property_unique', 'unique (name, property_id, sale_line_id)', 'Description and property must be unique !')
    ]
    _order = 'name, seq'
    
class sale_line_property_other(osv.osv):
    _name = 'sale.line.property.other'
    _description = "Color, Gender and Sizing Line"
    _columns = {
        'name': fields.text('Description', required=True),
        'seq': fields.integer('Sequence'),
        'color_id': fields.many2one('sale.color', 'Color' ),
        'gender_id': fields.many2one('sale.gender', 'Gender', required=True ),
        'size_id': fields.many2one('sale.size', 'Size'),
        'quantity': fields.integer('Quantity', required=True),
        'sale_line_id': fields.many2one('sale.order.line', 'Order Line', ondelete='cascade'),
        'style_id': fields.many2one('sale.style', 'Style'),
        'note': fields.char('Note', size=32, required=True),
    }
    _defaults = {
        'name': '...',
        'note': '-',
    }
#     _sql_constraints = [
#         ('name_property_unique', 'unique (color_id, gender_id, size_id, sale_line_id, style_id)', 'Data must be unique !')
#     ]
    _order = 'color_id, gender_id, size_id'
    
class sale_order_line(osv.osv):
    
    def _get_order_line(self, cr, uid, ids, context=None):
        result = {}
        for data in self.pool.get('sale.order').browse(cr, uid, ids, context=context):
            for line in data.order_line:
                result[line.id] = True
        return result.keys()
    
    _inherit = 'sale.order.line'
    _columns = {
        'name': fields.text('Description', required=True),
        'order_line_property_ids': fields.one2many('sale.line.property', 'sale_line_id', 'Property'),
        'order_line_property_other_ids': fields.one2many('sale.line.property.other', 'sale_line_id', 'Color, Gender and Sizing'),
        'sampling_qty': fields.integer('Sampling Quantity'),
        'garmentorder_date':fields.related('order_id', 'garment_order_date', type='date', 
            store={
                'sale.order.line': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'sale.order': (_get_order_line, ['garment_order_date'], 10),
            }, string='MO Date'),
        'dateorder':fields.related('order_id', 'date_order', type='date', 
            store={
                'sale.order.line': (lambda self, cr, uid, ids, c={}: ids, [], 10),
                'sale.order': (_get_order_line, ['garment_order_date'], 10),
            }, string='Date Order'),      
    }    
    _defaults = {
        'sampling_qty': 0,
    }

#     def create(self, cr, uid, vals, context=None):
#         order_id = vals.get('order_id', False)
#         product_id = vals.get('product_id', False)
#         if order_id and product_id:
#             sql = """
#                 select count(*) as total from sale_order_line sol
#                 join product_product pp on sol.product_id = pp.id
#                 join product_template pt on pp.product_tmpl_id = pt.id
#                 where order_id = %s and pt.type <> 'service'           
#             """
#             cr.execute(sql % order_id)
#             record_count = cr.fetchone()[0] or 0.0
#             product_obj = self.pool.get('product.product').browse(cr, uid, product_id)
#             if record_count >= 1 and product_obj.type in ('consu','product'):
#                 raise osv.except_osv('Product Sale Exceed!', 'Sale line must be 1 product per Sale Order.') 
#         return super(sale_order_line, self).create(cr, uid, vals, context)
    
class sale_order(osv.osv):
    _inherit = 'sale.order'
    _description = 'Add Delivery Date'
    _columns = {
        'date_delivery': fields.date('Delivery Date'),
        'sale_revision': fields.char('Revision', size=32),   
        'sample_order_no': fields.char('Sampling Order No', size=32, readonly=True),
        'garment_order_no': fields.char('Garment Order No', size=32, readonly=True),    
        'sample_order_date': fields.date('Sampling Order Date',),
        'garment_order_date': fields.date('Garment Order Date',),
        'sample_deliver_date': fields.date('Sampling Deliver Date'),
        'cancel_sample_order': fields.boolean('Cancel Sampling Order'),
        'cancel_garment_order': fields.boolean('Cancel Garment Order'),
        'date_sale_close': fields.date('Closed Date'),
        'sample_revision_no': fields.char('Sampling Revision No', size=32,),
        'sample_revision_date': fields.date('Sampling Revision Date',),
        'to_correct': fields.boolean('To Corrected'),
    }
    _defaults = {
        'cancel_sample_order': False,
        'cancel_garment_order': False,
        'to_correct': False,
    }

    def copy(self, cr, uid, ids, default=None, context=None):
        if context is None:
            context = {}
        if default is None:
            default = {}
        default = default.copy()
        if 'change_shop' in context:
            default['sale_revision'] = False
            default['sample_order_no'] = False
            default['garment_order_no'] = False
            default['sample_order_date'] = False
            default['garment_order_date'] = False
            default['sample_deliver_date'] = False
            default['cancel_sample_order'] = False
            default['cancel_garment_order'] = False
            default['date_sale_close'] = False
            default['sample_revision_no'] = False
            default['sample_revision_date'] = False
            default['date_delivery'] = False
            default['date_order'] = time.strftime('%Y-%m-%d')
        return super(sale_order, self).copy(cr, uid, ids, default, context=context)
    
    def action_gen_sampling_no(self, cr, uid, ids, context=None):
        sample_order_no = self.pool.get('ir.sequence').get(cr, uid, 'ineco.sampling.order')
        self.write(cr, uid, ids, {'sample_order_no': sample_order_no, 'sample_order_date': time.strftime('%Y-%m-%d'), 'sample_revision_date': time.strftime('%Y-%m-%d')})
        return True

    def action_gen_garment_no(self, cr, uid, ids, context=None):
        sale_obj = self.browse(cr, uid, ids)[0]
        #Check MRP when exist
        production_obj = self.pool.get('mrp.production')
        production_ids = production_obj.search(cr, uid, [('origin','=',sale_obj.name)])
        garment_order_no = False
        if production_ids:
            garment_order = production_obj.browse(cr, uid, production_ids)[0]
            garment_order_no = garment_order.origin.split('#')[0]
            self.write(cr, uid, ids, {'garment_order_no': garment_order_no, 'garment_order_date': time.strftime('%Y-%m-%d')})
        else:
            if sale_obj.shop_id and sale_obj.shop_id.production_sequence_id:
                garment_order_no = self.pool.get('ir.sequence').get_id(cr, uid, sequence_code_or_id=sale_obj.shop_id.production_sequence_id.id )
            else:
                garment_order_no = self.pool.get('ir.sequence').get(cr, uid, 'ineco.garment.order')
            self.write(cr, uid, ids, {'garment_order_no': garment_order_no, 'garment_order_date': time.strftime('%Y-%m-%d')})
            #Make MO
            company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
            production_obj = self.pool.get('mrp.production')
            #move_obj = self.pool.get('stock.move')
            wf_service = netsvc.LocalService("workflow")
            bom_obj = self.pool.get('mrp.bom')
            #procurement_obj = self.pool.get('procurement.order')
            #res_id = procurement.move_id.id
            #newdate = datetime.strptime(procurement.date_planned, '%Y-%m-%d %H:%M:%S') - relativedelta(days=procurement.product_id.produce_delay or 0.0)
            #newdate = newdate - relativedelta(days=company.manufacturing_lead)
            stock_location_obj = self.pool.get('stock.warehouse').browse(cr, uid, [1])[0]
            seq = 1
            for line in sale_obj.order_line:
                bom_id = False
                bom_ids = bom_obj.search(cr, uid, [('product_id','=',line.product_id.id)])
                if bom_ids:
                    bom_id = bom_ids[0]
                produce_id = production_obj.create(cr, uid, {
                    'origin': sale_obj.name,
                    'product_id': line.product_id.id,
                    'product_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'product_uos_qty': False,
                    'product_uos': False,
                    'location_src_id': stock_location_obj.lot_stock_id.id,
                    'location_dest_id': stock_location_obj.lot_stock_id.id,
                    'bom_id': bom_id,
                    'date_planned': time.strftime('%Y-%m-%d'),
                    'move_prod_id': False,
                    'company_id': company.id,
                    'name': garment_order_no+('#%s' % seq),
                })        
                seq += 1
        return True

    def _prepare_order_picking(self, cr, uid, order, context=None):
        result = super(sale_order, self)._prepare_order_picking(cr, uid, order, context=context)
        result.update({'invoice_state':'2binvoiced', 'delivery_type_id': order.ineco_delivery_type_id.id or False})
        return result
    
    def _prepare_order_line_move_qty(self, cr, uid, order, line, picking_id, date_planned, new_qty, color, gender, size, note=None, context=None):
        location_id = order.shop_id.warehouse_id.lot_stock_id.id
        output_id = order.shop_id.warehouse_id.lot_output_id.id
        return {
            'name': line.name,
            'picking_id': picking_id,
            'product_id': line.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_qty': new_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': new_qty,
            'product_uos': (line.product_uos and line.product_uos.id)\
                    or line.product_uom.id,
            'product_packaging': line.product_packaging.id,
            'partner_id': line.address_allotment_id.id or order.partner_shipping_id.id,
            'location_id': location_id,
            'location_dest_id': output_id,
            'sale_line_id': line.id,
            'tracking_id': False,
            'state': 'draft',
            #'state': 'waiting',
            'company_id': order.company_id.id,
            'price_unit': line.product_id.standard_price or 0.0,
            'size_id': size,
            'color_id': color,
            'gender_id': gender,
            'note': note,
        }

    def _get_date_planned(self, cr, uid, order, line, start_date, context=None):
        #date_planned = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(days=line.delay or 0.0)
        #date_planned = (date_planned - timedelta(days=order.company_id.security_lead)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date_planned = order.date_delivery
        return date_planned

    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):

        sql = """
            select count(*) as total from sale_order_line sol
            join product_product pp on sol.product_id = pp.id
            join product_template pt on pp.product_tmpl_id = pt.id
            where order_id = %s and pt.type <> 'service'           
        """
        cr.execute(sql % order.id)
        record_count = cr.fetchone()[0] or 0.0
        if record_count > 1 :
            raise osv.except_osv('Product Sale Exceed!', 'Sale line must be 1 product per Sale Order.') 
        
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking.out')
        procurement_obj = self.pool.get('procurement.order')
        proc_ids = []

        for line in order_lines:
            #Check when sale line quantity <> production order qty (other tab)
            if len(line.order_line_property_other_ids) > 0:
                other_qty = 0
                for other in line.order_line_property_other_ids:
                    other_qty = other_qty + other.quantity
                if other_qty <> line.product_uom_qty:
                    raise osv.except_osv('Invalid Quantity!', 'Sale line quantity <> production.')
                
            if line.state == 'done':
                continue

            date_planned = self._get_date_planned(cr, uid, order, line, order.date_order, context=context)

            if line.product_id:
                if line.product_id.type in ('product', 'consu'):
                    if not picking_id:
                        picking_id = picking_obj.create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
                    if line.order_line_property_other_ids:
                        for other in line.order_line_property_other_ids:
                            move_id = move_obj.create(cr, uid, self._prepare_order_line_move_qty(cr, 
                                uid, order, line, picking_id, date_planned, other.quantity, 
                                other.color_id and other.color_id.id or False,
                                other.gender_id and other.gender_id.id or False,
                                other.size_id and other.size_id.id or False, other.note or False, context=context))
                    else:
                        move_id = move_obj.create(cr, uid, self._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned, context=context))
                else:
                    # a service has no stock move
                    move_id = False

                proc_id = procurement_obj.create(cr, uid, self._prepare_order_line_procurement(cr, uid, order, line, move_id, date_planned, context=context))
                proc_ids.append(proc_id)
                line.write({'procurement_id': proc_id})
                self.ship_recreate(cr, uid, order, line, move_id, proc_id)

        wf_service = netsvc.LocalService("workflow")
        if picking_id:
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        for proc_id in proc_ids:
            wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)

        val = {}
        if order.state == 'shipping_except':
            val['state'] = 'progress'
            val['shipped'] = False

            if (order.order_policy == 'manual'):
                for line in order.order_line:
                    if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                        val['state'] = 'manual'
                        break
        order.write(val)
        return True

class crm_lead(osv.osv):
    _inherit = 'crm.lead'
    _description = "Cost of CRM on Opportunity"
    _columns = {
        'cost_ids': fields.one2many('ineco.crm.cost','lead_id', 'Costs'),
    }

class ineco_crm_cost(osv.osv):

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.quantity * line.cost
            res[line.id] = price
        return res

    def on_change_costtype(self, cr, uid, ids, cost_type_id, context=None):
        if context==None:
            context={}
        result = 0.0
        cost_type_obj = self.pool.get('ineco.cost.type').browse(cr, uid, cost_type_id)
        if cost_type_obj:
            result = cost_type_obj.cost
        return {'value': {
            'cost': result,
            }
        }

    _name = 'ineco.crm.cost'
    _description = "Cost of CRM Line"
    _columns = {
        'name': fields.char('Description', size=128),
        'lead_id': fields.many2one('crm.lead', 'Opportunity'),
        'cost_type_id': fields.many2one('ineco.cost.type','Cost'),
        'quantity': fields.integer('Quantity', required=True),
        'cost': fields.float('Cost', required=True),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
    }
    
    _defaults = {
        'quantity': 1,
        'cost': 0.0,
    }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: