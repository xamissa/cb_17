# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    prod_art_fun_use = fields.Many2many('product.art.function.use', string="Design Name")
    prod_art_design = fields.Many2one('product.art.design', string="Range Name")
    prod_art_range = fields.Many2one('product.art.range', string="Design Subject")
    prod_art_designer = fields.Many2one('product.art.designer', string="Design Application")
    prod_art_prototyper = fields.Many2one('product.art.prototyper', string="Designer")
    #prod_art_prod_developer = fields.Many2one('product.art.product.developer', string="Product/Art/Product Developer/")
    prod_buying_proposed_date = fields.Date(string="Launch Date")
    prod_buying_actual_date = fields.Date(string="Product/Buying/Actual Launch Date/")
    prod_art_materials = fields.Many2many('product.art.materials', string="Materials")
    prod_art_colours = fields.Many2many('product.art.colours', string="Colours")
    prod_art_finish = fields.Many2many('product.art.finish', string="Finish")
    art_note = fields.Text(string='Notes')
    prod_design = fields.Many2many('product.design', string='Design Tags')
    main_categ_id = fields.Many2one('product.main.category', 'Component Classification')
    sub_categ_id = fields.Many2one('product.sub.category', 'Sub Product Category')
    product_group = fields.Many2one('product.group', string="Product group")
    sub_product_group = fields.Many2one('product.sub.group', string="Sub Product group")
    dishwasher_safe = fields.Boolean(string='Dishwasher Safe (Y/N)' , store=True)
    microwavwe_safe = fields.Boolean(string='Microwave Safe (Y/N)', store=True)
    oven_safe = fields.Boolean(string='Oven Safe (Y/N)', store=True)
    food_safe = fields.Boolean(string='Food Safe (Y/N)', store=True)
    sp_care_attr = fields.Text(string='Special Care Attributes')
    p_weight = fields.Char(string='Product Weight(g)', store=True)
    p_length = fields.Char(string='Product Length (mm)', store=True)
    p_width = fields.Char(string='Product Width (mm)', store=True)
    p_height = fields.Char(string='Product Height (mm)', store=True)
    p_diameter = fields.Char(string='Product Diameter (mm)', store=True)
    p_dimension = fields.Char(string='Product Dimension (L x W x H x D) (mm)', store=True)
    pack_length = fields.Char(string='Packaged Length (mm)', store=True)
    pack_width = fields.Char(string='Packaged Width (mm)', store=True)
    pack_height = fields.Char(string='Packaged Height (mm)', store=True)
    pack_diameter = fields.Char(string='Packaged Diameter (mm)', store=True)
    pack_dimensions = fields.Char(string='Packaged Dimensions (L x W x H x D) (mm)', store=True)
    capacity = fields.Char(string='Capacity (ml)', store=True)
    part_weight = fields.Char(string='Part Weight (g)', store=True)
    part_deimension = fields.Char(string='Part Dimensions (L x W x H x D) (mm)', store=True)
    part_capacity = fields.Char(string='Part Capacity (ml)', store=True)
    packaging_elements = fields.Text(string='Packaging Elements')
    warranty_type = fields.Many2one('warranty.type', string="Warranty Type")
    warranty_period = fields.Char(string='Warranty Period')
    sp_comp_attr = fields.Char(string='Special Compliance Attributes')
    long_desc_copy = fields.Text(string='Long Descriptive Copy')
    short_desc_copy = fields.Char(string='Short Descriptive Copy')
    bulletin_copy = fields.Char(string='Bulletin Copy')
    ps_attributes = fields.Char(string='Product & Sales Attributes')
    pack_copy = fields.Char(string='Packaging Copy / Design Blurb')
    ingredients = fields.Char(string='Ingredients')
    assembly_instructions = fields.Char(string='Assembly Instructions')
    warning_copy = fields.Char(string='Warning Copy')
    cu_instructions = fields.Char(string='Care & Usage Instructions')
    in_box = fields.Char(string='What\'s In The Box')
    pairs_with = fields.Char(string='Pairs with')
    upsell = fields.Char(string='Upsell Suggestion')
    merchandising = fields.Char(string='Merchandising Info')
    copy_tags = fields.Char(string='Tags')
    shop_range = fields.Char(string='Shop The Range')
    qr_destination = fields.Char(string='QR Code Destination')
    prod_status = fields.Many2many('product.status', string='Product Status')
    retail_ready = fields.Boolean(string='Retail Ready')
    retail_ready_notes = fields.Char(string='Retail Ready Notes')

    @api.model_create_multi
    def create(self, vals):
        res=super(ProductTemplate, self).create(vals)
        if res.type == 'product':
            res.write({"company_id":self.env.company.id})
        return res

