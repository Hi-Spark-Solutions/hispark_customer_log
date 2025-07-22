odoo.define('hispark_customer_log.CustomerLogScreen', function(require) {
	'use strict';
	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const rpc = require('web.rpc')
	const core = require('web.core');
	var QWeb = core.qweb;

	class CustomerLogScreen extends PosComponent {
		setup() {
			super.setup();
			this._start();
		}
		cancelButton() {
			var line = this.env.pos.get_order().get_paymentlines();
			if (line.length > 0) {
				this.orderDone()
				this.showScreen('ProductScreen');
			} else {
				this.showScreen('ProductScreen');
			}
		}

		get currentOrder() {
			return this.env.pos.get_order();
		}

		get nextScreen() {
			return { name: 'ProductScreen' };
		}

		orderDone() {
			this.env.pos.removeOrder(this.currentOrder);
			this.env.pos.add_new_order();
			this.showScreen('ProductScreen');
			const { name, props } = this.nextScreen;
			this.showScreen(name, props);
		}

		_start() {
			var self = this;
			this.renderElement();
			this.old_client = this.env.pos.get_order().get_partner();
			var order = self.env.pos.get_order();
			self.render_order(self.get_data(), order);
			$(document).unbind().on('click', ".order_invoice", function() {
				var tr = $(this).closest('tr');
				var orderType = tr.find('.dl_order_type').text();
				var invoiceId = tr.find('.dl_invoice_id').text();
				self.orderInvoicePrint(invoiceId, orderType);

			});

			$(document).on('click', ".expand_func", function() {
				var tr = $(this).closest('tr');
				var orderId = tr.find('.dl_order_id').text();
				var type = tr.find('.dl_order_type').text();
				$(this).addClass('close_func');
				$(this).removeClass('expand_func');
				$("#symbolcollapse_" + orderId).closest('i').removeClass('fa-angle-double-down');
				tr.next("tr").show();
				rpc.query({
					model: 'pos.order',
					method: 'fetch_customer_olines',
					args: [orderId, type],
				})
					.then(function(result) {
						var rlineHtml = QWeb.render('CLOLineScreen', { widget: self, lines: result });
						$('#expandline_' + orderId).html(rlineHtml);
					});
			});

			$(document).on('click', ".close_func", function() {
				var tr = $(this).closest('tr');
				var orderId = tr.find('.dl_order_id').text();
				$(this).addClass('expand_func');
				$(this).removeClass('close_func');
				tr.next("tr").hide();
				$("#symbolcollapse_" + orderId).closest('i').addClass('fa-angle-double-down');
			});

		}
		autoBack = true;

		renderElement() {
			var self = this;
			$('.customerlog-button').click(function() {
				self.showScreen('CustomerLogScreen')
			});
		}

		getCurrentScreenParam() {
			if (this.env.pos.get_order()) {
				var params = this.env.pos.get_order().get_screen_data('params');
				var datas = params['props']['dldata']
				return datas;
			} else {
				return params;
			}
		}

		get_data() {
			return this.getCurrentScreenParam('dldata');
		}

		orderInvoicePrint(invoiceId, orderType) {
			var self = this;
			if (orderType === 'POS') {
				self.env.legacyActionManager.do_action('account.account_invoices', {
					additional_context: {
						active_ids: [invoiceId],
					},
				})
			} else {
				self.env.legacyActionManager.do_action('account.account_invoices', {
                    additional_context: { active_ids: [invoiceId], }
                });
			}
		}
		render_order() {
			$(document).ready(function() {
				$("table.table-hover").each(function() {
					$(this).addClass("customer-log-table");
				});
			});
		}
	}
	CustomerLogScreen.template = 'CustomerLogScreen';
	Registries.Component.add(CustomerLogScreen);
	return CustomerLogScreen;
});