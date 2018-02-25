# -*- coding: utf-8 -*-
{
    'name': "Stock Move Backdating",

    'summary': """
            Backdating option for transfer.
        """,

    'description': """
        Stock transfer can be backdating by this module.      
    """,

    'author': "Genweb2",
    'website': "www.genweb2.com",

    'category': 'Inventory',
    'version': '10.0.0.1',

    'depends': ['stock'],

    'data': [
        'views/stock_picking_views.xml',
    ],

}