# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
import pprint
import random
import requests
import string
import requests
import json
from dateutil.parser import parse
from requests.structures import CaseInsensitiveDict
from odoo import fields, models, api, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError


class data_log(models.Model):

    _name = 'data.log'
    _description = 'data.log'

    name = fields.Char(string='Name')
    log_ids = fields.One2many('waybill.data.log', 'waybill_data',string='Logs')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('common.log.waybill.data') or '/'
        vals['name'] = seq
        return super(data_log, self).create(vals)


class waybill_data_log(models.Model):
    _name = 'waybill.data.log'
    _description = 'waybill.data.log'

    name = fields.Char(string='Name')
    payload = fields.Text(string='Payload')
    error = fields.Text(string='Message')
    etype = fields.Selection([('fail', 'Fail'), ('done', 'Done')],string='State')
    waybill_data = fields.Many2one('data.log', string='Waybill Data')

class carrolboyes_getdata(models.Model):
    _name = 'postcode.get.data'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Postcode Data'

    name = fields.Char(string='Account Number', default='D2C180')
    password = fields.Char(string='Password', default='D2C180')
    account_number=fields.Char(string="Account Name")
    order_type = fields.Selection([('magento', 'Magento Order'), ('takealot', 'Take a Lot Order'), ('other', 'Others')], string='Type of Order')
    token = fields.Char(string='Token', copy=False, readonly=True)

    def get_token(self):
        headers = {'Content-Type': 'application/json'}
        #url='http://swatws.dawnwing.co.za/dwwebservices/v2/uat/api/Token'
        url=''
        payload = json.dumps({'userName': self.name,'password': self.password})
        resp = requests.post(url, headers=headers, data=payload)
        if resp.status_code == 200:
            self.token = resp.text
            self.message_post(body=_('Token Generated'))
        else:
            self.message_post(body=_('Token Error '))
        return resp.text

    def get_data(self):
        waybill_log = self.env['waybill.data.log']
        waybill_get_data = self.env['carrol.postcode']
        log_data = self.env['data.log'].create({'name': 'Test'})
        #url='http://swatws.dawnwing.co.za/dwwebservices/v2/uat/api/Token'
        url=''

        payload = json.dumps({'userName': self.name,'password': self.password})
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=payload)
        res=response.json()
        headers = {'Authorization': 'Bearer %s' % res.get('token'),'Content-Type': 'application/json'}
        #url='http://swatws.dawnwing.co.za/dwwebservices/live/api/district'
        url=''
        resp = requests.request("POST", url, headers=headers)
        if resp.status_code == 200:
            res = resp.json()
            for r in res:
                data1 = waybill_get_data.search([('name','=', r['name']),('postcode','=',r['postCode']),('city','=',r['city']),('state','=',r['state'])])

                if not data1:
                    log_book_id = waybill_get_data.create({
                        'name': r['name'],
                        'postcode': r['postCode'],                        
                        'city': r['city'],                        
                        'state': r['state'],
                        'payload':r,
                        })
        return True

class carrolboyes_postcode(models.Model):
    _name = 'carrol.postcode'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']    
    _description = 'Postcode'

    name = fields.Char(string="Name")
    payload = fields.Text(string='Payload')
    postcode = fields.Char(string="PostCode")
    city = fields.Char(string="City")
    state = fields.Char(string="State")
    token = fields.Char(string='Token', copy=False, readonly=True)

class CarrolResPartner(models.Model):

    _inherit = 'res.partner'
    waybill_id=fields.Many2one('carrol.postcode',string='DPD Address',compute="dpd_address")
    waybill_postcode=fields.Char(string='DPD Postcode')
    waybill_city=fields.Char(string='DPD City')
    waybill_state=fields.Char(string='DPD State')


    @api.depends('city','state_id','zip')
    def dpd_address(self):
        dpd_add=False
        dpd_add2=False
        dpd_add3=False
        self.waybill_id=False
        self.waybill_postcode=False
        self.waybill_city=False
        self.waybill_state=False
        if self.state_id and self.zip and self.city and self.street2:
            dpd_add=self.env['carrol.postcode'].search([('state','ilike',self.state_id.name.upper()),('postcode','=',self.zip),('city','=ilike',self.city.upper()),('name','=ilike',self.street2.upper())],limit=1)
        if self.state_id and self.zip and self.city:
           dpd_add2=self.env['carrol.postcode'].search([('state','ilike',self.state_id.name.upper()),('postcode','=',self.zip),('city','=ilike',self.city.upper())],limit=1)
        if self.state_id and self.zip:
            dpd_add3=self.env['carrol.postcode'].search([('state','ilike',self.state_id.name.upper()),('postcode','=',self.zip)],limit=1)
        if dpd_add:
            self.waybill_id=dpd_add.id
            self.waybill_postcode=dpd_add.postcode
            self.waybill_city=dpd_add.city
            self.waybill_state=dpd_add.state
        elif dpd_add2:
            self.waybill_id=dpd_add2.id
            self.waybill_postcode=dpd_add2.postcode
            self.waybill_city=dpd_add2.city
            self.waybill_state=dpd_add2.state
        elif dpd_add3:
            self.waybill_id=dpd_add3.id
            self.waybill_postcode=dpd_add3.postcode
            self.waybill_city=dpd_add3.city
            self.waybill_state=dpd_add3.state
       
        
        
    
class CarrolStockPicking(models.Model):

    _inherit = 'stock.picking'

    waybill_id=fields.Many2one('carrol.postcode',string='DPD Address',compute="waybill_dpd_address")
    waybill_postcode=fields.Char(string='DPD Postcode')
    waybill_city=fields.Char(string='DPD City')
    waybill_state=fields.Char(string='DPD State')
    tracking_ref=fields.Char(string="Tracking Number",compute="set_tracking")

    @api.depends('waybill_id')
    def waybill_dpd_address(self):
        dpd_add=self.env['res.partner'].search([('id','=',self.partner_id.id)])
        self.waybill_id=dpd_add.waybill_id
        self.waybill_postcode=dpd_add.waybill_postcode
        self.waybill_city=dpd_add.waybill_city
        self.waybill_state=dpd_add.waybill_state
    

    def set_tracking(self):
        self.tracking_ref=self.carrier_tracking_ref

    def carrol_waybills(self):
        if not self.sale_id:
            raise UserError(_('Sale order is not set.'))
        if self.magento_instance_id:
            type1 = 'magento'        
        else:
            raise UserError(_('Please configure Magento Instance in this picking.'))
        get_token= self.env['postcode.get.data'].search([('order_type','=',type1)],limit=1)    
        #url='http://swatws.dawnwing.co.za/dwwebservices/v2/uat/api/Token'
        url=''
        payload = json.dumps({'userName': get_token.name,'password': get_token.password})
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=payload)
        res=response.json()
        headers = {'Authorization': 'Bearer %s' % res.get('token'),'Content-Type': 'application/json'}
        #waybill_tracking_number='OY'+self.waybill_number
        s_id_len = len(self.sale_id.name) + 2
        str1 = ''
        if s_id_len < 13 :
            rem_len = 12 - s_id_len
            waybill_tracking = 'OY' + self.sale_id.name
            for r in range(0,rem_len):
                str1 += '0'
        waybill_tracking_number = waybill_tracking + str1
        #url = 'http://api.inboundfnf.co.za/api/InhouseUpload/ImportPartialWaybill/'+ waybill_tracking_number
        url = ""
        data=json.dumps({
               "WaybillNo": waybill_tracking_number,
               "Account": get_token.name, #"D2C180",
               "Service": "ECON",
               "WaybillType": 2,
               "Packets": 0,
               "Department": "",
               "Insurance": 0.0,
               "Transporter": "",
               "Sender": {
                    "Consignor": self.company_id.name,
                    "StreetNo": self.company_id.street2 or '',
                    "StreetName": self.company_id.street or '',
                    # "Complex": "emerald",
                    # "UnitNo": "565",
                    "Suburb": self.company_id.city or '',
                    "Town": self.company_id.city or '',
                    "PostCode": self.company_id.zip or '',
                    "StoreCode": "",
                    "Latitude": "",
                    "Longitude": ""
                },
               "Consignee": {
                    "Consignee": self.partner_id.name,
                    "StreetNo": self.partner_id.street or '',
                    "StreetName": self.partner_id.street2 or '',
                    # "Complex": "test",
                    # "UnitNo": "56",
                    "Suburb": self.partner_id.waybill_id.name or '',
                    "Town": self.partner_id.waybill_city or '',
                    "PostCode": self.partner_id.waybill_postcode or '',
                    "StoreCode": "",
                    "Latitude": "",
                    "Longitude": ""
               },
               "Parcels": [],
               "References": [{
                    "ReferenceNo": "",
                    "ReferenceType": "",
                    "Pages": 0,
                    "Document": ""
                }],
               "Notes": [{
                    "Message": ""
                    }],
               "SpecialInstructions": [],
               "Contacts": [{
                    "Firstname": self.partner_id.name,
                    "Surname": "",
                    "Telephone": self.partner_id.phone or self.partner_id.mobile or '',
                    "Mobile": self.partner_id.mobile or self.partner_id.phone or '',
                    "Mail": self.partner_id.email or '',
                    "NationalID": ""
                }],
               "Content": "",
               "UniqueReference": ""
            })
        response = requests.request("POST", url, headers=headers, data=data)

        if response.status_code == 200:
            #dpd_carrier = self.env.ref('carrolboyes_waybill.dpd_delivery_carrier').id
            self.write({'carrier_tracking_ref':waybill_tracking_number,'carrier_id':46})
        return True
