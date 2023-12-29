/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { Order, Orderline } from "@point_of_sale/app/store/models";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";

let check_pay = true;
let check_dol = true;

patch(ProductScreen.prototype, {

async checkPswd(){
	let res = false;
	const { confirmed, payload } = await this.popup.add(NumberPopup, {
				title: _t('Manager Password'),
				isPassword: true,
	});
	if (confirmed) {
		let user_passd;
		let secondary_user_passd;
		let users = this.pos.config.pos_user_id;
		if (this.pos.user.id === users[0]) {
			user_passd = this.pos.user.pos_security_pin;
		}
		let secondary_users = this.pos.config.pos_secondary_user_id;
		if (this.pos.user.id === secondary_users[0]) {
			secondary_user_passd = this.pos.user.pos_security_pin;
		}
		
		if (payload == user_passd || payload == secondary_user_passd){
			res =  true;
		}else{
			this.popup.add(ErrorPopup, {
						title: _t('Invalid Password'),
						body: _t('Wrong Password'),
					});
			return false;
		}
	}
	return res;
},

async onClickPay() {
	let config = this.pos.config;
	let config_otp = config.one_time_valid;
	let result = true;
	let order = this.env.pos.get_order();

	if(config.pos_payment_perm && check_pay){
		if(config_otp){
			result = await this.checkPswd();
		}
		if(!config_otp){
			result = await this.checkPswd();
		}
	}
	if(result){
		super._onClickPay();
	}
},

async _setValue(val) {
    const { numpadMode } = this.pos;
    let config = this.pos.config;
    let config_otp = config.one_time_valid;
    let result = true;
    let order = this.pos.get_order();
    const selectedLine = this.currentOrder.get_selected_orderline();
    if (selectedLine) {
        if (numpadMode === "quantity") {
            if (val === "remove") {
            	if(config.pos_order_line_delete){
	            		alert("you can not delete order line. Please create a new order")
	            		return;
	            }
	            else{
                	this.currentOrder.removeOrderline(selectedLine);}	
            } else {
            	if(val < 0)
            	{
            		if(config_otp){
                    	result = await this.checkPswd();
                    }
                    if(!config_otp){
                        result = await this.checkPswd();
                        if(result == false)
                        {
                            selectedLine.set_quantity(1);
                            return;
                        }
                        selectedLine.set_quantity(val);
                    }
            	}
            	else{
            		selectedLine.set_quantity(val); 
            	}
                
            }
        } else if (numpadMode === "discount") {
        	if(config.pos_set_max_discount != 0)
            {
                if (val > config.pos_set_max_discount)
                {
                    if(config_otp)
                    {
                        result = await this.checkPswd();
                    }
                    if(!config_otp)
                    {
                        result = await this.checkPswd();
                        console.log("========================",result)
                        if(result == false)
                        {
                            selectedLine.set_discount(0);
                            this.numberBuffer.reset();
                            return;
                        }
                    }
                }
            }
            selectedLine.set_discount(val);
        } else if (numpadMode === "price") {
            selectedLine.price_type = "manual";
            selectedLine.set_unit_price(val);
        }
    }
}

});