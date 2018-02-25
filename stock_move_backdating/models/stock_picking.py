# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError

class StockPicking(models.Model):

    _inherit = 'stock.picking'

    date_done = fields.Datetime('Date of Transfer', copy=False, readonly=False,
                                help="Completion Date of Transfer")

    @api.constrains('date_done')
    def _check_date_done(self):
        for stock_picking in self:
            if datetime.strptime(stock_picking.date_done, "%Y-%m-%d %H:%M:%S")>datetime.now():
                raise ValidationError('Transfer Date can not be greater then present date!!')

    @api.multi
    def do_transfer(self):
        """ If no pack operation, we do simple action_done of the picking.
        Otherwise, do the pack operations. """
        # TDE CLEAN ME: reclean me, please
        self._create_lots_for_picking()

        no_pack_op_pickings = self.filtered(lambda picking: not picking.pack_operation_ids)
        no_pack_op_pickings.action_done()
        other_pickings = self - no_pack_op_pickings
        for picking in other_pickings:
            need_rereserve, all_op_processed = picking.picking_recompute_remaining_quantities()
            todo_moves = self.env['stock.move']
            toassign_moves = self.env['stock.move']

            # create extra moves in the picking (unexpected product moves coming from pack operations)
            if not all_op_processed:
                todo_moves |= picking._create_extra_moves()

            if need_rereserve or not all_op_processed:
                moves_reassign = any(x.origin_returned_move_id or x.move_orig_ids for x in picking.move_lines if
                                     x.state not in ['done', 'cancel'])
                if moves_reassign and picking.location_id.usage not in ("supplier", "production", "inventory"):
                    # unnecessary to assign other quants than those involved with pack operations as they will be unreserved anyways.
                    picking.with_context(reserve_only_ops=True, no_state_change=True).rereserve_quants(
                        move_ids=picking.move_lines.ids)
                picking.do_recompute_remaining_quantities()

            # split move lines if needed
            for move in picking.move_lines:

                rounding = move.product_id.uom_id.rounding
                remaining_qty = move.remaining_qty
                if move.state in ('done', 'cancel'):
                    # ignore stock moves cancelled or already done
                    continue
                elif move.state == 'draft':
                    toassign_moves |= move
                if float_compare(remaining_qty, 0, precision_rounding=rounding) == 0:
                    if move.state in ('draft', 'assigned', 'confirmed'):
                        todo_moves |= move
                        # self.env['indent.indent'].search([('id', '=', move.indent_id.id)]).write(
                        #     {'state': 'received'})
                elif float_compare(remaining_qty, 0, precision_rounding=rounding) > 0 and float_compare(remaining_qty,
                                                                                                        move.product_qty,
                                                                                                        precision_rounding=rounding) < 0:
                    # TDE FIXME: shoudl probably return a move - check for no track key, by the way
                    new_move_id = move.split(remaining_qty)
                    new_move = self.env['stock.move'].with_context(mail_notrack=True).browse(new_move_id)
                    todo_moves |= move
                    # Assign move as it was assigned before
                    toassign_moves |= new_move

            # TDE FIXME: do_only_split does not seem used anymore
            if todo_moves and not self.env.context.get('do_only_split'):
                todo_moves.action_done()
                for move in todo_moves:
                    if self.date_done:
                        move.write({'date': self.date_done})
            elif self.env.context.get('do_only_split'):
                picking = picking.with_context(split=todo_moves.ids)

            picking._create_backorder()

        return True
