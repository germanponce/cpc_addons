# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class fleet_vehicle_category(models.Model):
    _inherit = 'fleet.vehicle.category'

    tip_vehicle = fields.Selection([('plat','Plataforma de Elevación'),
                                    ('mont','Montacargas'),
                                    ('mani','Manipuladores'),
                                    ('tor_ilum', 'Torres de Iluminación'),
                                    ('ofc_mov', 'Oficinas Móviles'),
                                    ('sant', 'Sanitarios'),
                                    ('migt', 'Migitorios')],'Categoria')

class fleet_vehicle(models.Model):
    _name = 'fleet.vehicle'
    _inherit = 'fleet.vehicle'

    @api.depends('product_ids','vehicle_type_id')
    def _get_status_rental(self):
        for rec in self:
            product_ids = []
            status_vehicles = {
            'available': 'Disponible',
            'deliver':'Entregar',
            'collect':'Recoger',
            'rental':'Rentado',
            'service': 'Servicio',
            }
            if rec.product_ids:
                product_ids = [x.id for x in rec.product_ids]
                self.env.cr.execute("""
                    select sale_order.state from sale_order join sale_order_line
                        on sale_order_line.order_id = sale_order.id
                        and sale_order.state not in ('done','cancel','draft')
                        and sale_order_line.product_id in %s;

                    """, (tuple(product_ids),))
                cr_res = self.env.cr.fetchall()
                sale_order_line_ids = [x[0] for x in cr_res]
                if not sale_order_line_ids:
                    tms_mro = self.env['fleet.mro.order']
                    tms_mro_ids = tms_mro.search([('vehicle_id','=',rec.id),('state','!=','done')])
                    if tms_mro_ids:
                        self.status_rental_vehicle = status_vehicles['service']
                    else:
                        self.status_rental_vehicle = status_vehicles['available']
                else:
                    sale_order_line = self.env['sale.order.line']
                    date_act  =  fields.Date.context_today(self)
                    for line in sale_order_line.browse(sale_order_line_ids):
                        if date_act > line.end_date:
                            self.status_rental_vehicle = status_vehicles['collect']
                            break
                        else:
                            picking_ids = self.env['stock.picking'].search([('group_id', '=', line.order_id.procurement_group_id.id)])
                            if not picking_ids:
                                self.status_rental_vehicle = status_vehicles['deliver']
                            all_done = 0
                            all_draft = 0
                            for picking in picking_ids:
                                if picking.state == 'done':
                                    all_done += 1
                                else:
                                    all_draft += 1
                            if all_done < 1:
                                self.status_rental_vehicle = status_vehicles['rental']
                                break
                            if all_done == 0:
                                self.status_rental_vehicle = status_vehicles['deliver']
                                break 
            else:
                self.status_rental_vehicle = status_vehicles['available']

    status_rental_vehicle = fields.Char("Estado del Vehiculo", size=256, compute=_get_status_rental)

    tip_vehicle = fields.Selection([('plat','Plataforma de Elevacion'),
                                    ('mont','Montacargas'),
                                    ('mani','Manipuladores'),
                                    ('tor_ilum', 'Torres de Iluminacion')],'Categoria', related="vehicle_type_id.tip_vehicle", readonly=True)
    tip = fields.Selection([('renta','Renta'),('venta','Venta'),('rent_vent','Renta/Venta')], string="Tipo")

    num_int = fields.Char('Número Interno',size=128)
    num_ser_equi = fields.Char('Número Serie Equipo', size=128)
    num_fac = fields.Char('Número de Factura', size=128)

    hor = fields.Float('Horómetro')

    func = fields.Selection([('com','Combustión'),('elec','Eléctrico')])
    alt_t = fields.Float('Altura de Trabajo (Mts)')
    alt_p = fields.Float('Altura de Plataforma (Mts)')
    cap_car = fields.Float('Capacidad de Carga (Kg)')
    anch = fields.Float('Ancho (Mts)')
    peso = fields.Float('Peso (Ton)')
    fich_tec = fields.Text('Ficha Técnica')

    car_max = fields.Float('Carga Máxima (Ton)')
    alt_max_mas =fields.Float('Altura Máxima de Mástil (Mts)')
    anch_equi = fields.Float('Anchura de Equipo (Mts)')
    larg_equi = fields.Float('Largo del Equipo sin Orquillas')
    alt_equi = fields.Float('Altura de Equipo (Mts)')
    larg_orq = fields.Float('Largo de Orquillas')
    rad_equi = fields.Float('Radio de Équipo')
    tip_llan = fields.Selection([('sol','Sólidas'),
                                    ('sol_neu','Sólidas/Neumáticas'),
                                    ('sol_no','Sólidas (No Marking)')],'Tipo de Llantas')
    desp_lat = fields.Boolean('Desplazamiento Lateral')
    pes_total = fields.Float('Peso Total del Equipo')
    caract = fields.Text('Características')

    max_cap_alt = fields.Float('Máxima Capacidad de Carga en Altura (Ton)')
    alt_max_el = fields.Float('Altura Máxima de Elevación (Mts)')
    alt_veh = fields.Float('Altura de Vehículo (Mts)')
    long_veh = fields.Float('Longitud de Vehículo (Mts)')
    anch_veh = fields.Float('Anchura de Vehículo (Mts)')

    ilum = fields.Float('Ilumintación (Watts)')
    alt_ret = fields.Float('Alt. Mástil Retraido (mts)')
    alt_ele = fields.Float('Alt. Mástil Elevado (mts)')
    longitud = fields.Float('Longitud')
    ancho = fields.Float('Ancho')
    pes = fields.Float('Peso')

    dia = fields.Float('Dia')
    sem = fields.Float('Semana')
    mes = fields.Float('Mes')
    mon = fields.Many2one('res.currency')
    obser = fields.Text('Observaciones')
