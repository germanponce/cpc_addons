# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time

class repairing_causes(models.Model):
    _name = 'mrp.repair.wes.cause'
    
    name = fields.Char('Code', required=True, copy=False, help="Code for this repairing cause")
    description = fields.Char('Description', required=True, help="Repairing cause description")
    
class hddcheck_in(models.Model):
    _name = 'mrp.repair.wes.hddcheckin'
    
    name = fields.Char('Code', required=True, copy=False, help="Code for this HDD CheckIn")
    description = fields.Text('Description', required=True, help="HDD CheckIn code description")
    comments = fields.Text('Comments')
    
class failure_code(models.Model):
    _name = 'mrp.repair.wes.failcode'
    
    name = fields.Char('Code', required=True, copy=False, help="Code for this Failure")
    description = fields.Text('Description', required=True, help="Failure code description")
    comments = fields.Text('Comments')
    
class scrap_code(models.Model):
    _name = 'mrp.repair.wes.scrap'
    
    name = fields.Char('Name', required=True, copy=False, help="Name for this Scrap code")
    comments = fields.Text('Comments')
    
class brands(models.Model):
    _name = 'mrp.repair.wes.brand'
    
    name = fields.Char('Name', required=True, copy=False, help="Name for this Brand")
    comments = fields.Text('Comments')
    
class nonrepair_reason(models.Model):
    _name = 'mrp.repair.wes.nonrepreason'
    
    name = fields.Char('Reason', required=True, copy=False, help="Name for this Reason")
    comments = fields.Text('Comments')

class repair_type(models.Model):
    _name = 'mrp.repair.wes.type'
    
    name = fields.Char('Code', required=True, copy=False, help="Code for this Repairing Type")
    description = fields.Text('Description', required=True, help="Repairing type description")
    cause_id = fields.Many2one('mrp.repair.wes.cause', 'Cause', required=True)
    stage_id = fields.Many2one('mrp.repair.wes.stages', 'Stage', required=True)
    comments = fields.Text('Comments')

class part_number(models.Model):
    _name = 'mrp.repair.wes.partnum'
    
    name = fields.Char('Part number', required=True, copy=False, help="Number for this Part")
    description = fields.Text('Description', required=True, help="Part number description")
    type_id = fields.Many2one('mrp.repair.wes.parttype', 'Type')
    subtype_id = fields.Many2one('mrp.repair.wes.partsubtype', 'Sub Type')
    client = fields.Char('Client')
    rohs = fields.Boolean('ROHS')
    serialized = fields.Boolean('Serialized')
    brand_id = fields.Many2one('mrp.repair.wes.brand', 'Brand')
    cosmetic_stage = fields.Boolean('For Cosmetical Stage')
    is_hdd = fields.Boolean('Is HDD')
    comments = fields.Text('Comments')
    
class part_type(models.Model):
    _name = 'mrp.repair.wes.parttype'
    
    name = fields.Char('Name', required=True, copy=False, help="Name for this Part Type")
    comments = fields.Text('Comments')
    
class part_subtype(models.Model):
    _name = 'mrp.repair.wes.partsubtype'
    
    name = fields.Char('Name', required=True, copy=False, help="Name for this Part SubType")
    type_id = fields.Many2one('mrp.repair.wes.parttype', 'Type')
    description = fields.Text('Description', required=True, help="Part SubType description")
    comments = fields.Text('Comments')

class user_role(models.Model):
    _name = 'mrp.repair.wes.roles'
    
    name = fields.Char('Name', required=True, copy=False, help="Name for this User Role")

class parts_list(models.Model):
    _name = 'mrp.repair.wes.partslist'
    
    name = fields.Char('Name', required=True, copy=False, help="Name for this Parts List")
    cause_id = fields.Many2one('mrp.repair.wes.cause', 'Cause', required=True)
    operations = fields.One2many(
        'mrp.repair.wes.line', 'partslist_id', 'Parts Lines',
        copy=True)
    
class parts_line(models.Model):
    _name = 'mrp.repair.wes.line'
    
    partslist_id = fields.Many2one(
        'mrp.repair.wes.partslist', 'Parts List Reference',
        index=True, ondelete='cascade')
    type = fields.Selection([
        ('add', 'Add'),
        ('remove', 'Remove')], 'Type', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True, domain="[('categ_id.part_prod','=',True)]")
    name = fields.Char('Description', required=True)
    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        index=True, required=True)
    location_dest_id = fields.Many2one(
        'stock.location', 'Dest. Location',
        index=True, required=True)
    product_uom_qty = fields.Float(
        'Quantity', default=1.0,
        digits=dp.get_precision('Product Unit of Measure'), required=True)
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'))
    to_invoice = fields.Boolean('To Invoice')
    tax_id = fields.Many2many(
        'account.tax', 'mrp_repair_wes_line_tax', 'part_line_id', 'tax_id', 'Taxes')
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        self.price_unit = self.product_id.lst_price

