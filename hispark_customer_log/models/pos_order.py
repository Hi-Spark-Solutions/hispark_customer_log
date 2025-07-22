# -*- coding: utf-8 -*-
from odoo import api, fields, models


# Inheriting the PosOrder model
class PosOrder(models.Model):
    _inherit = 'pos.order'
        
    @api.model
    def fetch_customer_order(self, customer, session_id):
        """ Serialize the orders of the customer.
        get the sales,POS order and without order in invoice.
        params: customer int representing the customer id
        """
        params = {'partner_id': customer}
        sql_query = """ select  x.order_id, x.date_order, x.type  from (
                        select id as order_id,date_order,'SO'as type
                        from sale_order
                        where partner_id = %(partner_id)s
                        union
                        select id as order_id,date_order,'POS'as type
                        from pos_order
                        where partner_id = %(partner_id)s
                        union
                        select id as order_id,invoice_date as date_order,
                        ''as type
                        from account_move
                        where move_type not in ('in_invoice' , 'in_refund')
                        and partner_id = %(partner_id)s  and name is null
                        )
                        as x order by x.date_order desc"""

        self._cr.execute(sql_query, params)
        rows = self._cr.dictfetchall()
        datas = self.get_orderdata(rows, session_id)

        result = {'orders': datas}
        return result

    @api.model
    def get_orderdata(self, rows, session_id):
        """ Serialize all orders of the customer.
        list of the sales,POS order and without order in invoice.
        date_f is used to get date format from res_lang.
        Instead of round the value of amount, used ".2f" for printing two decimals.
        params: rows - list of orders
        """
        datas = []
        s_no = 0
        so_ids = [x['order_id'] for x in rows if x['type'] == "SO"]
        pos_ids = [x['order_id'] for x in rows if x['type'] == "POS"]
        invoice_ids = [x['order_id'] for x in rows if x['type'] == ""]
        s_orders = self.env['sale.order'].search([('id', 'in', so_ids)])
        p_orders = self.env['pos.order'].search([('id', 'in', pos_ids)])
        
        invoice = self.env['account.move'].search([
                                                ('id', 'in', invoice_ids)])
        date_f = self.env['res.lang'].search([('active', '=' , True)], limit=1)
        all_orders = {'SO': s_orders, 'POS': p_orders, 'Invoice': invoice}
        for key, orders in all_orders.items():
            for order in orders:
                s_no = s_no + 1
                date_orders = False
                if key == 'SO':
                    session_id = 0
                    invoice_cancel = False
                    order_invoice = order.invoice_ids.ids
                    invoices = self.move_returns(key , order_invoice, order)
                elif key == 'POS':
                    session_id = order.session_id.id
                    invoice_cancel = True if order.account_move.state == 'voided' else False
                    order_invoice = order.account_move.ids
                    invoices = self.move_returns(key , order_invoice, order)
                else:
                    session_id = 0
                    invoice_cancel = False
                    order_invoice = order.id
                    invoices = self.move_returns(key, order_invoice, order)
                if invoices.get('date_orders'):
                    date_orders = invoices.get('date_orders').strftime(date_f.date_format)
                if invoices.get('invoice_id'):
                    
                    for invoice in invoices.get('invoice_id'):
                        datas.append({
                                'id': order.id,
                                'sno': s_no,
                                'type': key,
                                'invoice_ref': invoice.name,
                                'invoice_id': invoice.id,
                                'amount_total': format(order.amount_total, ".2f"),
                                'date_order': date_orders,
                                'name': order.name or '',
                                'status': invoices.get('state'),
                                'session_id': session_id,
                                'invoice_cancel': invoice_cancel})
                else:
                    datas.append({'id': order.id,
                                'sno': s_no,
                                'type': key,
                                'invoice_ref': '',
                                'invoice_id': '',
                                'amount_total': format(order.amount_total, ".2f"),
                                'date_order': date_orders,
                                'name': order.name or '',
                                'status': invoices.get('state'),
                                'session_id': session_id,
                                'invoice_cancel': invoice_cancel
                                })
        return datas
    
    def move_returns(self, key, order_invoice, pos_order):
        '''Construct a dictionary containing invoice details based on provided key, order_invoice IDs, and pos_order state'''
        invoices = self.env['account.move'].search([('id', 'in', order_invoice)])
       
        date_orders = fields.Date.from_string(pos_order.date_order)
        state = ""
        if pos_order.state == 'draft':
            if key == 'SO':
                state = 'Quotation'
            elif key == 'POS':
                state = 'New'
            else:
                state = 'Draft'
        elif pos_order.state == 'sent' and key in 'SO':
            state = 'Quotation Sent'
        elif pos_order.state == 'sale':
            state = 'Sales Order'
        elif pos_order.state == 'done':
            if key == 'SO':
                state = 'Locked'
            if key == 'POS':
                state = 'Posted'
        elif pos_order.state == 'cancel':
            state = 'Cancelled'
        elif pos_order.state == 'paid':
            state = 'Paid'
        elif pos_order.state == 'invoiced':
            state = 'Invoiced'
        elif pos_order.state in ['proforma2','proforma'] and key not in ['POS','SO']:
            state = 'Pro-forma'
        elif pos_order.state == 'open' and key not in ['POS','SO']:
            state = 'Open'
        invoice = {
            'invoice_id': invoices,
            'state': state,
            'date_orders': date_orders
        }
        return invoice

    @api.model
    def fetch_customer_olines(self, order_id, otype):
        """ Serialize the orders Lines of the customer.
        Instead of round the value of amount, used ".2f" for printing two decimals.
        params: customer int representing the customer id
        """
        if otype and otype == "SO":
            order = self.env['sale.order'].browse(int(order_id))
            o_lines = order.order_line
            qty_column = 'product_uom_qty'
        elif otype == "POS":
            order = self.env['pos.order'].browse(int(order_id))
            o_lines = order.lines
            qty_column = 'qty'
        else:
            order = self.env['account.move'].browse(int(order_id))
            o_lines = order.invoice_line_ids
            qty_column = 'quantity'
        line = []
        s_no = 0
        for oLine in o_lines:
            s_no = s_no + 1
            qty = oLine[qty_column]
            line.append({
                'sno': s_no,
                'id': oLine.id,
                'product': oLine.product_id.name,
                'qty': qty,
                'price_unit': format(oLine.price_unit, ".2f"),
            })
        return line
