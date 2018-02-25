# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api


class InheritStockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_new_transfer(self):

        for record in self.move_lines:
            sum = 0
            if record.purchase_line_id:
                for rec in self.env['stock.move'].search(
                        [('product_id', '=', record.product_id.id), ('state', '=', 'done')]):

                    if rec.purchase_line_id:
                        sum = sum + rec.product_qty
                    else:
                        sum = sum - rec.product_qty

                avg_price = self.env['product.variant.history'].search([('product_id', '=', record.product_id.id)],
                                                                       order='effective_datetime DESC', limit=1)

                avg = (sum * avg_price.value + record.ordered_qty * record.price_unit) / (sum + record.ordered_qty)
                self.env['product.variant.history'].create({
                    'product_id': record.product_id.id,
                    'product_tmpl_id': record.product_id.product_tmpl_id.id,
                    'uom_id': record.product_id.uom_id.id,
                    'company_id': record.company_id.id,
                    'effective_datetime': datetime.now(),
                    'value': round(avg, 2),
                })
                record.product_id.write({'standard_price': round(avg, 2)})

        return super(InheritStockPicking, self).do_new_transfer()
