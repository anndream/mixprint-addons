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

from openerp.osv import osv, fields
import time
#import openerp.addons.decimal_precision as dp

class ineco_pattern(osv.osv):
    _name = 'ineco.pattern'
    _inherit = ['mail.thread']
    _description = "Pattern"
    _columns = {
        'name': fields.char('Code', size=64, required=True),
        'product_id': fields.many2one('product.product','Product',required=True),
        'saleorder_id': fields.many2one('sale.order','Sale Order', required=True),
        'garment_order_no': fields.related('saleorder_id', 'garment_order_no', type='char', string='Garment Order No', readonly=True),
        'partner_id': fields.related('saleorder_id', 'partner_id', type='many2one', relation='res.partner', string='Customer', readonly=True),
        'product_type_id': fields.many2one('ineco.pattern.product.type','Product Type',required=True),
        'line_ids': fields.one2many('ineco.pattern.line','pattern_id','Lines'),
        'log_ids': fields.one2many('ineco.pattern.log','pattern_id','Logs'),
        'component_ids': fields.one2many('ineco.pattern.component','pattern_id','Components'),
        'gender_ids': fields.many2many('sale.gender', 'ineco_pattern_sale_gender_rel', 'child_id', 'parent_id', 'Gender'),
        'size_ids': fields.many2many('sale.size', 'ineco_pattern_sale_size_rel', 'child_id', 'parent_id', 'Size'),
        'state': fields.selection([('ready','Ready'),('used','Used'),('damage','Damage')],'Status', readonly=True),
    }
    
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Code must be unique!'),
    ]
    
    _defaults = {
        'state': 'ready',
    }
    
    def button_ready(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'ready'})
        return True

    def button_used(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'used'})
        return True

    def button_damage(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'damage'})
        return True
    
class ineco_pattern_type(osv.osv):
    _name = 'ineco.pattern.type'
    _description = 'Type of Pattern Line'
    _columns = {
        'name': fields.char('Description',size=64,required=True),
        'code': fields.char('Code', size=10, required=True),
    }
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Description must be unique !')
    ]   
    
class ineco_pattern_product_type(osv.osv):
    _name = 'ineco.pattern.product.type'
    _description = 'Product Type of Pattern Line'
    _columns = {
        'name': fields.char('Description',size=64,required=True),
        'code': fields.char('Code', size=10, required=True),
    }
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Description must be unique !')
    ]   
    
class ineco_pattern_component(osv.osv):
    _name = 'ineco.pattern.component'
    _description = "Pattern Component"
    _columns = {
        'name': fields.char('Description',size=64,),
        'seq': fields.integer('Sequence'),
        'type_id': fields.many2one('ineco.pattern.type','Type',required=True),
        'last_updated': fields.datetime('Last Updated'),
        'pattern_id': fields.many2one('ineco.pattern','Pattern'),
    }
    _defaults = {
        'name': '...',
        'last_updated': time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    def write(self, cr, uid, ids, vals, context=None):
        vals.update({'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")})
        res = super(ineco_pattern_component, self).write(cr, uid, ids, vals, context=context)
        return res    
        
class ineco_pattern_line(osv.osv):
    _name = 'ineco.pattern.line'
    _description = "Pattern Line"
    _columns = {
        'name': fields.char('Line Code',size=64,required=True),
        'gender_id': fields.many2one('sale.gender','Gender',required=True),
        'size_id': fields.many2one('sale.size','Size',required=True),
        'type_id': fields.many2one('ineco.pattern.type','Type',required=True),
        'last_updated': fields.datetime('Last Updated'),
        'pattern_id': fields.many2one('ineco.pattern','Pattern'),
    }
    _sql_constraints = [
        ('name_gender_size_type_unique', 'unique (name,gender_id,size_id,type_id)', 'Data must be unique !')
    ]   
    _defaults = {
        'last_updated': time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    def write(self, cr, uid, ids, vals, context=None):
        vals.update({'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")})
        res = super(ineco_pattern_line, self).write(cr, uid, ids, vals, context=context)
        return res
    
class ineco_pattern_log(osv.osv):
    _name = "ineco.pattern.log"
    _description = "Pattern LOG"
    _columns = {
        'name': fields.char('Description',size=64,),
        'type': fields.selection([('in','In'),('out','Out')],'Type',required=True),
        'user_id': fields.many2one('res.users','User', required=True),
        'pattern_line_id': fields.many2one('ineco.pattern.line','Pattern Line',),
        'last_updated': fields.datetime('Last Updated'),    
        'pattern_id': fields.many2one('ineco.pattern','Pattern'),
    }
    _defaults = {
        'last_updated': time.strftime("%Y-%m-%d %H:%M:%S"),
    }
