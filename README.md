# DUCApp Payment Provider Module for Odoo 18

This module integrates the DUCApp payment gateway into Odoo 18, enabling seamless processing of payments through the DUCApp platform.
## Features

- Secure payment processing via DUCApp.- Easy configuration within Odoo's payment acquirers.- Support for multiple currencies and countries.
## Prerequisites

Before installing this module, ensure you have:

- Odoo 18 installed and running.- Administrative access to your Odoo instance.- An active DUCApp merchant account.
## Installation

1. **Download the Module:**
   - Clone or download the `payment_duc` module from the [GitHub repository](https://github.com/voltusv/payment_duc/).
2. **Add to Odoo Addons Path:**
   - Place the `payment_duc` directory into your Odoo addons directory.
3. **Update Module List:**
   - Navigate to the Odoo interface.   - Go to the **Apps** menu.   - Click on **Update Apps List** to refresh the module list.
4. **Install the Module:**
   - In the **Apps** menu, search for "DUCApp Payment Acquirer".   - Click **Install** to add the module to your Odoo instance.
## Configuration

1. **Access Payment Providers:**
   - Navigate to **Invoicing** > **Configuration** > **Payment Acquirers**.
2. **Activate DUCApp:**
   - Locate "DUCApp" in the list of payment acquirers.   - Click the **Activate** button to enable it.
3. **Configure DUCApp Settings:**
   - Click on "DUCApp" to open the configuration form.   - In the **Credentials** tab, enter your DUCApp Merchant ID and Secure Hash Secret.   - In the **Configuration** tab, set the desired options:     - **State:** Set to **Enabled** for live transactions or **Test Mode** for testing purposes.     - **Payment Journal:** Select the journal to record DUCApp transactions.     - **Supported Currencies:** Specify the currencies accepted via DUCApp.     - **Countries:** Define the countries where DUCApp is available.
4. **Customize Messages (Optional):**
   - In the **Messages** tab, tailor the messages displayed to customers during various transaction states, such as pending, done, or canceled.
5. **Save and Publish:**
   - Click **Save** to apply the settings.   - Ensure the DUCApp payment acquirer is published to make it available to customers.
## Testing the Integration

Before going live, it's crucial to test the DUCApp integration:

1. **Enable Test Mode:**
   - In the DUCApp configuration, set the **State** to **Test Mode**.
2. **Perform Test Transactions:**
   - Simulate transactions to verify the payment flow and ensure everything functions as expected.
3. **Review Transactions:**
   - Check the transaction records in Odoo to confirm successful payment processing.
## Going Live

Once testing is complete:

1. **Switch to Live Mode:**
   - In the DUCApp configuration, set the **State** to **Enabled**.
2. **Monitor Transactions:**
   - Keep an eye on initial live transactions to ensure smooth operation.
## Support

For assistance with the DUCApp payment provider module:

- **DUCApp Support:** Contact DUCApp's support team for issues related to your merchant account or payment processing.- **Odoo Support:** Reach out to Odoo's support channels for help with module installation or configuration.
By following these steps, you can successfully integrate and configure the DUCApp payment provider in your Odoo 18 instance, offering a seamless payment experience for your customers.
