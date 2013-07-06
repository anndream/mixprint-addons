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
{
    'name' : 'Ineco Quotation for Garment',
    'version' : '0.1',
    'author' : 'Mr.Tititab Srisookco',
    'category' : 'INECO',
    'description' : """
New Quotation Menu/View for Garment Business.
    """,
    'website': 'http://www.ineco.co.th',
    'images' : [],
    'depends' : ['base','sale','crm','ineco_crm','stock','sale_stock','account','hr'],
    'data': [
    ],
    'js': [
    ],
    'qweb' : [
    ],
    'css':[
           
    ],
    'demo': [
    ],
    'test': [
    ],
    'update_xml':[
        'sale_view.xml',
        'stock_view.xml',
        'account_view.xml',
        'sale_data.xml',
        'stock_partial_picking_view.xml',
        'partner_view.xml',
        'problem_view.xml',
        'problem_data.xml',
        'dashboard_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
