# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-Today INECO LTD., Part. (<http://www.ineco.co.th>).
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
    'name' : 'Iyara',
    'version' : '0.1',
    'depends' : ["sale","purchase","analytic","account"],
    'author' : 'INECO LTD.,PART.',
    'category': 'sale',
    'description': """
Feature: 
A. Sale Module:
1. Add Delivery Date on Sale Order
    """,
    'website': 'http://www.ineco.co.th',
    'data': [],
    'update_xml': [
        'sale_view.xml',
        'purchase_view.xml',
        'analytic_view.xml',

    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
