# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################
from itertools import groupby
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import requests
from datetime import datetime,timezone
from odoo.exceptions import UserError, ValidationError , AccessError

import base64



class crypto_data_date(models.Model):
    _name = "crypto.data.date"

    price = fields.Float(string="Price")
    price_date = fields.Datetime(string="Price Date")
    crypto_id = fields.Many2one('crypto.data',string="crypto Id")
    name= fields.Char(string="Name")



class crypto_data(models.Model):

    _name = "crypto.data"


    name = fields.Char(string="Name")
    price = fields.Float(string="Price")
    price_date = fields.Datetime(string="Price Date")
    market_cap = fields.Float(string="Market Cap")
    market_cap_dominance = fields.Float(string="Market cap Dominance")
    rank = fields.Integer(string="Rank")
    img = fields.Binary(string="Logo")
    price_ids = fields.One2many('crypto.data.date','crypto_id',string="Price History")
    id_code = fields.Char(string="Code")
    currency_id = fields.Many2one( 
        'res.currency', string='Currency') 

    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")
    image_url = fields.Char(string='Image URL', required=True)
    image_1920 = fields.Binary(string='Image', compute='_compute_image', store=True, attachment=False)
    


    @api.depends('image_url')
    def _compute_image(self):
        
        for record in self:
            image = None
            if record.image_url:
                url_field = base64.b64encode(requests.get(record.image_url.strip()).content).replace(b'\n', b'')

                record.update({'image_1920': url_field })

            else :

                record.update({'image_1920': False })



    def view_graph(self):

        action = self.env["ir.actions.act_window"]._for_xml_id("crypto_module.date_action_view_order_graph_date")
        action['domain'] = [('id','in',self.price_ids.ids)]
        action['context'] = {'search_default_group_by_date': 1}
        return action




    def calculate_price_date(self) :

        start_day = str(self.start_date.day)

        if len(start_day) <2 :
            start_day = "0" + start_day

        start_month = str(self.start_date.month)

        if len(start_month) <2 :
            start_month = "0" + start_month


        end_day = str(self.end_date.day)

        if len(end_day) <2 :
            end_day = "0" + end_day

        end_month = str(self.end_date.month)

        if len(end_month) <2 :
            end_month = "0" + end_month



        url_date = "https://api.nomics.com/v1/exchange-rates/history?key=b1e6e192bca016b2cddfb98b79510f191ad4124f&currency="+self.id_code+"&start="+ str(self.start_date.year)+"-"+start_month+"-"+start_day+"T00%3A00%3A00Z&end="+str(self.end_date.year)+"-"+end_month+"-"+end_day+"T00%3A00%3A00Z"

        headers = {'Content-Type' : 'application/json' }       
        d=requests.get(url=url_date,headers= headers)

        print ("dddddddddd",d)
        if (d.status_code == 200):


            print ("=============",d.json())
            self.price_ids.unlink()


            for j in d.json() :

                rate = float(j.get('rate'))
                time = j.get('timestamp')

                date_rate = datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')



                self.env['crypto.data.date'].create({'price': rate,'price_date' : date_rate ,'crypto_id' : self.id,'name' : self.name})


        print ("======not=========",self.name)

        return






class token_detail(models.Model):

    _name = "user.data.crypto"


    experience = fields.Selection([('never','Never Invested'),('zero_three','0 To 3 years Of Experience'),('three_more','3+ years Of Experience')],string="Experience")
    risk_amount = fields.Float(string="Amount",required=True)
    start_date = fields.Datetime(string="Start Date",required=True)
    end_date = fields.Datetime(string="End Date",required=True)
    all_data = fields.Boolean(string="Get All Data")
    currency_id = fields.Many2one( 
        'res.currency', string='Currency') 




    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        

        currency_id = self.env['res.currency'].search([('name','=','USD')],limit=1)
        print ("kkkkkkk",currency_id)
        res['currency_id'] = currency_id.id

        
        return res



    def validate_data(self) :


        if self.end_date > fields.Datetime.now() or self.start_date > fields.Datetime.now() :

            raise UserError("Start Date Or End Date Should Be Before Current Time.")

        if  self.end_date < self.start_date :

            raise UserError("Provide Valid Start Date and End Date")

        if self.risk_amount <= 0 :
            raise UserError("Risk Amount Should Be More than 0")

        return







    def submit_data(self) :

        self.validate_data()

        url = "https://api.nomics.com/v1/currencies/ticker?key=b1e6e192bca016b2cddfb98b79510f191ad4124f&ids=&interval=1d,30d&convert=CAD&per-page=200&page=1"

        ids = []

        r=requests.get(url)
        data_obj = self.env['crypto.data']

        data_obj.search([]).unlink()

        for i in r.json() :


            date = datetime.strptime(i.get('price_date'), '%Y-%m-%dT%H:%M:%SZ')


            record = data_obj.create({

                'name' : i.get('name'),
                'price' : i.get('price'),
                'price_date' : date,
                'id_code':i.get('id'),
                'market_cap' : i.get('market_cap'),
                'market_cap_dominance' : i.get('market_cap_dominance'),
                'rank' : i.get('rank'),
                'start_date' : self.start_date,
                'end_date' : self.end_date,
                'currency_id':self.currency_id.id,
                'image_url':i.get('logo_url'),


                })




            record.calculate_price_date()

            price_diff = 0


            if record.price_ids :

                price_diff = record.price_ids[0].price - record.price_ids[-1].price



            if price_diff  :

                ids.append(record.id)





            





             


        action = self.env["ir.actions.act_window"]._for_xml_id("crypto_module.crypto_datq_action_stored")
        action['domain'] = [('id','in',ids)]
        action['context'] = {'graph_mode':'pie'}

        
        if self.all_data == True :

            action = self.env["ir.actions.act_window"]._for_xml_id("crypto_module.crypto_datq_action_stored")
            action['context'] = {'graph_mode':'pie'}

        print (action)
        return action

         



    