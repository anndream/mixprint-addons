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

from datetime import datetime
from dateutil.relativedelta import relativedelta

import time
from osv import fields, osv
import decimal_precision as dp
from operator import itemgetter

class account_period_close(osv.osv_memory):
    _inherit = "account.period.close"
    
    
    def data_save(self, cr, uid, ids, context=None):
        """
        This function close period
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: account period close’s ID or list of IDs
         """
        period_pool = self.pool.get('account.period')
        account_move_obj = self.pool.get('account.move')
        account_account = self.pool.get('account.account')
        ineco_close_accont_obj = self.pool.get('ineco.close.account')
        
        mode = 'done'
        for form in self.read(cr, uid, ids, context=context):
            if form['sure']:
                for id in context['active_ids']:
                    account_move_ids = account_move_obj.search(cr, uid, [('period_id', '=', id), ('state', '=', "draft")], context=context)
                    if account_move_ids:
                        raise osv.except_osv(_('Invalid Action!'), _('In order to close a period, you must first post related journal entries.'))

                    account_account_ids = account_account.search(cr, uid, [('type', '!=', "view")])
                    account_account_obj = account_account.browse(cr, uid,account_account_ids)
                    for acc_line in account_account_obj:
                        debit = 0.00
                        credit = 0.00
                        before_balance = 0.00
                        balance = 0.00
                        cr.execute('select sum(debit) as debit  from account_move_line  where period_id = %s  and account_id = %s',(id,acc_line.id))
                        row_debit =  map(itemgetter(0), cr.fetchall())
                        cr.execute('select sum(credit) as credit from account_move_line  where period_id = %s  and account_id = %s',(id,acc_line.id))
                        row_credit = map(itemgetter(0), cr.fetchall())
                        cr.execute('select balance from ineco_close_account  where account_id ='+ str(acc_line.id) +'order by id desc limit 1')
                        row_balance = map(itemgetter(0), cr.fetchall())
                        
                        if row_debit != [] and row_debit[0] != None:
                            debit = row_debit[0]
                        if row_credit != [] and row_credit[0] != None:
                            credit = row_credit[0]
                        if row_balance != [] and row_balance[0] != None:
                            before_balance = row_balance[0]
                            
                        balance = debit - credit + before_balance
                        ineco_id = ineco_close_accont_obj.create(cr, uid, {
                                        'account_id': acc_line.id,
                                        'period_id': id,
                                        'debit': debit,
                                        'credit': credit,
                                        'balance': balance,
                                        'balance_before' : before_balance,
                            })
                        
                    cr.execute('update account_journal_period set state=%s where period_id=%s', (mode, id))
                    cr.execute('update account_period set state=%s where id=%s', (mode, id))

        return {'type': 'ir.actions.act_window_close'}
    

class account_period(osv.osv):
    _inherit = "account.period"
    _description = "Add close account in period"
    _columns = {
        'close_line_ids': fields.one2many('ineco.close.account', 'period_id', 'Account'),
    }
    def action_draft(self, cr, uid, ids, *args):
        mode = 'draft'
        cr.execute('delete from ineco_close_account where period_id =%s',tuple(ids))
        cr.execute('update account_journal_period set state=%s where period_id in %s', (mode, tuple(ids),))
        cr.execute('update account_period set state=%s where id in %s', (mode, tuple(ids),))
        return True

class ineco_close_account(osv.osv):
    _name = "ineco.close.account"
    _description = "Close Account for Account Code"    
    _columns = {
        'name': fields.related('account_id', 'name',  string='Account Name', size=256,  store=True, type='char'),
        'code': fields.related('account_id', 'code',  string='Account Code', size=64,  store=True, type='char' ),
        'account_id': fields.many2one('account.account', 'Account',required=True,readonly=True),   
        'period_id': fields.many2one('account.period', 'Period',required=True,readonly=True),   
        'debit': fields.float('Debit', required=True, digits_compute= dp.get_precision('Account'), readonly=True),
        'credit': fields.float('Credit', required=True, digits_compute= dp.get_precision('Account'), readonly=True),
        'balance_before': fields.float('Balance Before', required=True, digits_compute= dp.get_precision('Account'), readonly=True),
        'balance': fields.float('Balance', required=True, digits_compute= dp.get_precision('Account'), readonly=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        }
    _defaults = {
        'balance': 0.00,
        'debit': 0.00,
        'credit': 0.00,
        'balance_before': 0.00,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
    }
    _sql_constraints = [
        ('account_period_uniq', 'unique(account_id, period_id)', 'Account and Period Name must be unique per company!'),
    ]    
    
ineco_close_account()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: