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

#from lxml import etree
#from datetime import datetime
#from dateutil.relativedelta import relativedelta
#import time
#from operator import itemgetter
#from itertools import groupby

from openerp.osv import fields, osv
#from openerp.tools.translate import _
#from openerp import netsvc
#from openerp import tools
#from openerp.tools import float_compare
#import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class stock_journal(osv.osv):
    _inherit = 'stock.journal'
    _columns = {
        'sequence_id': fields.many2one('ir.sequence', 'Sequence'),
    }
    
class stock_picking_out(osv.osv):
    
    _inherit = 'stock.picking.out'

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        picking_obj = self.browse(cr, uid, id, context=context)
        move_obj=self.pool.get('stock.move')
        if ('name' not in default) or (picking_obj.name=='/'):
            if picking_obj.stock_journal_id:
                seq_obj_name =picking_obj.stock_journal_id.sequence_id.code
            else:
                seq_obj_name =  'stock.picking.' + picking_obj.type
            default['name'] = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
            default['origin'] = ''
            default['backorder_id'] = False
        if 'invoice_state' not in default and picking_obj.invoice_state == 'invoiced':
            default['invoice_state'] = '2binvoiced'
        res=super(stock_picking_out, self).copy(cr, uid, id, default, context)
        if res:
            picking_obj = self.browse(cr, uid, res, context=context)
            for move in picking_obj.move_lines:
                move_obj.write(cr, uid, [move.id], {'tracking_id': False,'prodlot_id':False, 'move_history_ids2': [(6, 0, [])], 'move_history_ids': [(6, 0, [])]})
        return res
    
    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            if ('stock_journal_id' in vals) and (vals.get('stock_journal_id')):
                stock_journal = self.pool.get('stock.journal').browse(cr, user, [vals.get('stock_journal_id')])[0]
                if stock_journal:
                    seq_obj_name = stock_journal.sequence_id.code
                else:
                    seq_obj_name =  'stock.picking.' + vals['type']
            elif ('stock_journal_id' in context): #make stock_journal_id in context
                stock_journal_ids = self.pool.get('stock.journal').search(cr, user, [('name','=',context['stock_journal_id'])])
                if stock_journal_ids:
                    stock_journal = self.pool.get('stock.journal').browse(cr, user, stock_journal_ids)[0]
                    if stock_journal:
                        vals['stock_journal_id'] = stock_journal.id
                        seq_obj_name = stock_journal.sequence_id.code
                    else:
                        seq_obj_name =  'stock.picking.' + vals['type']
            else:
                seq_obj_name =  'stock.picking.' + vals['type']
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        new_id = super(stock_picking_out, self).create(cr, user, vals, context)
        return new_id
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: