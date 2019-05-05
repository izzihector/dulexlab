from odoo import fields, models, api


class PickingsMerge(models.TransientModel):
    _name = 'stock.picking.merge'

    # RETURNS SELECTED TICKETS IDS
    @api.model
    def _selected_pickings(self):
        return [('id', 'in', self._context.get("actives"))]

    # RETURNS SELECTED TICKETS IDS
    @api.model
    def _get_pickings(self):
        pickings = self.env['stock.picking'].search(self._selected_pickings()).ids
        self.driver_id = pickings[0].driver_name.id or False
        return pickings.ids

    @api.model
    def _get_products(self):
        products = {}
        for pick in self.all_pickings:
            for line in pick.move_ids_without_package:
                if line.product_id.name in products:
                    products[line.product_id.name] += line.product_uom_qty
                else:
                    products[line.product_id.name] = line.product_uom_qty
        return products

    @api.model
    def _get_driver(self):
        driver = False
        if self.all_pickings:
            driver = self.all_pickings[0].driver_name.id
        return driver

    all_pickings = fields.Many2many(comodel_name='stock.picking', default=_get_pickings)
    driver_id = fields.Many2one('driver.name', 'Driver', default=_get_driver)
    date = fields.Date(string="Date", default=fields.Date.today())

    @api.multi
    def print_report(self):
        assert len(self) == 1
        return (
            self.env['ir.actions.report'].search(
                [('report_name', '=', "bi_pickings_report_merged.merged_pickings_template")], limit=1).
                report_action(self.env["stock.picking.merge"].browse(self.ids))
        )