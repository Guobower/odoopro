# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductVariantHistory(models.Model):
    _name = 'product.variant.history'

    value = fields.Float('Value')
    effective_datetime = fields.Datetime('Effective Date')

    product_id = fields.Many2one('product.product', 'Product', ondelete='cascade', required=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', ondelete='cascade', required=True)
    company_id = fields.Many2one('res.company', 'Company', ondelete='cascade', required=True)
    uom_id = fields.Many2one('product.uom', 'UoM', ondelete='cascade', required=True)
