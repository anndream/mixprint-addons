# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-Today INECO LTD,. PART. (<http://www.ineco.co.th>).
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

from osv import fields, osv
import decimal_precision as dp


class ineco_cheque(osv.osv):

    _name = "ineco.cheque"
    _description = "cheque for customer payment and supplier payment"
    _columns = {
        'name': fields.char('Cheque No.', size=32, required=True),
        'cheque_date': fields.date('Date',required=True), 
        'bank': fields.many2one('res.bank', 'Bank',required=True),        
        'partner_id': fields.many2one('res.partner', 'Pay', required=True, ondelete='cascade', select=True),
        'the_sum_of': fields.char('The Sum Of', size=254, required=True),  
        'amount': fields.float('Amount', digits_compute= dp.get_precision('Account'), required=True),
        'type': fields.selection([('out', 'Supplier'), ('in', 'Customer')], 'Cheque Type', required=True, select=True),
        'note': fields.text('Notes', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'active': fields.boolean('Active'),
        'voucher_id': fields.many2one('account.voucher','Voucher'),        
        'state': fields.selection([
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('assigned', 'Assigned'),
            ('pending', 'Pending'), 
            ('reject', 'Reject'),                                   
            ('done', 'Done'),
            ], 'Status', readonly=True, select=True, track_visibility='onchange', 
        ), 
    }
    _defaults = {
        'active': 1,                 
        'state': 'draft',
    }                  
    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Cheque No. must be unique !')
    ]


ineco_cheque()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
