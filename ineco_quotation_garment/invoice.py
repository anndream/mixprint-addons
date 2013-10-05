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

import time
from lxml import etree
import openerp.addons.decimal_precision as dp

from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class account_invoice(osv.osv):

    def _find_partner(self, inv):
        '''
        Find the partner for which the accounting entries will be created
        '''
        #if the chosen partner is not a company and has a parent company, use the parent for the journal entries 
        #because you want to invoice 'Agrolait, accounting department' but the journal items are for 'Agrolait'
        part = inv.partner_id
#         if part.parent_id and not part.is_company:
#             part = part.parent_id
        return part
        
    _inherit = 'account.invoice'
    
