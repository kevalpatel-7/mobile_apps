# -*- coding: utf-8 -*-
{
    'name': "Crypto Solutions",

    'summary': """
        Crypto Solutions Helps User to get data about crypto rates.""",

    'description': """
        
    """,

    'author': "Conestoga.",
    'website': "",

    'category': 'Crypto',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/product_view.xml'
    ],
    'js': ['static/src/js/test.js']

}


