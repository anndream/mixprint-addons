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

from openerp.osv import fields, osv
from datetime import datetime, timedelta

class ineco_mrp_box(osv.osv):
    _name = "ineco.mrp.box"
    _description = "Box Master"
    _columns = {
        'name': fields.char('Box Code', size=32,required=True),
        'production_id': fields.many2one('mrp.production','Production',),
        'workcenter_id': fields.many2one('mrp.workcenter','Workcenter'),
        'employee_id': fields.many2one('hr.employee','Employee',),
        'last_action_datetime': fields.datetime('Last Action'),
        'active': fields.boolean('Active'),
    }
    _sql_constraints = [
        ('name', 'unique(name)', 'The name of the Box Master must be unique')
    ]
    _defauts = {
        'active': True,
    }
    
class ineco_mrp_box_activity(osv.osv):
    _name = 'ineco.mrp.box.activity'
    _description = 'Box Activity'
    _columns = {
        'name': fields.char('Description',size=64,),
        'date_action': fields.datetime('Date Action', required=True),
        'quantity': fields.integer('Quantity', required=True),
        'box_id': fields.many2one('ineco.mrp.box','Box'),
        'workcenter_id': fields.many2one('mrp.workcenter','Workcenter',),
        'employee_id': fields.many2one('hr.employee','Employee',),
        'workorder_id': fields.many2one('mrp.production.workcenter.line','Work Order',),
    }
    
class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'
    _columns = {
        'activity_ids': fields.one2many('ineco.mrp.box.activity','workorder_id','Activities'),
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: