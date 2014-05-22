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
import time
# from operator import itemgetter
# from itertools import groupby

from openerp.osv import fields, osv
#from tools.translate import _
from openerp import netsvc
#import tools
#from tools import float_compare
import openerp.addons.decimal_precision as dp
# import logging
# _logger = logging.getLogger(__name__)

class ineco_delivery_objective(osv.osv):
    _name = 'ineco.delivery.objective'
    _description = "Objective to delivery something"
    _columns = {
        'name': fields.char('Description', size=128),
    }
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Description must be unique !')
    ]

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
        'note': fields.char('Note', size=32,),
        'product_weight': fields.float('Weight', digits_compute=dp.get_precision('Product Unit of Measure')),
    }
    
class stock_picking_out(osv.osv):
    
    def _get_quantity(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for stock in self.browse(cr, uid, ids, context=context):
            res[stock.id] = 0.0
            #res[stock.id] = {'quantity': 0.0}
            sql = "select sum(product_qty) from stock_move where picking_id = %s"
            cr.execute(sql % stock.id)
            product_qty =  cr.fetchone()[0] or 0.0
            res[stock.id] = product_qty
        return res    

    def _get_picking(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            result[line.picking_id.id] = True
        return result.keys()
        
    _inherit = "stock.picking.out"
    _columns = {
        'delivery_type_id': fields.many2one('ineco.delivery.type','Delivery Type'),
        'shiping_cost': fields.float('Shipping Cost', digits_compute=dp.get_precision('Account')),
        'batch_no': fields.integer('Batch No'),
        'ineco_date_delivery': fields.date('Actual Delivery Date'),
        'garment_order_no': fields.related('sale_id', 'garment_order_no', type="char", string="Garment No", readonly=True),
        'date_delivery': fields.related('sale_id', 'date_delivery', type="date", string="Delivery Date", readonly=True),
        'picking_transfer_id': fields.many2one('stock.picking','Transfers Doc'),
        'quantity': fields.function(_get_quantity, 
                                    digits_compute=dp.get_precision('Product Unit of Measure'), 
                                    string='Quantity',
                                    type="float",
            #store={
            #    'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 10),
            #    'stock.move': (_get_picking, ['product_qty'], 10),
            #},
            #multi='sums', help="Summary Product."
            ),
        'opportunity_id': fields.many2one('crm.lead', 'Opportunity',domain=[('type','=','opportunity')]),
        'objective_id': fields.many2one('ineco.delivery.objective', 'Objective')
    }
        
    
class stock_picking(osv.osv):

    def _get_quantity(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for stock in self.browse(cr, uid, ids, context=context):
            res[stock.id] = {'quantity': 0.0}
            sql = "select sum(product_qty) from stock_move where picking_id = %s"
            cr.execute(sql % stock.id)
            product_qty =  cr.fetchone()[0] or 0.0
            res[stock.id]['quantity'] = product_qty
        return res    
    
    def _get_productions(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for stock in self.browse(cr, uid, ids, context=context):
            #res[stock.id] = {'production_list': False}
            production_list = ""
            for production in stock.production_ids:
                production_list = production_list + production.name + ", "
            #res[stock.id]['production_list'] = production_list
            res[stock.id] = production_list
        return res

    def _get_picking(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            result[line.picking_id.id] = True
        return result.keys()
    
    _inherit = "stock.picking"
    _columns = {
        'order_color': fields.char('Color',size=64),
        'order_type': fields.char('Type', size=64),
        'order_weight': fields.char('Weight', size=64),
        'picking_note_id': fields.many2one('ineco.picking.note', 'Picking Note',),
        'quantity': fields.function(_get_quantity, 
                                    digits_compute=dp.get_precision('Product Unit of Measure'), 
                                    string='Quantity',
                                    type="float",
            store={
                'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['move_lines'], 10),
                'stock.move': (_get_picking, ['product_qty'], 10),
            },
            multi='sums', help="Summary Product."),
        'production_list': fields.function(_get_productions,
                                           string="Production List",
                                           type="char",
            store={
                'stock.picking': (lambda self, cr, uid, ids, c={}: ids, ['production_ids'], 10),
            }, ),
    }

    def onchange_note_id(self, cr, uid, ids, note_id=False, context=None):
        note_obj = self.pool.get('ineco.picking.note')
        if not note_id:
            return {'value':{}}
        val = {}
        note = note_obj.read(cr, uid, note_id, ['note'],context=context)
        val['note'] = note.get('note', False) and note.get('note') or False
        return {'value': val}

#     def name_get(self, cr, uid, ids, context=None):
#         if not ids:
#             return []
#         reads = self.read(cr, uid, ids, ['name'], context)
#         res = []
#         for record in reads:
#             name = record['name']
#             res.append((record['id'], name))
#         return res
    
    def action_done(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        picking_obj = self.pool.get("stock.picking")
        journal_obj = self.pool.get('stock.journal')
        journal_ids = journal_obj.search(cr, uid, [('transfer_fg','=',True)])
        location_production_id = 7
        location_stock_id = 12
        data = self.browse(cr, uid, ids)[0]
        data_out = self.pool.get('stock.picking.out').browse(cr, uid, ids)[0]
        if data_out.picking_transfer_id:
            picking_obj.action_done_draft(cr, uid, [data_out.picking_transfer_id.id])
            wf_service.trg_validate(uid, 'stock.picking', data_out.picking_transfer_id.id, 'button_cancel', cr)
        production_obj = self.pool.get('mrp.production')
        production = production_obj.search(cr, uid, [('origin','ilike',data.origin)])
        new_picking = False
        if production:
            new_picking = picking_obj.copy(cr, uid, data.id,
                                {
                                    'name': '/',
                                    'type': 'internal',
                                    'stock_journal_id': journal_ids and journal_ids[0] or False,
                                    'state':'draft',

                                })
            new_data = self.browse(cr, uid, [new_picking])[0]
            for move in new_data.move_lines:
                move.write({'location_id': location_production_id, 
                            'location_dest_id': location_stock_id,
                            'state': 'done' })
            new_data.write({'state':'done'})

        self.pool.get('stock.picking.out').write(cr, uid, ids, {'ineco_date_delivery': time.strftime('%Y-%m-%d'),
                                                                'picking_transfer_id': new_picking or False})
        result = super(stock_picking, self).action_done(cr, uid, ids, context)
        return result 
    
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

class stock_move_split_lines_exist(osv.osv_memory):
    _inherit = "stock.move.split.lines"
    _columns = {
        'product_weight': fields.float('Weight', digits_compute=dp.get_precision('Product Unit of Measure')),
    }
    
class split_in_production_lot(osv.osv_memory):
    _inherit = "stock.move.split"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(split_in_production_lot, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            move = self.pool.get('stock.move').browse(cr, uid, context['active_id'], context=context)
            if 'product_id' in fields:
                res.update({'product_id': move.product_id.id})
            if 'product_uom' in fields:
                res.update({'product_uom': move.product_uom.id})
            if 'qty' in fields:
                res.update({'qty': move.product_qty})
            if 'use_exist' in fields:
                res.update({'use_exist': (move.picking_id and move.picking_id.type=='out' and True) or False})
            if 'location_id' in fields:
                res.update({'location_id': move.location_id.id})
            if 'product_weight' in fields:
                res.update({'product_weight': move.product_weight})
        return res
    
    def split(self, cr, uid, ids, move_ids, context=None):
        """ To split stock moves into serial numbers

        :param move_ids: the ID or list of IDs of stock move we want to split
        """
        if context is None:
            context = {}
        assert context.get('active_model') == 'stock.move',\
             'Incorrect use of the stock move split wizard'
        inventory_id = context.get('inventory_id', False)
        prodlot_obj = self.pool.get('stock.production.lot')
        inventory_obj = self.pool.get('stock.inventory')
        move_obj = self.pool.get('stock.move')
        new_move = []
        for data in self.browse(cr, uid, ids, context=context):
            for move in move_obj.browse(cr, uid, move_ids, context=context):
                move_qty = move.product_qty
                quantity_rest = move.product_qty
                uos_qty_rest = move.product_uos_qty
                new_move = []
                if data.use_exist:
                    lines = [l for l in data.line_exist_ids if l]
                else:
                    lines = [l for l in data.line_ids if l]
                total_move_qty = 0.0
                for line in lines:
                    quantity = line.quantity
                    total_move_qty += quantity
                    if total_move_qty > move_qty:
                        raise osv.except_osv(_('Processing Error!'), _('Serial number quantity %d of %s is larger than available quantity (%d)!') \
                                % (total_move_qty, move.product_id.name, move_qty))
                    if quantity <= 0 or move_qty == 0:
                        continue
                    quantity_rest -= quantity
                    uos_qty = quantity / move_qty * move.product_uos_qty
                    uos_qty_rest = quantity_rest / move_qty * move.product_uos_qty
                    if quantity_rest < 0:
                        quantity_rest = quantity
                        self.pool.get('stock.move').log(cr, uid, move.id, _('Unable to assign all lots to this move!'))
                        return False
                    default_val = {
                        'product_qty': quantity,
                        'product_uos_qty': uos_qty,
                        'state': move.state
                    }
                    if quantity_rest > 0:
                        current_move = move_obj.copy(cr, uid, move.id, default_val, context=context)
                        if inventory_id and current_move:
                            inventory_obj.write(cr, uid, inventory_id, {'move_ids': [(4, current_move)]}, context=context)
                        new_move.append(current_move)

                    if quantity_rest == 0:
                        current_move = move.id
                    prodlot_id = False
                    if data.use_exist:
                        prodlot_id = line.prodlot_id.id
                    if not prodlot_id:
                        prodlot_id = prodlot_obj.create(cr, uid, {
                            'name': line.name,
                            'product_id': move.product_id.id,
                            'ref': move.prodlot_id.ref or False},
                        context=context)

                    move_obj.write(cr, uid, [current_move], {'prodlot_id': prodlot_id, 'state':move.state, 'product_weight':line.product_weight or 0.0})

                    update_val = {}
                    if quantity_rest > 0:
                        update_val['product_qty'] = quantity_rest
                        update_val['product_uos_qty'] = uos_qty_rest
                        update_val['state'] = move.state
                        move_obj.write(cr, uid, [move.id], update_val)

        return new_move
    
class ineco_picking_note(osv.osv):
    _name = 'ineco.picking.note'
    _columns = {
        'name': fields.char('description', size=128, reqruied=True),
        'note': fields.text('Note', required=True),
        'seq': fields.integer('Sequence')
    }
    _order = 'seq'
    _defaults = {
        'seq': 0,
    }
    
class stock_journal(osv.osv):
    _inherit = 'stock.journal'
    _columns = {
        'transfer_fg': fields.boolean('Is Transfer FG'),
    }

