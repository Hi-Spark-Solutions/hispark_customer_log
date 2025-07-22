# -*- coding: utf-8 -*-
{
    "name": "Customer Log",
    "summary": "View customer order history and reprint invoices directly from the POS interface.",
    "description": """
        Enhance your POS with instant access to customer history. View past orders, track total purchases, and reprint 
        invoices directly from the POS screen for faster service and improved customer experience.
    """,
    
     "version": "16.0",
    "category": "Point Of Sale",
    "author": "Hi Spark Solutions",
    "company": "Hi Spark Solutions",
    "maintainer": "Hi Spark Solutions",
    "website": "https://www.hisparksolutions.com/",

    "depends": ["sale_management", "point_of_sale"],
    "demo": [],
    "data": [],
    "assets": {
        "point_of_sale.assets": [
            "hispark_customer_log/static/src/xml/customer_log_screen.xml",
            "hispark_customer_log/static/src/xml/pos_customer.xml",
            "hispark_customer_log/static/src/js/pos_customer.js",
            "hispark_customer_log/static/src/js/payment_screen.js",
            "hispark_customer_log/static/src/js/customer_log_screen.js",
            "hispark_customer_log/static/src/css/pos_customer_log.css",
            ],
         },

    "images": ["static/description/banner.gif"],
    "qweb": [],
    "live_test_url": "",

    "license": "OPL-1",
    "application": True,
    "auto_install": False,
    "installable": True,
    "price": "5",
    "currency": "USD",
}