class repair_route(models.Model):
    _name = 'mrp.repair.wes.route'
    
    name = fields.Char('Name', required=True, copy=False, help="Name for this Route")
    type_id = fields.Many2one('mrp.repair.wes.type', 'Repairing Type', required=True)
    activities_ids = fields.Many2many(
        'mrp.repair.wes.activity', 'mrp_repair_wes_route_activity', 'route_id', 'activity_id', 'Activities',
        copy=True)

class repair_stages(models.Model):
    _name = 'mrp.repair.wes.stages'
    _order = 'sequence'
    
    sequence = fields.Integer(help="Used to order the states")
    name = fields.Char('Name', required=True, copy=False, help="Name for this Stage")
    comments = fields.Text('Comments')

class repair_state(models.Model):
    _name = 'mrp.repair.wes.state'
    _order = 'sequence'
    
    def next(self):
        tmp = self.search([('sequence','>',self.sequence)])
        if len(tmp) > 0:
            return tmp[0].id
        return 0
    
    def first(self):
        self._cr.execute("select min(sequence) from mrp_repair_wes_state")
        res = self._cr.fetchone()
        if len(res) > 0:
            return res[0]
        return 0
    
    def last(self):
        self._cr.execute("select max(sequence) from mrp_repair_wes_state")
        res = self._cr.fetchone()
        if len(res) > 0:
            return res[0]
        return 0
    
    sequence = fields.Integer(help="Used to order the states")
    name = fields.Char('Description', required=True, copy=False, help="Name for this State")
    comments = fields.Text('Comments')
    type_id = fields.Many2one('mrp.repair.wes.parttype', 'Type')
    subtype_id = fields.Many2one('mrp.repair.wes.partsubtype', 'Sub Type')
    
class repair_activity(models.Model):
    _name = 'mrp.repair.wes.activity'

    name = fields.Char('Name', required=True, copy=False, help="Name for this Task")
    planned_hours = fields.Float(string='Initially Planned Hours', help='Estimated time to do the task.')
    description = fields.Char('Description', required=True, help="Repairing task description")
    tag_ids = fields.Many2many('mrp.repair.wes.tags', string='Tags')
    
class repair_activity_line(models.Model):
    _name = 'mrp.repair.wes.activity.line'
    
    name = fields.Char(related='activity_id.name', readonly=True)
    description = fields.Char(related='activity_id.description', readonly=True)
    state_id = fields.Many2one('mrp.repair.wes.state', 'State', readonly=True)
    required_hours = fields.Float(string='Required Hours', help='Estimated time to do the task(s).')
    planned_hours = fields.Float(related='activity_id.planned_hours', readonly=True)
    date_end = fields.Datetime(string='Date End', readonly=True)
    repair_id = fields.Many2one('mrp.repair', 'Repairing Order', required=True)
    user_id = fields.Many2one('hr.employee', 'User', help="Assigned User")
    activity_id = fields.Many2one('mrp.repair.wes.activity', 'Activity', required=True)
    timesheet_ids = fields.One2many('mrp.repair.wes.timesheet', 'act_line_id', "Timesheet")
    
    repair_state = fields.Selection(related='repair_id.state')
    
    @api.multi
    def action_view_actv(self):
        return {
                'name': _("Activity Details"),
                'type': 'ir.actions.act_window',
                'res_model': 'mrp.repair.wes.activity.line',
                'res_id': self.ids[0],
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': self.env.context
            }
        
    @api.multi
    def action_next(self):
        times = self.env['mrp.repair.wes.timesheet']
        state = self.env['mrp.repair.wes.state']
        if not self.state_id:
            res = state.first()
        else:
            res = self.state_id.next()
        if res == 0:
            self.date_end = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.state_id = res
        if res == state.last():
            self.date_end = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        else:
            times.create({'state_id': self.state_id.id, 'act_line_id': self.id})
    
    @api.onchange('activity_id')
    def onchange_activity_id(self):
        self.planned_hours = self.repair_id.product_qty * self.activity_id.planned_hours

class repair_tags(models.Model):
    """ Tags of repairing's tasks """
    _name = "mrp.repair.wes.tags"
    _description = "Tags of repairing's tasks"

    name = fields.Char(required=True)
    color = fields.Integer(string='Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]
    
class activity_timesheets(models.Model):
    _name = "mrp.repair.wes.timesheet"
    
    act_line_id = fields.Many2one('mrp.repair.wes.activity.line', "Activity")
    state_id = state_id = fields.Many2one('mrp.repair.wes.state', 'State')
    date = fields.Datetime(string='Date Start', readonly=True, default=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
