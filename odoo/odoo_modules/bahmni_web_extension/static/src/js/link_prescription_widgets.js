odoo.define('bahmni_web_extension.link_prescription_widget', function(require) {
"use strict";

var core = require('web.core');
var formats = require('web.formats');
var form_widgets = require('web.form_widgets');
var FieldChar = core.form_widget_registry.get('char');

// Field in which the user can both type normally and scan barcodes

var link_prescription = FieldChar.extend({
	template: "link_prescription",
    init: function(parent, action) {
    	console.log("link_prescription::::::::::::",  parent)
        this._super.apply(this, arguments);
        this._start = null;
        this.parent = parent;
   },

   start: function() {
        this._super.apply(this, arguments);
        //console.log(">>>>>>>>>>", $('#latest-prescription'))
        this.parent.$el.find('.oe_web_example').replaceWith('<button name="latest-prescription" type="object" class="btn btn-sm" id="latest-prescription" accesskey="P">Latest Prescription</button>');
        this.parent.$el.find('#latest-prescription').click($.proxy(function() {
            if(this.parent.datarecord.partner_uuid != null) {
                this.openLatestPrescription(this.parent.datarecord.partner_uuid);
            } else {
                alert("This patient does not have a proper ID to show latest prescription. Please use clinical app.");
            }
        }, this));
    },

    openLatestPrescription: function(partner_uuid) {
        window.open("https://" + window.location.hostname + "/bahmni/clinical/#/default/patient/" + partner_uuid + "/dashboard/treatment");
    },
});

core.form_widget_registry.add('link-prescription', link_prescription);

return {
	link_prescription: link_prescription,
};

});
