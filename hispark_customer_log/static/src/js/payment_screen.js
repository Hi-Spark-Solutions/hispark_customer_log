odoo.define('hispark_customer_log.PaymentScreen', function(require) {
	'use strict';

	const PaymentScreen = require('point_of_sale.PaymentScreen');
	const Registries = require('point_of_sale.Registries');
	const NumberBuffer = require('point_of_sale.NumberBuffer');

	const PosMercuryPaymentScreen = (PaymentScreen) =>
		class extends PaymentScreen {
			setup() {
				super.setup();
			}
			deletePaymentLine(event) {
				var self = this;
				const { cid } = event.detail;
				const line = this.paymentLines.find((line) => line.cid === cid);
				if (['waiting', 'waitingCard', 'timeout'].includes(line.get_payment_status())) {
					line.set_payment_status('waitingCancel');
					line.payment_method.payment_terminal.send_payment_cancel(this.currentOrder, cid).then(function() {
						self.currentOrder.remove_paymentline(line);
						NumberBuffer.reset();
						self.showScreen('PaymentScreen')
						self.render(true);
					})
				}
				else if (line.get_payment_status() !== 'waitingCancel') {
					this.currentOrder.remove_paymentline(line);
					NumberBuffer.reset();
					self.showScreen('PaymentScreen')
					this.render(true);
				}
			}
		};

	Registries.Component.extend(PaymentScreen, PosMercuryPaymentScreen);
	return PaymentScreen;
});