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

from openerp.osv import fields, osv

#from datetime import datetime, timedelta
#from dateutil.relativedelta import relativedelta
import time
#import pooler

#from tools.translate import _
#from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
#import decimal_precision as dp
#import netsvc

class account_invoice(osv.osv):

    def onchange_payment_term_date_invoice(self, cr, uid, ids, payment_term_id, date_invoice):
        res = {}        
        if not date_invoice:
            date_invoice = time.strftime('%Y-%m-%d')
        if not payment_term_id:
            return {'value':{'date_due': date_invoice}} #To make sure the invoice has a due date when no payment term 
        pterm_list = self.pool.get('account.payment.term').compute(cr, uid, payment_term_id, value=1, date_ref=date_invoice)
        if pterm_list:
            pterm_list = [line[0] for line in pterm_list]
            pterm_list.sort()
            res = {'value':{'date_due': pterm_list[-1]}}
#         else:
#             raise osv.except_osv(_('Insufficient Data!'), _('The payment term of supplier does not have a payment term line.'))
        return res
    
    def _get_move_lines(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            id = invoice.id
            res[id] = []
            if not invoice.move_id:
                continue
            data_lines = [x for x in invoice.move_id.line_id]
            partial_ids = []
            for line in data_lines:
#                 ids_line = []
#                 if line.reconcile_id:
#                     ids_line = line.reconcile_id.line_id
#                 elif line.reconcile_partial_id:
#                     ids_line = line.reconcile_partial_id.line_partial_ids
#                 l = map(lambda x: x.id, ids_line)
                partial_ids.append(line.id)
            res[id] =[x for x in partial_ids]
        return res
    
    _inherit = "account.invoice"
    _columns = {
        'account_move_lines':fields.function(_get_move_lines, type='many2many', relation='account.move.line', string='General Ledgers'),                
#         'date_due': fields.date('Due Date', select=True,
#             help="If you use payment terms, the due date will be computed automatically at the generation "\
#                 "of accounting entries. The payment term may compute several due dates, for example 50% now and 50% in one month, but if you want to force a due date, make sure that the payment term is not set on the invoice. If you keep the payment term and the due date empty, it means direct payment."),        
        'bill_due': fields.date('Billing Date', select=True)
    }

#     def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
#             date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
#         partner_payment_term = False
#         acc_id = False
#         bank_id = False
#         fiscal_position = False
# 
#         opt = [('uid', str(uid))]
#         if partner_id:
# 
#             opt.insert(0, ('id', partner_id))
#             p = self.pool.get('res.partner').browse(cr, uid, partner_id)
#             if company_id:
#                 if (p.property_account_receivable.company_id and (p.property_account_receivable.company_id.id != company_id)) and (p.property_account_payable.company_id and (p.property_account_payable.company_id.id != company_id)):
#                     property_obj = self.pool.get('ir.property')
#                     rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
#                     pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
#                     if not rec_pro_id:
#                         rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('company_id','=',company_id)])
#                     if not pay_pro_id:
#                         pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('company_id','=',company_id)])
#                     rec_line_data = property_obj.read(cr,uid,rec_pro_id,['name','value_reference','res_id'])
#                     pay_line_data = property_obj.read(cr,uid,pay_pro_id,['name','value_reference','res_id'])
#                     rec_res_id = rec_line_data and rec_line_data[0].get('value_reference',False) and int(rec_line_data[0]['value_reference'].split(',')[1]) or False
#                     pay_res_id = pay_line_data and pay_line_data[0].get('value_reference',False) and int(pay_line_data[0]['value_reference'].split(',')[1]) or False
#                     if not rec_res_id and not pay_res_id:
#                         raise osv.except_osv(_('Configuration Error!'),
#                             _('Cannot find a chart of accounts for this company, you should create one.'))
#                     account_obj = self.pool.get('account.account')
#                     rec_obj_acc = account_obj.browse(cr, uid, [rec_res_id])
#                     pay_obj_acc = account_obj.browse(cr, uid, [pay_res_id])
#                     p.property_account_receivable = rec_obj_acc[0]
#                     p.property_account_payable = pay_obj_acc[0]
# 
#             if type in ('out_invoice', 'out_refund'):
#                 acc_id = p.property_account_receivable.id
#                 partner_payment_term = p.property_payment_term and p.property_payment_term.id or False
#             else:
#                 acc_id = p.property_account_payable.id
#                 partner_payment_term = p.property_supplier_payment_term and p.property_supplier_payment_term.id or False
#             fiscal_position = p.property_account_position and p.property_account_position.id or False
#             if p.bank_ids:
#                 bank_id = p.bank_ids[0].id
# 
#         result = {'value': {
#             'account_id': acc_id,
#             'payment_term': partner_payment_term,
#             'fiscal_position': fiscal_position
#             }
#         }
# 
#         if type in ('in_invoice', 'in_refund'):
#             result['value']['partner_bank_id'] = bank_id
# 
#         if payment_term != partner_payment_term:
#             if partner_payment_term:
#                 to_update = self.onchange_payment_term_date_invoice(
#                     cr, uid, ids, partner_payment_term, date_invoice)
#                 result['value'].update(to_update['value'])
#                 #Change Billing Date
#                 if p.billing_payment_id:
#                     bill_update = self.onchange_payment_term_date_due(
#                     cr, uid, ids, p.billing_payment_id.id, to_update['value'])
#                     result['value'].update(bill_update['value'])
#                 else:
#                     result['value']['bill_due'] = False
#             else:
#                 result['value']['date_due'] = False
# 
#         if partner_bank_id != bank_id:
#             to_update = self.onchange_partner_bank(cr, uid, ids, bank_id)
#             result['value'].update(to_update['value'])
#         return result    

    def onchange_payment_term_date_due(self, cr, uid, ids, payment_term_id, date_invoice):
        res = {}        
        if not date_invoice:
            date_invoice = time.strftime('%Y-%m-%d')
        if not payment_term_id:
            return {'value':{'bill_due': date_invoice}} #To make sure the invoice has a due date when no payment term 
        pterm_list = self.pool.get('account.payment.term').compute(cr, uid, payment_term_id, value=1, date_ref=date_invoice)
        if pterm_list:
            pterm_list = [line[0] for line in pterm_list]
            pterm_list.sort()
            res = {'value':{'bill_due': pterm_list[-1]}}
        else:
            raise osv.except_osv(_('Insufficient Data!'), _('The payment term of supplier does not have a payment term line.'))
        return res

#     def create(self, cr, uid, vals, context=None):
#         if vals.get('partner_id', False) and vals.get('date_due', False) :
#             partner = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'])[0]
#             if partner.billing_payment_id:
#                 pterm_list = self.pool.get('account.payment.term').compute(cr, uid, partner.billing_payment_id.id, value=1, date_ref=vals['date_due'])
#                 if pterm_list:
#                     pterm_list = [line[0] for line in pterm_list]
#                     pterm_list.sort()
#                     vals['bill_due'] = pterm_list[-1]
#                 
#         return super(account_invoice, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('date_due',False):
            for line in self.browse(cr, uid, ids):
                if line.partner_id.billing_payment_id:
                    pterm_list = self.pool.get('account.payment.term').compute(cr, uid, line.partner_id.billing_payment_id.id, value=1, date_ref=vals['date_due'])
                    if pterm_list:
                        pterm_list = [line[0] for line in pterm_list]
                        pterm_list.sort()
                        vals['bill_due'] = pterm_list[-1]
        return super(account_invoice, self).write(cr, uid, ids, vals, context=context)


class account_voucher(osv.osv):
    
    def _get_move_lines(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            id = invoice.id
            res[id] = []
            if not invoice.move_id:
                continue
            data_lines = [x for x in invoice.move_id.line_id]
            partial_ids = []
            for line in data_lines:
#                 ids_line = []
#                 if line.reconcile_id:
#                     ids_line = line.reconcile_id.line_id
#                 elif line.reconcile_partial_id:
#                     ids_line = line.reconcile_partial_id.line_partial_ids
#                 l = map(lambda x: x.id, ids_line)
                partial_ids.append(line.id)
            res[id] =[x for x in partial_ids]
        return res
    _inherit = "account.voucher"
    _columns = {
        'account_move_lines':fields.function(_get_move_lines, type='many2many', 
            relation='account.move.line', string='General Ledgers'),      
        'wht_ids': fields.one2many('ineco.wht', 'voucher_id', 'WHT'),
        'cheque_id': fields.many2one('ineco.cheque','Cheque'),        
        
    }
    
    def _get_wht_total(self, cr, uid, voucher_id, context=None):
        _amount_tax = 0.0
        voucher = self.browse(cr, uid, voucher_id)
        for wht in voucher.wht_ids:
            _amount_tax += wht.tax or 0.0
        return _amount_tax
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}           
        default.update({
            'wht_ids':False,
        })
        return super(account_voucher, self).copy(cr, uid, id, default, context)

    def wht_move_line_create(self, cr, uid, voucher_id, move_id, company_currency, current_currency, context=None):
        voucher_brw = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        move_line_pool = self.pool.get('account.move.line')
        for wht in voucher_brw.wht_ids:
            debit = credit = 0.0
            if voucher_brw.type in ('purchase', 'payment'):
                credit = wht.tax
            elif voucher_brw.type in ('sale', 'receipt'):
                debit = wht.tax
            if debit < 0: credit = -debit; debit = 0.0
            if credit < 0: debit = -credit; credit = 0.0
            sign = debit - credit < 0 and -1 or 1
            #set the first line of the voucher
            move_line = {
                    'name': 'WHT NO: ' + wht.name or '/',
                    'debit': debit,
                    'credit': credit,
                    'account_id': wht.account_id.id,
                    'move_id': move_id,
                    'journal_id': voucher_brw.journal_id.id,
                    'period_id': voucher_brw.period_id.id,
                    'partner_id': voucher_brw.partner_id.id,
                    'currency_id': company_currency <> current_currency and  current_currency or False,
                    'amount_currency': company_currency <> current_currency and sign * voucher_brw.amount or 0.0,
                    'date': voucher_brw.date,
                    'date_maturity': voucher_brw.date_due
                }
            move_line_pool.create(cr, uid, move_line)
        return True
    
    def first_move_line_get(self, cr, uid, voucher_id, move_id, company_currency, current_currency, context=None):
        voucher_brw = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        debit = credit = 0.0
        if voucher_brw.type in ('purchase', 'payment'):
            credit = voucher_brw.paid_amount_in_company_currency
            credit -= self._get_wht_total(cr, uid, voucher_id, context) or 0.0
        elif voucher_brw.type in ('sale', 'receipt'):
            debit = voucher_brw.paid_amount_in_company_currency
            debit -= self._get_wht_total(cr, uid, voucher_id, context) or 0.0
        if debit < 0: credit = -debit; debit = 0.0
        if credit < 0: debit = -credit; credit = 0.0
        sign = debit - credit < 0 and -1 or 1
        move_line = {
                'name': voucher_brw.name or voucher_brw.account_id.name or '/',
                'debit': debit,
                'credit': credit,
                'account_id': voucher_brw.account_id.id,
                'move_id': move_id,
                'journal_id': voucher_brw.journal_id.id,
                'period_id': voucher_brw.period_id.id,
                'partner_id': voucher_brw.partner_id.id,
                'currency_id': company_currency <> current_currency and  current_currency or False,
                'amount_currency': company_currency <> current_currency and sign * voucher_brw.amount or 0.0,
                'date': voucher_brw.date,
                'date_maturity': voucher_brw.date_due
            }
        return move_line
    
    def action_move_line_create(self, cr, uid, ids, context=None):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.move_id:
                continue
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            # we select the context to use accordingly if it's a multicurrency case or not
            context = self._sel_context(cr, uid, voucher.id, context)
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = context.copy()
            ctx.update({'date': voucher.date})
            # Create the account move record.
            move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
            # Get the name of the account_move just created
            name = move_pool.browse(cr, uid, move_id, context=context).name
            # Create the first line of the voucher
            move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, context), context)
            move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
            #WHT Tax Amount
            wht_total = self._get_wht_total(cr, uid, voucher.id, context)
            if voucher.type in {'sale','receipt'}:
                line_total = move_line_brw.debit - move_line_brw.credit + wht_total
            elif voucher.type in {'purchase','payment'}:
                line_total = move_line_brw.debit - move_line_brw.credit - wht_total
            else:
                line_total = move_line_brw.debit - move_line_brw.credit
            if wht_total:
                self.wht_move_line_create(cr, uid, voucher.id, move_id, company_currency, current_currency, context)
            rec_list_ids = []
            if voucher.type == 'sale':
                line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            elif voucher.type == 'purchase':
                line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            # Create one move line per voucher line where amount is not 0.0
            line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)

            # Create the writeoff line if needed
            ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, context)
            if ml_writeoff:
                move_line_pool.create(cr, uid, ml_writeoff, context)
            # We post the voucher.
            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            if voucher.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context={})
            # We automatically reconcile the account move lines.
            reconcile = False
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
        return True

class account_payment_term(osv.osv):
    _inherit = "account.payment.term"
    _columns = {
        'billing_term': fields.boolean('Billing Term'),
    }
    _defaults = {
        'billing_term': False,
    }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: