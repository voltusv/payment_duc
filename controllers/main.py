# Import necessary modules
import logging  # For logging messages
import pprint  # For pretty-printing data structures
import requests  # For making HTTP requests
import json  # For handling JSON data
import datetime  # For date and time manipulation
import werkzeug  # For redirect and utility functions
import time  # For adding delays
from odoo import _  # To fetch translated strings
from odoo import http  # For creating HTTP routes
from odoo.http import request  # For managing HTTP requests in Odoo

# Logger instance for debugging and logging info/warnings/errors
_logger = logging.getLogger(__name__)


# *** Define a controller for handling payment-related routes and actions ***
class DucPaymentLinkController(http.Controller):
    # Define routes (URLs) for webhook, feedback, and return actions
    _webhook_url = '/payment/ducapi3/webhook'  # Endpoint for webhooks
    _feedback_url = '/payment/ducapi3/feedback'  # Endpoint for form feedback
    _return_url = '/payment/ducapi3/pay_return'  # Endpoint for return callback

    # *** Route for handling payment return requests ***
    @http.route(_return_url, type='http', methods=['GET'], auth='public', csrf=False)
    def duc_return(self, **post):
        # Log the incoming data for debugging
        _logger.info("Handling DUC processing with data:\n%s", pprint.pformat(post))

        # Retry logic for searching the transaction in case of failure
        max_retries = 5  # Maximum number of retry attempts
        delay = 2  # Delay between retries (seconds)

        transaction = None  # Initialize the transaction holder
        for attempt in range(max_retries):
            # Search for the transaction based on the reference provided in the request
            transaction = request.env['payment.transaction'].sudo().search([
                ('reference', '=', post.get('reference'))
            ], limit=1)

            if transaction:  # If transaction is found
                current_state = transaction.state
                _logger.info(f"Attempt {attempt + 1}: Transaction {transaction.id} has current state: {current_state}")
                # If the transaction is completed or canceled, set the status accordingly
                if current_state in ['done', 'cancel']:
                    post['status'] = current_state
                    break

            time.sleep(delay)  # Wait before the next attempt

        if not transaction:  # If no transaction is found
            _logger.warning("No transaction found for reference: %s", post.get('reference'))
        else:
            # If status was not already set, mark it as 'pending'
            if 'status' not in post:
                post['status'] = 'pending'

        # Notify payment transaction about the received data
        request.env['payment.transaction'].sudo()._handle_notification_data('ducapi3', post)

        # Redirect to the payment status page
        return request.redirect('/payment/status')

    # *** Route for handling DUCApi webhook notifications (POST requests only) ***
    @http.route(_webhook_url, type='http', methods=['POST'], auth='public', csrf=False)
    def ducapi3_webhook(self):
        # Parse the incoming JSON data
        data = json.loads(request.httprequest.data)

        _logger.info('Beginning DUCApi form_feedback with post data %s', pprint.pformat(data))  # Log the data

        try:
            # If the incoming data contains a transaction object
            if 'transaction' in data:
                transaction = data.get('transaction')
                # Check the transaction status
                if 'transactionStatus' in transaction:
                    transactionStatus = transaction.get('transactionStatus')
                    if transactionStatus in ['confirmed', 'accepted', 'canceled']:
                        # If all necessary transaction details exist
                        if ('transactionID' in transaction) and ('externalID' in transaction):
                            # Extract transaction reference from the external ID
                            transaction_reference = transaction.get('externalID').split("_")[0]
                            data = {
                                'reference': transaction_reference,
                                'status': transactionStatus,
                            }
                            # Find the transaction based on the notification
                            tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
                                'ducapi3', data
                            )
                            # Pass the data to payment transaction for handling
                            tx_sudo._handle_notification_data('ducapi3', data)
            else:
                # If no transaction data is provided in the webhook
                payload = {
                    'error': 'DUC',
                    'message': 'No Transaction',
                }
                return request.render('payment_duc.payment_link_info', payload)
        except Exception as ex:  # Handle unexpected exceptions
            _logger.info('DUCApi Return EndPoint: ' + str(ex))

        # Return "OK" response if successfully processed
        return "OK"

    # *** Route for handling form feedback for generating payment links ***
    @http.route(_feedback_url, type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def ducapi3_form_feedback(self, **post):
        payLink = None  # Initialize payLink
        try:
            # Extract order ID from the reference
            order_id = post['reference'].split("-")[0]
            # Fetch the corresponding order and payment provider
            order = request.env['sale.order'].sudo().search([('name', '=', order_id)], limit=1)
            payment_provider = request.env['payment.provider'].sudo().search([('id', '=', post['payment_provider_id'])],
                                                                             limit=1)
            timestamp = str(datetime.datetime.now().timestamp())  # Generate a timestamp

            # Construct the return URL to be used
            url_base = payment_provider.ducapi3_ngrok_link
            redirect_url = f"{url_base.strip()}{self._return_url}?reference={post['reference']}"

            # Prepare the payload for the payment link request
            data = {
                "product": {
                    "name": "DUC Pay",
                    "description": _("Sale Order Pay: ") + post['reference'].split("-")[0]
                },
                "amount": float(post['amount']),
                "currency": post['currency'],
                "merchant_external_id": post['reference'] + '_' + timestamp,
                "redirectUrl": redirect_url,
            }
            # Call helper function to create payment link
            response_data = self._create_duc_payment_link(payment_provider, data)

            # Handle response from the DUC API
            if 'error' in response_data:
                return {'error': response_data['error'], 'message': response_data['message']}

            if ('data' in response_data) and ('status' in response_data['data']):
                # If the request to DUC API is successful
                if response_data['data']['status'] in (200, 201):
                    payLink = response_data['data']['payload']['link']  # Retrieve the payment link
                    payload = {
                        "payLink": payLink,
                    }
                    # Write the transaction ID to the order
                    if 'transactionID' in response_data:
                        order.write({'duc_transaction_id': response_data['transactionID']})
                else:  # Handle errors in response
                    payload = {
                        'error': 'DUC',
                        'message': response_data['payload']
                    }
            else:  # Handle unknown errors
                payload = {
                    'error': 'DUC',
                    'message': 'Unknown error',
                }
        except Exception as ex:  # Handle exceptions gracefully
            _logger.info('DUCApi Return EndPoint: ' + str(ex))
            payload = {
                'error': 'DUC',
                'message': 'An error has occurred with your payment provider' + str(ex),
            }
        if payLink:  # Redirect to payment link if available
            return werkzeug.utils.redirect(payLink)
        else:  # Render a page with the error payload
            return request.render('payment_duc.payment_link_info', payload)

        # Default fallback response
        return request.render('payment_duc.payment_link_info',
                              {'error': 'DUC', 'message': 'Payment link not available'})

    # *** Helper function: Authenticate with DUC API provider ***
    def _authenticate_with_duc(self, payment_provider):
        """Authenticate with the DUC API provider."""
        headers = {"x-api-key": payment_provider.ducapi3_api_key}
        data = {"phone": payment_provider.ducapi3_merchant_phone,
                "password": payment_provider.ducapi3_merchant_password}
        url = f"{payment_provider.ducapi3_api_url}/auth/login"

        # Send authentication request
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json().get("accessToken")  # Return token if success
        else:
            raise Exception(f"Error authenticating with DUC: {response.text}")

    # *** Helper function: Create a payment link via DUC API ***
    def _create_duc_payment_link(self, payment_provider, data):
        """Create a payment link using the DUC API."""
        ducapi_token = self._authenticate_with_duc(payment_provider)  # Fetch access token
        headers = {
            "Authorization": "Bearer " + ducapi_token,
            "x-api-key": payment_provider.ducapi3_api_key,
            "Content-Type": "application/json",
        }
        # Send the request to the DUC API
        url = payment_provider.ducapi3_api_url + payment_provider.ducapi3_payment_page
        resp = requests.post(url, data=json.dumps(data), headers=headers)
        response_data = json.loads(resp.text)  # Parse response
        return response_data
