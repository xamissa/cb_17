/** @odoo-module */

let emp_no = false

import { Order, Orderline } from "@point_of_sale/app/store/models";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";

patch(PosStore.prototype, {

    getReceiptHeaderData(order) {
        const json = super.getReceiptHeaderData(...arguments);        
        json.emp_registartion_number = this.emp_no;       
        return json;
    },

    });


patch(Order.prototype, {
        setup(_defaultObj, options) {
            super.setup(...arguments);
            this.total_items = this.get_total_items() || 0;
            this.total_qty = this.get_total_qty() || 0;
            this.emp_registartion_number = this.get_emp_registartion_number() || false;

        },
        get_total_items: function() {
            var total_items = 0
            this.orderlines.forEach(function (line) {
                 if (line.product.display_name != 'DISCOUNT'){
                    total_items ++;
                }
            });
            return total_items
        },
        get_total_qty: function() {
            var total_qty = 0
            this.orderlines.forEach(function (line) {
                if (line.product.display_name != 'DISCOUNT'){
                    total_qty += line.quantity
                }
            });
            return total_qty
        },
        async get_emp_registartion_number(){

            var cashier = this.pos.get_cashier();
            try
            {
                const notification = await this.env.services.orm.silent
                .call('hr.employee', 'get_emp_registartion_number',[cashier.id]).then(result=> {
                    if (result)
                        this.pos.emp_no = result
                });
                return this.pos.emp_no
            }
            catch (error)
            {
                throw error;
            }           
        },
        export_for_printing() {
            const json = super.export_for_printing(...arguments);
            this.get_emp_registartion_number();
            json.total_items = this.get_total_items();
            json.total_qty = this.get_total_qty();
            json.emp_registartion_number = this.pos.emp_no;
            return json;
        },
    });
  
