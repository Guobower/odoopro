# -*- coding: utf-8 -*-
{
    'name': "Product Variant Average Price History",
    'summary': """
        History Of Purchased Product Average""",
    'description': """
        This module save the history record of all product purchased price variant wise
    """,
    'author': "Genweb2",
    'website': "www.genweb2.com",
    'category': 'Product',
    'version': '10.0.1',
    'depends': [
        'purchase',
        'sale',
        'stock',
        'stock_move_backdating'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_variant_history_views.xml',
    ],
    'installable': True,
    'application': True,
}
