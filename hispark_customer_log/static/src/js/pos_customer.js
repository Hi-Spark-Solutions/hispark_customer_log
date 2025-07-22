odoo.define('hispark_customer_log.PosCustomerButton', function(require) {
	'use strict';
	const { Gui } = require('point_of_sale.Gui');
	const Registries = require('point_of_sale.Registries');
	const rpc = require('web.rpc')
	const core = require('web.core');
	const TicketButton = require('point_of_sale.TicketButton');
	var _t = core._t;

	const PosCustomerButton = (TicketButton) =>
		class extends TicketButton {
			setup() {
				super.setup();
			}

			async selectPartner() {
				var order = this.env.pos.get_order();
				const currentPartner = order.get_partner_name()
				const { confirmed, payload: newPartner } = await this.showTempScreen(
					'PartnerListScreen',
					{ partner: currentPartner }
				);
				if (confirmed) {
					order.set_partner(newPartner);
					order.updatePricelist(newPartner);
				}
			}

			async onClickPosCustomer() {
				var order = this.env.pos.get_order()
				if (!order.get_partner_name()) {
					const { confirmed } = await this.showPopup('ConfirmPopup', {
						title: this.env._t('Please select the Customer'),
						body: this.env._t('You need to select the customer before you can proceed.'),
					});
					if (confirmed) {
						this.selectPartner();
					}
				} else {
					this.viewCustomerLogClickHandler();
				}
			}

			viewCustomerLogClickHandler() {
				var self = this;
				var order = self.env.pos.get_order();
				var partner = order.get_partner();

				if (partner) {
					rpc.query({
						model: 'pos.order',
						method: 'fetch_customer_order',
						args: [partner.id, self.env.pos.pos_session.id],
					}).then(function(result) {
						self.showScreen('CustomerLogScreen', { dldata: result }, 'refresh');
					}, function(err) {
						err.event.preventDefault();
						var errMsg = 'Please check the Internet Connection./n';
						if (err.event.message)
							errMsg = err.data.message;
						Gui.showPopup('alert', {
							'title': _t('Error: Could not get order details.'),
							'body': _t(errMsg),
						});
					});
				} else {
					this.showPopup('ConfirmPopup', {
						title: this.env._t('Please select the Customer'),
						body: this.env._t('You need to select the customer before you can proceed.'),
					});
				}
			}
		}
	Registries.Component.add(PosCustomerButton);
	Registries.Component.extend(TicketButton, PosCustomerButton);
	return { TicketButton };
});