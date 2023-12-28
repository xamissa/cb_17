/** @odoo-module */


import { patch } from "@web/core/utils/patch";
import { Order, Orderline } from "@point_of_sale/app/store/models";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { PosStore } from "@point_of_sale/app/store/pos_store";

    patch(PosStore.prototype, {
         async _processData(loadedData) {
            await super._processData(...arguments);
            this.pos_order_line = loadedData["pos.order.line"];
            }
    });

    patch(ProductScreen.prototype, {
        _setValue(val) {
            const { numpadMode } = this.pos;
            if (numpadMode === 'price') {
                var selected_orderline = this.currentOrder.get_selected_orderline();
                selected_orderline.change_price = true;
            }
            super._setValue(val);
            }
    });

    patch(Orderline.prototype, {
        setup() {
            super.setup(...arguments);
            this.change_price = false;
        },
        export_as_JSON() {
            var self = this;
            const result = super.export_as_JSON(...arguments);
            result.change_price = self.change_price;
            return result;
        },
    });

