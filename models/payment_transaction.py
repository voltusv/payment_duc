# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, api, models, fields
from odoo.exceptions import ValidationError
from ..controllers.main import DucPaymentLinkController

# Logger to track messages and errors for the PaymentTransaction class
_logger = logging.getLogger(__name__)


# *** This class defines custom behavior and extensions for payment transactions ***
class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    _order = 'id desc'
    _order = 'id desc'  # Defines default sorting for transaction records
    _rec_name = 'reference'  # Sets the display name for transaction records

    # *** Handles form feedback received for a transaction ***
    def form_feedback(self, provider_code, data):
        pass


    # *** Retrieves the name of a currency from its ID ***
    def _get_currency_name(self, currency_id):

        currency = self.env['res.currency'].search([('id', '=', currency_id)], limit=1)  # Searches for the currency with the given ID
        if currency:
            return currency.name  # Returns the name of the currency if found
        else:
            return 'Currency not exist'  # Returns a default message if the currency is not found

    # *** Prepares specific rendering values required by the provider ***
    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'ducapi3':
            return res
        self.ensure_one()
        rendering_values = {
             "amount": processing_values["amount"],
             "reference": processing_values["reference"],
             "currency": self._get_currency_name(processing_values["currency_id"]),
             "payment_provider_id": processing_values["provider_id"],
             "api_url": DucPaymentLinkController._feedback_url,
        }

        return rendering_values

    # *** Finds a transaction using provider code and notification data ***
    def _get_tx_from_notification_data(self, provider_code, notification_data):
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'ducapi3' or len(tx) == 1:
            return tx

        reference = notification_data.get('reference')
        if not reference:
            raise ValidationError(  # Raises an error if the reference is missing in the notification data
                "DUC: " + _(
                    "Received data with missing reference %(r)s.",
                    r=reference
                )
            )

        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'ducapi3')])
        if not tx:
            raise ValidationError(  # Raises an error if no matching transaction is found
                "DUC: " + _("No transaction found matching reference %s.", reference)
            )

        return tx

    # *** Gets a unique channel identifier for a user based on their partner ID ***
    def _get_user_channel(self, partner_id):

        user_id = self.env['res.users'].sudo().search([('partner_id', '=', partner_id)])  # Finds the user with the given partner ID
        return 'user_' + str(user_id.id)  # Returns a unique user channel string based on the user ID

    # *** Processes notification data and updates the transaction status ***
    def _process_notification_data(self, notification_data):
        super()._process_notification_data(notification_data)
        if self.provider_code != 'ducapi3':
            return

        # self.provider_reference = notification_data.get('trade_no')  # Uncomment to set the provider reference from notification data
        user_channel = self._get_user_channel(self.partner_id.id)  # Retrieves the user channel based on the partner ID

        status = notification_data.get('status')  # Extracts the payment status from the notification data

        if status == 'accepted':  # Checks if the payment status is 'accepted'
            self.env['bus.bus']._sendone(user_channel, 'order.notification', {  # Sends an order confirmation notification
                'message': 'La orden ' + str(self.reference.split('-')[0]) + ' ha sido confirmada'})
            self._set_done()  # Marks the transaction as done


            # self._finalize_post_processing()
            # self.env.cr.commit()
        elif status == 'canceled':
            self.env['bus.bus']._sendone(user_channel, 'order.notification', {  # Sends an order cancellation notification
                'message': 'La orden ' + str(self.reference.split('-')[0]) + ' ha sido cancelada'})
            self._set_canceled()  # Marks the transaction as canceled

            # self._finalize_post_processing()
            # self.env.cr.commit()

        else:
            _logger.info(  # Logs information about invalid payment status
                "received data with invalid payment status (%s) for transaction with reference %s",
                status, self.reference,
            )

            self._set_error("DUC: " + _("received invalid transaction status: %s", status))  # Sets the transaction to an error state
