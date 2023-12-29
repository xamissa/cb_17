/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";

let check_close = true;

patch(Navbar.prototype, {

	setup() {
        super.setup(...arguments);
            
    },
    async checkPswd(){
				let self = this;
				let res = false;
				const { confirmed, payload } = await this.popup.add(NumberPopup, {
					title: _t('Manager Password'),
					isPassword: true,
				});
				if (confirmed) {
					let user_passd;
					let users = this.pos.config.pos_user_id;
					if (this.pos.user.id === users[0]) {
						user_passd = this.pos.user.pos_security_pin;
					}
					if (payload == user_passd){
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
	async closeSession() {
        let self = this;
				let config = this.pos.config;
				let config_otp = config.one_time_valid;
				let result = true;
				let order = this.pos.get_order();
				if(config.pos_close_pos && check_close){
					if(config_otp){
						result = await self.checkPswd();
					}
					if(!config_otp){
						result = await self.checkPswd();
					}
				}

				if(result){
					check_close = false;
					super.closeSession();
				}
    },
});
	