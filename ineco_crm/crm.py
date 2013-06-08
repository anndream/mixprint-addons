# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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

# 2013-02-10     POP-001    ADD New notification on sale user
from datetime import datetime
from openerp.osv import fields, osv
import time
#import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _

#POP-001
class crm_phonecall(osv.osv):
    _inherit = 'crm.phonecall'
    _columns = {
        'create_user_id': fields.many2one('res.users', 'Created By'),
        'new_customer': fields.boolean('New Customer'),
    }
    _defaults = {
        'create_user_id': lambda self,cr,uid,ctx: uid,
        'new_customer': False,
    }

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}         
        for phone in self.browse(cr, uid, ids, context=context):
            if phone.partner_id:
                self.pool.get("res.partner").write(cr, uid, [phone.partner_id.id], {'last_phonecall': time.strftime('%Y-%m-%d %H:%M:%S')})                                   
        return super(crm_phonecall, self).write(cr, uid, ids, vals, context=context)
    
    #Copy from Original
    def convert_opportunity(self, cr, uid, ids, opportunity_summary=False, partner_id=False, planned_revenue=0.0, probability=0.0, context=None):
        partner = self.pool.get('res.partner')
        opportunity = self.pool.get('crm.lead')
        opportunity_dict = {}
        default_contact = False
        for call in self.browse(cr, uid, ids, context=context):
            if not partner_id:
                partner_id = call.partner_id and call.partner_id.id or False
            if partner_id:
                partner.write(cr, uid, [partner_id], {'last_phonecall': time.strftime('%Y-%m-%d %H:%M:%S')})
                address_id = partner.address_get(cr, uid, [partner_id])['default']
                if address_id:
                    default_contact = partner.browse(cr, uid, address_id, context=context)
            opportunity_id = opportunity.create(cr, uid, {
                            'name': opportunity_summary or call.name,
                            'planned_revenue': planned_revenue,
                            'probability': probability,
                            'parquotation_mixprint_20130205_1_2_1tner_id': partner_id or False,
                            'mobile': default_contact and default_contact.mobile,
                            'section_id': call.section_id and call.section_id.id or False,
                            'description': call.description or False,
                            'priority': call.priority,
                            'type': 'opportunity',
                            'phone': call.partner_phone or False,
                            'email_from': default_contact and default_contact.email,
                        })
            vals = {
                    'partner_id': partner_id,
                    'opportunity_id' : opportunity_id,
            }
            self.write(cr, uid, [call.id], vals)
            self.case_close(cr, uid, [call.id])
            opportunity.case_open(cr, uid, [opportunity_id])
            opportunity_dict[call.id] = opportunity_id
        return opportunity_dict

    #Copy from Original
    def case_close(self, cr, uid, ids, context=None):
        """ Overrides close for crm_case for setting duration """
        res = True
        for phone in self.browse(cr, uid, ids, context=context):
            phone_id = phone.id
            data = {}
            if phone.duration <=0:
                duration = datetime.now() - datetime.strptime(phone.date, DEFAULT_SERVER_DATETIME_FORMAT)
                data['duration'] = duration.seconds/float(60)
            res = super(crm_phonecall, self).case_close(cr, uid, [phone_id], context=context)
            self.write(cr, uid, [phone_id], data, context=context)
            if phone.partner_id:
                self.pool.get("res.partner").write(cr, uid, [phone.partner_id.id], {'last_phonecall': time.strftime('%Y-%m-%d %H:%M:%S')})
        return res
    
    #Copy from Original
    def _call_create_partner(self, cr, uid, phonecall, context=None):
        partner = self.pool.get('res.partner')
        partner_id = partner.create(cr, uid, {
                    'name': phonecall.name,
                    'user_id': phonecall.user_id.id,
                    'comment': phonecall.description,
                    'address': [],
                    'last_phonecall': time.strftime('%Y-%m-%d %H:%M:%S'),
        })
        return partner_id

    def create(self, cr, uid, vals, context=None):
        obj_id = super(crm_phonecall, self).create(cr, uid, vals, context)
        if 'user_id' in vals:
            users = self.pool.get('res.users').browse(cr, uid, vals['user_id'] )
            self.message_subscribe(cr, uid, [obj_id], [users.partner_id.id], context=context)
            newid = self.message_post(cr, uid, [obj_id], body="Please read new phone call.", context=context)
            notification = self.pool.get('mail.notification')
            data = {
                'partner_id': users.partner_id.id,
                'message_id': newid,
                'read': False,
            }
            notification.create(cr, uid, data)
        return obj_id
    
    
