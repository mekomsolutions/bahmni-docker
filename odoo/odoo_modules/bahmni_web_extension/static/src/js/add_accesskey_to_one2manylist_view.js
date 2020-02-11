odoo.define('bahmni_web_extension.add_accesskey_to_one2manylist_view', function (require) {
"use strict";
var core = require('web.core');
var One2ManyListView = core.one2many_view_registry.get('list');
var form_relational = require('web.form_relational');
var X2ManyList = form_relational.X2ManyList;
var ListView = require('web.ListView');

var One2ManyListViewExtend = form_relational.One2ManyListView.extend({
		pad_table_to: function () {
			console.log("pad_table_to::::::::One2ManyListViewExtend")
	        this._super.apply(this, arguments);
	
	        var add_item_link = this.$current.find("td.oe_form_field_one2many_list_row_add a");
	        add_item_link.attr("accesskey", "I");
	        add_item_link.html("<span>Add an </span><span class='accesskey-char'>I</span><span>tem</span>");
	    }
	});
core.one2many_view_registry
.add('list', One2ManyListViewExtend);

});