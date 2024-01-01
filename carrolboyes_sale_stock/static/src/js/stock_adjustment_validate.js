odoo.define('carrolboyes_sale_stock.InventoryValidationController', function (require) {
    "use strict";

    var InventoryValidationController = require('stock.InventoryValidationController');
    var session = require('web.session');
    var core = require('web.core');
    var qweb = core.qweb;

    InventoryValidationController.include({

        renderButtons: function () {
            var self = this;
            this._super.apply(this, arguments);
            this.getSession().user_has_group('carrolboyes_sale_stock.group_validate_inventory').then(function(has_group) {
                if(!has_group) {
                    self.$buttons.find('.o_button_validate_inventory').addClass('d-none');
                }
            });
            return;
        },

    });
});
