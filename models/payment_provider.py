# coding: utf-8
from odoo import api, fields, models, tools, _
from .. import const

# *** "Model for adding DUC payment provider-specific fields and methods." ***
class VAProviderPaymentLink(models.Model):
    _inherit = 'payment.provider'

    # Selection field to add the DUC payment provider option.
    code = fields.Selection(
        selection_add=[('ducapi3', "DUC Card Payment Link")], ondelete={'ducapi3': 'set default'})

    # Field to specify the DUC payment mode.
    duc_mode = fields.Selection(
        string="DUC Mode",
        selection=[('duc_payment_link', "DUC Payment Link")],
        required_if_provider='ducapi3',
    )

    # URL of the DUC payment provider API.
    ducapi3_api_url = fields.Char('API URL', default="https://api_url", required_if_provider='ducapi3',
                                  groups='base.group_user')
    # Ngrok base URL for the provider's API.
    ducapi3_ngrok_link = fields.Char('Base url',
                                     default='https://your_domain.com',
                                     groups='base.group_user',
                                     required_if_provider='ducapi3',
                                     help="Ngrok link to base url")
    # API Key for authentication with the DUC payment provider.
    ducapi3_api_key = fields.Char('API Key', default="API Xxxxxx",
                                  required_if_provider='ducapi3', groups='base.group_user')
    # Merchant name for the DUC payment provider.
    ducapi3_mercant_name = fields.Char('DUC Merchant name', default="sedenob.erick@gmail.com", required_if_provider='ducapi3',
                                       groups='base.group_user')
    # Merchant password for the DUC payment provider.
    ducapi3_merchant_password = fields.Char('DUC Merchant password', default="XXXXXX", required_if_provider='ducapi3',
                                            groups='base.group_user')
    # Merchant phone number for the DUC payment provider.
    ducapi3_merchant_phone = fields.Char('DUC Merchant phone', default="+531234567",
                                         required_if_provider='ducapi3', groups='base.group_user')
    # URL of the payment link generation page for DUC.
    ducapi3_payment_page = fields.Char('DUC Payment page Url', default='/private/transactions/token/createPaymentLink',
                                       required_if_provider='ducapi3',
                                       groups='base.group_user')
    # Optional generated token for the DUC payment session.
    ducapi3_token = fields.Char('DUC Token', groups='base.group_user', required=False)


    # *** "Override to define default payment method codes for the DUC payment provider." ***
    def _get_default_payment_method_codes(self):

        # Override of `payment` to return the default payment method codes.
        """ Override of `payment` to return the default payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'ducapi3' or self.duc_mode != 'duc_payment_link':
            return default_codes
        return const.DEFAULT_PAYMENT_METHOD_CODES