class ineco_crm_reason(osv.osv):
    """ Category of Reason """
    _name = "ineco.crm.reason"
    _description = "Category of Reason"
    _columns = {
        'name': fields.char('Name', size=254, required=True),
    }

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Reason Name must be unique!')
    ]

class crm_lead(osv.osv):
    
    def _last_date_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for lead in self.browse(cr, uid, ids, context=context):
            last_date_count = 0
            if lead.state != 'done':
                date_now = time.strftime('%Y-%m-%d %H:%M:%S')
                date_start = datetime.strptime(lead.create_date,'%Y-%m-%d %H:%M:%S')
                date_finished = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')
                last_date_count = (date_finished-date_start).days 
            res[lead.id] = last_date_count
        return res
    
    _name = "crm.lead"
    _description = "Add Reason of LEAD/OPPORTUNITY"
    _inherit = "crm.lead"
    _columns = {
        'last_date_count': fields.function(_last_date_count, type="integer", string='Date Count',
            store={
                'crm.lead': (lambda self, cr, uid, ids, c={}: ids, [], 10),
            }, help="The amount without tax.", track_visibility='always'),
        'reason_ids': fields.many2many('ineco.crm.reason', 'crm_lead_reason_rel', 'lead_id', 'reason_id', 'Reasons'),
    }
    
    _defaults = {
        'referred': lambda s, cr, uid, c: s.pool.get('res.users').browse(cr, uid, uid).name,
    }

    def create(self, cr, uid, data, context=None):
        user = self.pool.get('res.users').browse(cr, uid, [uid])[0]
        data['referred'] = user.name
        return super(crm_lead, self).create(cr, uid, data, context=context)

    def case_reset(self, cr, uid, ids, context=None):
        """ Overrides case_reset from base_stage to set probability """
        res = super(crm_lead, self).case_reset(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'probability': 0.0, 'date_closed': False}, context=context)
        return res

    def case_mark_lost(self, cr, uid, ids, context=None):
        """ Mark the case as lost: state=cancel and probability=0 """
        for lead in self.browse(cr, uid, ids):
            stage_ids = self.pool.get('crm.case.stage').search(cr, uid, [('type','=','opportunity'),('state','=','cancel')])
            #stage_id = self.stage_find(cr, uid, [lead], lead.section_id.id or False, [('probability', '=', 0.0),('on_change','=',True)], context=context)
            if stage_ids:
                self.case_set(cr, uid, [lead.id], values_to_update={'probability': 0.0, 'date_closed': time.strftime("%Y-%m-%d %H:%M:%S")}, new_stage_id=stage_ids[0], context=context)
        return True

    def case_mark_won(self, cr, uid, ids, context=None):
        """ Mark the case as won: state=done and probability=100 """
        for lead in self.browse(cr, uid, ids):
            stage_id = self.stage_find(cr, uid, [lead], lead.section_id.id or False, [('probability', '=', 100.0),('on_change','=',True)], context=context)
            if stage_id:
                self.case_set(cr, uid, [lead.id], values_to_update={'probability': 100.0, 'date_closed': time.strftime("%Y-%m-%d %H:%M:%S")}, new_stage_id=stage_id, context=context)
        return True
    
#    def write(self, cr, uid, ids, vals, context=None):
#        if context is None:
#            context = {}            
#        if not ids:
#            return True       
#        if isinstance(ids, (int, long)):
#            ids = [ids]          
#        for lead in self.browse(cr, uid, ids):
#            stage_loss_id = self.stage_find(cr, uid, [lead], lead.section_id.id or False, [('probability', '=', 0.0)], context=context)
#            stage_win_id = self.stage_find(cr, uid, [lead], lead.section_id.id or False, [('probability', '=', 100.0)], context=context)
#    
#            if 'stage_id' in vals:
#                if vals['stage_id'] in [stage_loss_id, stage_win_id]:
#                    opp = self.browse(cr, uid, ids)[0]
#                    if not opp.date_deadline:
#                        raise osv.except_osv(_('Error!'),
#                                             _('Please inform Closing Date of (LOSS or WIN).'))         
#                    
#        return super(crm_lead, self).write(cr, uid, ids, vals, context=context)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
