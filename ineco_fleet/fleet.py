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

from openerp.osv import fields, osv
import time
import datetime
from openerp import tools
from openerp.osv.orm import except_orm
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta

class fleet_driver(osv.osv):
    _name = 'ineco.fleet.driver'
    _columns = {
        'name': fields.char('Driver Name', size=128, required=True),
        'mobile': fields.char('Mobile', size=64),   
        'odometer_ids': fields.one2many('fleet.vehicle_odometer','driver_id', 'Odometers'),   
    }
    
class fleet_vehicle_odometer(osv.Model):
    _inherit = 'fleet.vehicle.odometer'
    #_table = 'ineco_fleet_vehicle_odometer'
    _description = "Add Driver and Customer in Odometer"
    _order='date_start desc'
    _columns = {
        'date_start': fields.datetime('Date Start'),
        'date_stop': fields.datetime('Date Stop'),
        'driver_id': fields.many2one('ineco.fleet.driver','Driver'),
        'picking_id': fields.many2one('stock.picking','Picking'),
        'partner_id': fields.many2one('res.partner','Customer'),
    }
    _defaults = {
        'date_start': lambda obj, cr, uid, context: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
        