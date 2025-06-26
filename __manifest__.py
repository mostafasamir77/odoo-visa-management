{
    'name': "Visa Management",
    'author': "elsasa",
    'version': '18.1',
    'depends': ['base', 'contacts', 'mail', 'stock', 'accountant','hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/base_view.xml',
        'views/visa_management_view.xml',
        'views/visa_type.xml',
        'views/employee_inhert_view.xml',
        'wizard/use_visa_wizard_view.xml',
    ],
    'application': True,
}