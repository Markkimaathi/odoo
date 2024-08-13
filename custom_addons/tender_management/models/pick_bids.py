from odoo import api, fields, models, _


class Bid(models.Model):
    _name = 'pick.bid'
    _description = 'Pick Bid'

    name = fields.Char(string="Reference", copy=False, default='New', readonly=True)
    bid_id = fields.Many2one('tender.bid', string='Bids')
    tender_user = fields.Many2one(string='Purchase Representative', related='bid_id.tender_user')
    date_created = fields.Date(string='Start Date', related='bid_id.date_created')
    date_bid_to_end = fields.Date(string='End Date', related='bid_id.date_bid_to_end')
    days_to_deadline = fields.Integer(string='Days Remaining', related='bid_id.days_to_deadline')
    partner_id = fields.Many2many('res.partner', string="Vendor", related="bid_id.partner_id")

    pick_bid_management_line_ids = fields.One2many('pick.bid.management.line', 'pick_bid_management_id',
                                                   string='Pick Bid Management Line')
    state = fields.Selection([
        ('draft', 'DRAFT'),
        ('approved', 'APPROVED'),
        ('cancelled', 'CANCELLED')
    ], string='State', default='draft', required=True)

    def change_state(self, new_state):
        for rec in self:
            rec.state = new_state

    def action_accept(self):
        for bid in self:
            other_bids = self.search([
                ('id', '!=', bid.id),
                ('state', '!=', 'cancelled')
            ])
            other_bids.write({'state': 'cancelled'})
            bid.change_state('approved')

    def action_reject(self):
        self.change_state('reject')

    def action_draft(self):
        self.change_state('draft')


class PickBidManagementLine(models.Model):
    _name = 'pick.bid.management.line'
    _description = "Pick Bid Management Line"

    product_id = fields.Many2one('product.product', string='Products')
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure',
        store=True, readonly=True,
    )
    product_quantity = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit Of Measure',
        store=True, readonly=True,
    )
    price_unit = fields.Float(string='Price', related='product_id.list_price', readonly=False)
    qty = fields.Integer(string='Quantity')
    default_code = fields.Char(related='product_id.default_code', string='Code')
    description = fields.Char(string='Description')
    # price_total = fields.Monetary(string='Total', related='bid_management_line_id.price_total')
    # currency_id = fields.Many2one('res.currency', string='Currency', required=True,
    #                               default=lambda self: self.env.company.currency_id)
    pick_bid_management_id = fields.Many2one('pick.bid', string='Pick Bid')
