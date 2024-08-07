from odoo import api, fields, models, _

class Bid(models.Model):
    _name = 'tender.bid'
    _description = 'Bid'

    tender_id = fields.Many2one('tender.management', string="Tender")
    # tender_name = fields.Char(string='Tender Name', related='tender_id.tender_name')
    tender_user = fields.Many2one(string='Purchase Representative', related='tender_id.tender_user')
    ref = fields.Char(string="Reference", copy=False, default='New', readonly=True)
    partner_id = fields.Many2many('res.partner', string="Vendor")
    date_created = fields.Date(string='Start Date', related='tender_id.date_created')
    date_bid_to_end = fields.Date(string='End Date', related='tender_id.date_bid_to_end')
    bid_management_line_ids = fields.One2many('bid.management.line', 'bid_management_id', string='Tender Management Line')
    bid_amount = fields.Float(string='Bid Amount', required=True)
    formatted_date = fields.Char(string='Formatted Date', compute='_compute_formatted_date')
    days_to_deadline = fields.Integer(string='Days To Deadline', compute='_compute_days')
    state = fields.Selection([
        ('draft', 'DRAFT'),
        ('submit', 'SUBMITTED'),
        ('approve', 'APPROVE'),
        ('approved', 'IN PROGRESS'),
        ('done', 'DONE'),
        ('cancel', 'CANCEL')
    ], string='State', default='draft', required=True)

    @api.depends('date_bid_to_end')
    def _compute_days(self):
        for rec in self:
            if rec.date_bid_to_end:
                today = fields.Date.context_today(self)
                days_difference = (rec.date_bid_to_end - today).days
                rec.days_to_deadline = days_difference
            else:
                rec.days_to_deadline = 0

    @api.depends('date_created')
    def _compute_formatted_date(self):
        for record in self:
            if record.date_created:
                date = fields.Date.to_date(record.date_created)
                record.formatted_date = f"{date.strftime('%d')} \n {date.strftime('%b %Y')}"
            else:
                record.formatted_date = ''

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('tender.bid') or _('New')
        return super(Bid, self).create(vals)


    def change_state(self, new_state):
        for rec in self:
            rec.state = new_state

    def action_approve(self):
        self.change_state('approve')
        return {
            'name': 'Purchase RFQ',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_id': self.env.ref('purchase.purchase_order_form').id,
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_tender_id': self.tender_id.id,
            }
        }

    def action_done(self):
        self.change_state('done')

    def action_cancel(self):
        self.change_state('cancel')

    def action_draft(self):
        self.change_state('draft')

    def action_approved(self):
        self.change_state('approved')

    def action_submit(self):
        self.change_state('submit')

class BidManagementLine(models.Model):
    _name = 'bid.management.line'
    _description = 'Bid Management Line'


    bid_management_id = fields.Many2one('tender.bid', string='Bid Management')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Unit Price')
    price_total = fields.Float(string='Total Price', compute='_compute_price_total')
    default_code = fields.Char(related='product_id.default_code', string='Code')
    qty = fields.Integer(string='Quantity')
    description = fields.Char(string='Description')

    @api.depends('quantity', 'price_unit')
    def _compute_price_total(self):
        for line in self:
            line.price_total = line.quantity * line.price_unit
