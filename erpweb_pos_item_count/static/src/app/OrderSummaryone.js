/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { roundPrecision as round_pr } from "@web/core/utils/numbers";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Order, Orderline, Payment } from "@point_of_sale/app/store/models";
import { useService } from "@web/core/utils/hooks";

patch(OrderWidget.prototype, {

    setup() {
        super.setup();
        this.pos = usePos();
        },
    get order() {
        return this.pos.get_order();
    },
    _order_line_count(order){

        var orderlines =  order ? order.get_orderlines() : []
        var item_counter = 0.0
        orderlines.forEach(function (order_line) {
            if (order_line.product.display_name != 'DISCOUNT'){
                item_counter++;
            }
        });
        return item_counter
    },
    _total_qty_count(order){
        var orderlines =  order ? order.get_orderlines() : []
        var total_qty = 0.0
        orderlines.forEach(function (order_line) {
            if (order_line.product.display_name != 'DISCOUNT'){
                total_qty += order_line.quantity;
            }
        });
        return total_qty
    },
    _total_discount_count(order){

        const ignored_product_ids = []
        var orderlines =  order ? order.get_orderlines() : []
        return round_pr(
            orderlines.reduce((sum, orderLine) => {
                if (!ignored_product_ids.includes(orderLine.product.id)) {
                    sum +=
                        orderLine.getUnitDisplayPriceBeforeDiscount() *
                        (orderLine.get_discount() / 100) *
                        orderLine.get_quantity();
                    if (orderLine.display_discount_policy() === "without_discount") {
                        sum +=
                            (orderLine.get_taxed_lst_unit_price() -
                                orderLine.getUnitDisplayPriceBeforeDiscount()) *
                            orderLine.get_quantity();
                    }
                }
                return sum;
            }, 0),
            this.pos.currency.rounding
        );
    },
});