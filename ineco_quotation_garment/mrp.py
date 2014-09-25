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

#import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

#import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv
#from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
#from openerp.tools import float_compare
#from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools

class ineco_mrp_pattern_component(osv.osv):
    _name = 'ineco.mrp.pattern.component'
    _description = "Pattern Component"
    _columns = {
        'name': fields.char('Description', size=64,),
        'seq': fields.integer('Sequence'),
        'type_id': fields.many2one('ineco.pattern.type','Type',required=True),
        'process1': fields.boolean('Process 1'),
        'process2': fields.boolean('Process 2'),
        'production_id': fields.many2one('mrp.production','Production'),
    }
    _defaults = {
        'name': '...',
        'process1': False,
        'process2': False,
        #'last_updated': time.strftime("%Y-%m-%d %H:%M:%S"),
    }

class mrp_production(osv.osv):

    def _get_late(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        today = datetime.now()
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = {
                'late': True
            }
            if obj.date_plan_start and not obj.date_plan_finish :
                start_date = datetime.strptime(obj.date_plan_start, '%Y-%m-%d %H:%M:%S') + relativedelta(days=3)
                if today > start_date:
                    result[obj.id]['late'] = True
                else:
                    result[obj.id]['late'] = False
         
        return result
    
    _inherit = 'mrp.production'
    _description = 'MRP for Garment'
    _columns = {
        'date_plan_start': fields.datetime('Date Plan Start'),
        'date_plan_finish': fields.datetime('Date Plan Finish'),
        'color_id': fields.many2one('sale.color', 'Color'),
        'gender_id': fields.many2one('sale.gender', 'Gender'),
        'size_id': fields.many2one('sale.size', 'Size'),        
        'note': fields.char('Note', size=32,),
        'sale_order_id': fields.many2one('sale.order','Sale Order'),
        'pattern_id': fields.many2one('ineco.pattern','Pattern'),
        'comment': fields.text('Comment'),
        'bill_no': fields.char('Bill No', size=10),
        'bill_type': fields.char('Material Type', size=64),
        'worker': fields.char('Worker',size=64),
        'bill_weight': fields.float('Bill Weight'),
        'pattern_component_ids': fields.one2many('ineco.mrp.pattern.component','production_id','Components'),
        'is_print': fields.boolean('Print MO'),
        'late': fields.function(_get_late, string="Late", type="boolean", multi="_late"),
        'user_id': fields.related('sale_order_id', 'user_id', type='many2one', relation="res.users", string='Sale', readonly=True),
        'is_planning': fields.boolean('Print Planning'),
    }
    _defaults = {
        'is_print': False,
        'is_planning': False,
    }

    def button_done_draft(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        wf_service = netsvc.LocalService("workflow")
        for doc_id in ids:
            cr.execute("select id from wkf where osv = '"+'mrp.production'+"'")
            wkf_ids = map(lambda x: x[0], cr.fetchall())
            wkf_id = wkf_ids[0]
            cr.execute("select id from wkf_activity where wkf_id = %s and name = 'draft'" % (wkf_id))
            act_ids = map(lambda x: x[0], cr.fetchall())
            act_id = act_ids[0]
            cr.execute('update wkf_instance set state=%s where res_id=%s and res_type=%s', ('active', doc_id, 'mrp.production'))
            cr.execute("update wkf_workitem set state = 'active', act_id = %s where inst_id = (select id from wkf_instance where wkf_id = %s and res_id = %s)", (str(act_id), str(wkf_id), doc_id))    
            self.write(cr, uid, doc_id, {'state':'draft'})
        return True    

    def button_component(self, cr, uid, ids, context=None):
        for id in ids:
            production = self.browse(cr, uid, id)
            if production and production.pattern_id:
                sql = "delete from ineco_mrp_pattern_component where production_id = %s" % production.id
                cr.execute(sql)
                for component in production.pattern_id.component_ids:
                    new_data = {
                        'seq': component.seq,
                        'type_id': component.type_id.id,
                        'production_id': production.id,
                    }
                    self.pool.get('ineco.mrp.pattern.component').create(cr, uid, new_data)
        return True

    def action_compute(self, cr, uid, ids, properties=None, context=None):
        """ Computes bills of material of a product.
        @param properties: List containing dictionaries of properties.
        @return: No. of products.
        """
        if properties is None:
            properties = []
        results = []
        bom_obj = self.pool.get('mrp.bom')
        uom_obj = self.pool.get('product.uom')
        prod_line_obj = self.pool.get('mrp.production.product.line')
        workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')
        for production in self.browse(cr, uid, ids):
            cr.execute('delete from mrp_production_product_line where production_id=%s', (production.id,))
            cr.execute('delete from mrp_production_workcenter_line where production_id=%s', (production.id,))
            bom_point = production.bom_id
            bom_id = production.bom_id.id
            if not bom_point:
                bom_id = bom_obj._bom_find(cr, uid, production.product_id.id, production.product_uom.id, properties)
                if bom_id:
                    bom_point = bom_obj.browse(cr, uid, bom_id)
                    routing_id = bom_point.routing_id.id or False
                    self.write(cr, uid, [production.id], {'bom_id': bom_id, 'routing_id': routing_id})

            if not bom_id:
                raise osv.except_osv(_('Error!'), _("Cannot find a bill of material for this product."))
            factor = uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, bom_point.product_uom.id)
            res = bom_obj._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, properties, routing_id=production.routing_id.id)
            results = res[0]
            results2 = res[1]
            for line in results:
                line['production_id'] = production.id
                prod_line_obj.create(cr, uid, line)
            pattern_ids = self.pool.get('ineco.pattern').search(cr, uid, [('saleorder_id','=',production.sale_order_id.id)])
            pattern_obj = False
            if pattern_ids:
                pattern_obj =  self.pool.get('ineco.pattern').browse(cr, uid, pattern_ids)[0]
            for line in results2:
                if pattern_obj:
                    if line['multiple_component']:
                        line['cycle'] = (int(line['cycle']) or 1.0) * len(pattern_obj.component_ids) or 1.0
                line['production_id'] = production.id
                line['name'] = line['name'] +' : '+production.name
                workcenter_line_obj.create(cr, uid, line)
        return len(results)
 
    
