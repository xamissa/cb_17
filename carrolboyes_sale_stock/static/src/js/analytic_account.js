odoo.define('carrolboyes_sale_stock.analytic_account', function(require) {
	"use strict";

var ReconciliationRenderers = require('account.ReconciliationRenderer');
var ReconciliationAction = require('account.ReconciliationClientAction');
var ReconciliationModel = require('account.ReconciliationModel');
var LineRenderer = ReconciliationRenderers.LineRenderer;
var StatementAction = ReconciliationAction.StatementAction;
var WarningDialog = require('web.CrashManager').WarningDialog;
var relational_fields = require('web.relational_fields');
var basic_fields = require('web.basic_fields');
var FieldManagerMixin = require('web.FieldManagerMixin');
var core = require('web.core');
var qweb = core.qweb;
var _t = core._t;
var rpc = require('web.rpc');
var analytic_account = '';
var render_create = false;
var analytic_account_set = false;

LineRenderer.include({
    _renderCreate: function (state) {
        var self = this;
        render_create = true;
        console.log("_renderCreate=============");
        return this.model.makeRecord('account.bank.statement.line', [{
            relation: 'account.account',
            type: 'many2one',
            name: 'account_id',
            domain: [['company_id', '=', state.st_line.company_id], ['deprecated', '=', false]],
        }, {
            relation: 'account.journal',
            type: 'many2one',
            name: 'journal_id',
            domain: [['company_id', '=', state.st_line.company_id]],
        }, {
            relation: 'account.tax',
            type: 'many2many',
            name: 'tax_ids',
            domain: [['company_id', '=', state.st_line.company_id]],
        }, {
            relation: 'account.analytic.account',
            type: 'many2one',
            name: 'analytic_account_id',
        }, {
            relation: 'account.analytic.tag',
            type: 'many2many',
            name: 'analytic_tag_ids',
        }, {
            type: 'boolean',
            name: 'force_tax_included',
        }, {
            type: 'char',
            name: 'name',
        }, {
            type: 'float',
            name: 'amount',
        }, {
            type: 'char', //TODO is it a bug or a feature when type date exists ?
            name: 'date',
        }, {
            type: 'boolean',
            name: 'to_check',
        }], {
            account_id: {
                string: _t("Account"),
            },
            name: {string: _t("Label")},
            amount: {string: _t("Account")},
        }).then(function (recordID) {
            self.handleCreateRecord = recordID;
            analytic_account_set = false;
            var record = self.model.get(self.handleCreateRecord);

            self.fields.account_id = new relational_fields.FieldMany2One(self,
                'account_id', record, {mode: 'edit', attrs: {can_create:false}});

            self.fields.journal_id = new relational_fields.FieldMany2One(self,
                'journal_id', record, {mode: 'edit'});

            self.fields.tax_ids = new relational_fields.FieldMany2ManyTags(self,
                'tax_ids', record, {mode: 'edit', additionalContext: {append_type_to_tax_name: true}});

            self.fields.analytic_account_id = new relational_fields.FieldMany2One(self,
                'analytic_account_id', record, {mode: 'edit'});

            self.fields.analytic_tag_ids = new relational_fields.FieldMany2ManyTags(self,
                'analytic_tag_ids', record, {mode: 'edit'});

            self.fields.force_tax_included = new basic_fields.FieldBoolean(self,
                'force_tax_included', record, {mode: 'edit'});

            self.fields.name = new basic_fields.FieldChar(self,
                'name', record, {mode: 'edit'});

            self.fields.amount = new basic_fields.FieldFloat(self,
                'amount', record, {mode: 'edit'});

            self.fields.date = new basic_fields.FieldDate(self,
                'date', record, {mode: 'edit'});

            self.fields.to_check = new basic_fields.FieldBoolean(self,
                'to_check', record, {mode: 'edit'});

            var $create = $(qweb.render("reconciliation.line.create", {'state': state, 'group_tags': self.group_tags, 'group_acc': self.group_acc}));
            self.fields.account_id.appendTo($create.find('.create_account_id .o_td_field'))
                .then(addRequiredStyle.bind(self, self.fields.account_id));
            self.fields.journal_id.appendTo($create.find('.create_journal_id .o_td_field'));
            self.fields.tax_ids.appendTo($create.find('.create_tax_id .o_td_field'));
            self.fields.analytic_account_id.appendTo($create.find('.create_analytic_account_id .o_td_field'))
                .then(addRequiredStyle.bind(self, self.fields.analytic_account_id));
            self.fields.analytic_tag_ids.appendTo($create.find('.create_analytic_tag_ids .o_td_field'));
            self.fields.force_tax_included.appendTo($create.find('.create_force_tax_included .o_td_field'));
            self.fields.name.appendTo($create.find('.create_label .o_td_field'))
                .then(addRequiredStyle.bind(self, self.fields.name));
            self.fields.amount.appendTo($create.find('.create_amount .o_td_field'))
                .then(addRequiredStyle.bind(self, self.fields.amount));
            self.fields.date.appendTo($create.find('.create_date .o_td_field'));
            self.fields.to_check.appendTo($create.find('.create_to_check .o_td_field'));
            self.$('.create').append($create);

            function addRequiredStyle(widget) {
                widget.$el.addClass('o_required_modifier');
            }
        });
    },

    _onFieldChanged: function (event) {
        event.stopPropagation();
        var self = this;
        var fieldName = event.target.name;
        var analytic = '';
        if(fieldName === 'analytic_account_id')
        {
            analytic = event.data.changes.analytic_account_id.id;
        }
        if (analytic) {
            analytic_account_set = true;
        }
        self._super.apply(this, arguments);
    },

    _onSelectMoveLine: function (event) {
	render_create = false;
        var $el = $(event.target);
        $el.prop('disabled', true);
        this._destroyPopover($el);
        var moveLineId = $el.closest('.mv_line').data('line-id');
        var val1 = rpc.query({
            model: 'account.move.line',
            method: 'read',
            args: [[moveLineId]],
            }).then(function (a1) {
                analytic_account = a1[0]['analytic_account_id'];
        });
        this.trigger_up('add_proposition', {'data': moveLineId});
    },


   _onValidate: function () {
        var handle = this.handle;
        var current_line = this.model.getLine(handle);

        //if (analytic_account === false && analytic_account_set === false){
        console.log(render_create+"::::render_create::::::::"+analytic_account_set);
        if (render_create === true && analytic_account_set === false){
            new WarningDialog(self, {
                title: _t("Warning"),
            }, {
            message: _t("Please Set the Analytic Acc. for line.")
            }).open();
            return false;
        }
        this.trigger_up('validate');
    }

});

});
