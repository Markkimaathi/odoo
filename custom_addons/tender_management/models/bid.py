from odoo import api, fields, models,_

class Bid(models.Model):
    _name = 'tender.bid'
    _description = 'Bid'

    def _get_default_user(self):
        return self.env.user.id

    name = fields.Many2one('res.users', string="Purchase Representative", default=_get_default_user)
    tender_id = fields.Many2one('tender.management', string="Tender", required=True)
    ref = fields.Char(string="Reference", copy=False, default='New', readonly=True)
    partner_id = fields.Many2many('res.partner', string="Vendor")
    date_created = fields.Date(string='Start Date', default=fields.Date.context_today)
    date_bid_to_end = fields.Date(string='End Date', default=fields.Date.context_today)
    bid_amount = fields.Float(string="Bid Amount")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('tender.bid') or _('New')
        return super(Bid, self).create(vals)

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_accept(self):
        self.write({'state': 'accepted'})

    def action_reject(self):
        self.write({'state': 'rejected'})