class warrantyType(models.Model):
    _name = "warranty.type"
    _description = "warranty Type"

    name = fields.Char(string="Warranty Type")

class ProductMainCategory(models.Model):
    _name = "product.main.category"
    _description = "Product Main Category"

    name = fields.Char(string="Name")

class ProductSubCategory(models.Model):
    _name = "product.sub.category"
    _description = "Product Sub Category"

    name = fields.Char(string="Name")


class ProductGroup(models.Model):
    _name = "product.group"
    _description = "Product Group"

    name = fields.Char(string="Name")

class SubProductGroup(models.Model):
    _name = "product.sub.group"
    _description = "Product Sub Group"

    name = fields.Char(string="Name")

class ProductProduct(models.Model):
    _inherit = "product.product"

    prod_art_fun_use = fields.Many2one('product.art.function.use', string="Design Name")
    prod_art_design = fields.Many2one('product.art.design', string="Range Name")
    prod_art_range = fields.Many2one('product.art.range', string="Design Subject")
    prod_art_designer = fields.Many2one('product.art.designer', string="Design Application")
    prod_art_prototyper = fields.Many2one('product.art.prototyper', string="Designer")
    #prod_art_prod_developer = fields.Many2one('product.art.product.developer', string="Product/Art/Product Developer/")
    prod_buying_proposed_date = fields.Date(string="Launch Date")
    prod_buying_actual_date = fields.Date(string="Product/Buying/Actual Launch Date/")
    prod_art_materials = fields.Many2many('product.art.materials', string="Materials")
    prod_art_colours = fields.Many2many('product.art.colours', string="Colours")
    prod_art_finish = fields.Many2many('product.art.finish', string="Finish")
    art_note = fields.Text(string='Notes')
    prod_design = fields.Many2many('product.design', string='Design Tags')
    prod_status = fields.Many2many('product.status', string='Product Status')
    retail_ready = fields.Boolean(string='Retail Ready')
    retail_ready_notes = fields.Char(string='Retail Ready Notes')

class ProductArtFunctionUse(models.Model):
    _name = "product.art.function.use"
    _description = "Product Art Function Use"

    name = fields.Char(string="Name")

class ProductArtDesign(models.Model):
    _name = "product.art.design"
    _description = "Product Art Design"

    name = fields.Char(string="Name")

class ProductArtRange(models.Model):
    _name = "product.art.range"
    _description = "Product Art Range"

    name = fields.Char(string="Name")

class ProductArtDesigner(models.Model):
    _name = "product.art.designer"
    _description = "Product Art Designer"

    name = fields.Char(string="Name")

class ProductArtPrototyper(models.Model):
    _name = "product.art.prototyper"
    _description = "Product Art Prototyper"

    name = fields.Char(string="Name")

#class ProductArtProductDeveloper(models.Model):
#    _name = "product.art.product.developer"

#    name = fields.Char(string="Name")

class ProductArtMaterials(models.Model):
    _name = "product.art.materials"
    _description = "Product Art Materials"

    name = fields.Char(string="Name")

class ProductArtColours(models.Model):
    _name = "product.art.colours"
    _description = "Product Art Colours"

    name = fields.Char(string="Name")

class ProductArtFinish(models.Model):
    _name = "product.art.finish"
    _description = "Product Art Finish"

    name = fields.Char(string="Name")

class ProductDesign(models.Model):
    _name = "product.design"
    _description = "Product Design"

    name = fields.Char(string="Name")

class ProductStatus(models.Model):
    _name = "product.status"
    _description = "Product Status"

    name = fields.Char(string="Name")
