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
from openerp.tools.translate import _


class account_account(osv.osv):

    _inherit = "account.account"
    _description = "Add Name2"

    _columns = {
        'name2': fields.char('Name2', size=256, select=True),
    }

account_account()


class account_voucher(osv.osv):
    
    _inherit = "account.voucher"
    _description = "Add Date Bank"
    _columns = {
        'iyara_bank_date': fields.date('Bank Date', select=True),
    }

account_voucher()

class account_move(osv.osv):
    
    _inherit = "account.move"
    _description = "Add Tax Period"
    _columns = {   
        'period_tax_id': fields.many2one('account.period', 'Tax Period'),
    }    
    
account_move()
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
