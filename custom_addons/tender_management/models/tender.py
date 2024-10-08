from odoo import api, fields, models, _


class TenderManagement(models.Model):
    _name = "tender.management"
    _description = "Tender Management"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(default='Tender Name', required=True)
    tender_user = fields.Many2one('res.users', string="Purchase Representative", default=lambda self: self.env.user.id)
    ref = fields.Char(string="Reference", copy=False, default='New', readonly=True)
    partner_id = fields.Many2many('res.partner', string="Vendor")
    date_created = fields.Date(string='Start Date', default=fields.Date.context_today)
    date_bid_to_end = fields.Date(string='End Date', default=fields.Date.context_today)
    state = fields.Selection([
        ('draft', 'DRAFT'),
        ('submit', 'SUBMITTED'),
        ('approve', 'APPROVE'),
        ('approved', 'IN PROGRESS'),
        ('done', 'DONE'),
        ('cancel', 'CANCEL')
    ], string='State', default='draft', required=True)
    days_to_deadline = fields.Integer(string='Days To Deadline', compute='_compute_days')
    bid_ids = fields.One2many('tender.bid', 'tender_id', string="Bids")
    bid_count = fields.Integer(string='Bid Count', compute='_compute_bid_count', store=True)
    tender_management_line_ids = fields.One2many('tender.management.line', 'tender_management_id',
                                                 string='Tender Management Line')
    formatted_date = fields.Char(string='Formatted Date', compute='_compute_formatted_date')
    category_id = fields.Many2one('tender.category', string='Category')
    category_name = fields.Char(related='category_id.name', string='Category Name', store=True)
    top_rank = fields.Char(string='Top Rank', compute='_compute_top_rank')
    rank = fields.Integer(string='Rank')
    is_active = fields.Boolean(string='Active', default=True)
    website_published = fields.Boolean('Publish on Website', copy=False)
    tender_id = fields.Many2one('tender.bid', string='Tender ID')

    @api.depends('date_created')
    def _compute_formatted_date(self):
        for record in self:
            if record.date_created:
                date = fields.Date.to_date(record.date_created)
                record.formatted_date = f"{date.strftime('%d')} \n {date.strftime('%b %Y')}"
            else:
                record.formatted_date = ''

    @api.depends('date_bid_to_end')
    def _compute_days(self):
        for rec in self:
            if rec.date_bid_to_end:
                today = fields.Date.context_today(self)
                days_difference = (rec.date_bid_to_end - today).days
                rec.days_to_deadline = days_difference
            else:
                rec.days_to_deadline = 0

    @api.depends('bid_ids')
    def _compute_bid_count(self):
        for tender in self:
            tender.bid_count = len(tender.bid_ids)

    def _compute_rank(self):
        for bid in self:
            if bid.tender_id:
                bid.tender_id._compute_top_rank()

    @api.depends('bid_ids')
    def _compute_top_rank(self):
        for tender in self:
            if tender.bid_ids:
                highest_bids_by_vendor = {}
                for bid in tender.bid_ids:
                    partner_id = bid.partner_id.id
                    if partner_id not in highest_bids_by_vendor or bid.bid_amount > highest_bids_by_vendor[
                        partner_id].bid_amount:
                        highest_bids_by_vendor[partner_id] = bid
                sorted_bids = sorted(highest_bids_by_vendor.values(), key=lambda b: b.bid_amount, reverse=True)
                highest_bid_amount = sorted_bids[0].bid_amount if sorted_bids else 0
                for rank, bid in enumerate(sorted_bids, start=1):
                    bid.rank = rank
                tender.top_rank = f"Top Rank: 1 | Highest Bid: {highest_bid_amount}"
            else:
                tender.top_rank = "No Bids"

    def change_state(self, new_state):
        for rec in self:
            rec.state = new_state

    def action_approve(self):
        self.change_state('approve')

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

    @api.model
    def create(self, vals):
        if vals.get('ref', 'New') == 'New':
            vals['ref'] = self.env['ir.sequence'].next_by_code('tender.management') or 'New'
        return super(TenderManagement, self).create(vals)

    def toggle_website_publish(self):
        for record in self:
            record.website_published = not record.website_published
        return True


class TenderManagementLine(models.Model):
    _name = 'tender.management.line'
    _description = "Tender Management Line"

    product_id = fields.Many2one('product.product', string='Products', required=True)
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Product Uom',
        store=True, readonly=False,
    )
    price_unit = fields.Float(string='Price', readonly=False)
    qty = fields.Integer(string='Quantity', required=True)
    description = fields.Char(string='Description')
    tender_management_id = fields.Many2one('tender.management', string='Tender Management')

    @api.depends('product_id')
    def _compute_product_uom_id(self):
        for line in self:
            if line.product_id:
                line.product_uom_id = line.product_id.uom_id
                line.product_quantity = line.product_id.uom_id
            else:
                line.product_uom_id = False
                line.product_quantity = False
