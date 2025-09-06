{
    'name': "NST Sale-like Demo (Step 1)",
    'version': '1.0',
    'depends': ['base', 'product'],   # <-- product обязателен!
    'data': [
        'security/ir.model.access.csv',
        'views/nst_order_views.xml',
    ],
    'installable': True,
    'application': True,
}
