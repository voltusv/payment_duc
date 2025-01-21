# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


# *** SaleOrder model to extend sale.order functionality ***
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # *** Field to store DUc transaction id for Sale Orders ***
    duc_transaction_id = fields.Char('duc transaction id', default="",
                                  groups='base.group_user')