class mrp_routing_workcenter(osv.osv):
    """
    Defines working cycles and hours of a Work Center using routings.
    """
    _inherit = 'mrp.routing.workcenter'
    _columns = {
        'multiple_component': fields.boolean('Multiple Pattern Component'),
    }
    _default = {
        'multiple_component': False,
    }
    
class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'
    _columns = {
        'multiple_component': fields.boolean('Multiple Pattern Component'),
#        'cycle_count': fields.float('Cycle Counts', digits=(16,2)),
        'size_id': fields.related('production_id', 'size_id', type='many2one', relation='sale.size', string='Size', readonly=True),
        'note': fields.related('production_id', 'note', type='char', string='Note', size=100, readonly=True),
        'worker': fields.related('production_id', 'worker', type='char', string='Worker', readonly=True),
    }
    _default = {
#        'cycle_count': 0.0,
        'multiple_component': False,
    }

def rounding(f, r):
    import math
    if not r:
        return f
    return math.ceil(f / r) * r

class mrp_bom(osv.osv):
    _inherit = 'mrp.bom'
    def _bom_explode(self, cr, uid, bom, factor, properties=None, addthis=False, level=0, routing_id=False):
        """ Finds Products and Work Centers for related BoM for manufacturing order.
        @param bom: BoM of particular product.
        @param factor: Factor of product UoM.
        @param properties: A List of properties Ids.
        @param addthis: If BoM found then True else False.
        @param level: Depth level to find BoM lines starts from 10.
        @return: result: List of dictionaries containing product details.
                 result2: List of dictionaries containing Work Center details.
        """
        routing_obj = self.pool.get('mrp.routing')
        factor = factor / (bom.product_efficiency or 1.0)
        factor = rounding(factor, bom.product_rounding)
        if factor < bom.product_rounding:
            factor = bom.product_rounding
        result = []
        result2 = []
        phantom = False
        if bom.type == 'phantom' and not bom.bom_lines:
            newbom = self._bom_find(cr, uid, bom.product_id.id, bom.product_uom.id, properties)

            if newbom:
                res = self._bom_explode(cr, uid, self.browse(cr, uid, [newbom])[0], factor*bom.product_qty, properties, addthis=True, level=level+10)
                result = result + res[0]
                result2 = result2 + res[1]
                phantom = True
            else:
                phantom = False
        if not phantom:
            if addthis and not bom.bom_lines:
                result.append(
                {
                    'name': bom.product_id.name,
                    'product_id': bom.product_id.id,
                    'product_qty': bom.product_qty * factor,
                    'product_uom': bom.product_uom.id,
                    'product_uos_qty': bom.product_uos and bom.product_uos_qty * factor or False,
                    'product_uos': bom.product_uos and bom.product_uos.id or False,
                })
            routing = (routing_id and routing_obj.browse(cr, uid, routing_id)) or bom.routing_id or False
            if routing:
                for wc_use in routing.workcenter_lines:
                    wc = wc_use.workcenter_id
                    d, m = divmod(factor, wc_use.workcenter_id.capacity_per_cycle)
                    mult = (d + (m and 1.0 or 0.0))
                    cycle = mult * wc_use.cycle_nbr
                    result2.append({
                        'name': tools.ustr(wc_use.name) + ' - '  + tools.ustr(bom.product_id.name),
                        'workcenter_id': wc.id,
                        'sequence': level+(wc_use.sequence or 0),
                        'cycle': cycle,
                        'hour': float(wc_use.hour_nbr*mult + ((wc.time_start or 0.0)+(wc.time_stop or 0.0)+cycle*(wc.time_cycle or 0.0)) * (wc.time_efficiency or 1.0)),
                        'multiple_component': wc_use.multiple_component or False,
                    })
            for bom2 in bom.bom_lines:
                res = self._bom_explode(cr, uid, bom2, factor, properties, addthis=True, level=level+10)
                result = result + res[0]
                result2 = result2 + res[1]
        return result, result2
    
    