# models/category.py
from odoo import models, fields

class Category(models.Model):
    _name = 'tender.category'
    _description = 'Category'

    def _get_default_user(self):
        return self.env.user.id

    name = fields.Many2one('res.users', string="Purchase Representative", default=_get_default_user)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    category = fields.Char(string='Category')
