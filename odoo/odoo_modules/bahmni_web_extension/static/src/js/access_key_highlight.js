odoo.define('bahmni_web_extension.access_key_highlight', function (require) {
"use strict";
var core = require('web.core');

var ViewManager = require('web.ViewManager');
var FormRenderingEngine = require('web.FormRenderingEngine');

var _t = core._t;
var _lt = core._lt;

ViewManager.include({
	 start: function() {
         this._super.apply(this, arguments);
         var createUnderlinedAccessKeyElem = function(text, accesskey) {
             if(text == null) {
                 return null;
             } else if(accesskey == null || accesskey == "") {
                 return text;
             }
             var i = text.toLowerCase().indexOf(accesskey.toLowerCase());
             return "<span>" + text.slice(0, i) + "</span><span class='accesskey-char'>" + accesskey + "</span><span>" + text.slice(i+1) + "</span>";
         };
//         console.log(" $('[accesskey]')::::::::::::::", $("[accesskey]"))
         $("[accesskey]").each(function(index, elem) {
//        	 console.log("elem:::::::::::::::",elem);
//        	 console.log(":::::::elem.innerText::::::", elem.innerText);
//        	 console.log(":::::::elem.accessKey::::::", elem.accessKey);
//        	 console.log(":::::::elem.ulKey::::::::::", elem.ulKey);
             var newInnerHtml = createUnderlinedAccessKeyElem(elem.innerText, elem.accessKey);
             if(newInnerHtml != null) {
                 elem.innerHTML = newInnerHtml;
             }
         });
     },

	});

FormRenderingEngine.include({
		process_label: function($label) {
		    var name = $label.attr("for"),
		        field_orm = this.fvg.fields[name];
		    var dict = {
		        string: $label.attr('string') || (field_orm || {}).string || '',
		        help: $label.attr('help') || (field_orm || {}).help || '',
		        _for: name ? _.uniqueId('o_field_input_') : undefined,
		        accesskey: $label.attr('accesskey'),
		        ulkey: $label.attr('ulkey')
		    };
		    var $new_label = this.render_element('FormRenderingLabel', dict);
		    $label.before($new_label).remove();
		    this.handle_common_properties($new_label, $label);
		    if (name) {
		        this.labels[name] = $new_label;
		    }
		    return $new_label;
		},
		preprocess_field: function($field) {
	        var self = this;
	        var name = $field.attr('name'),
	            field_colspan = parseInt($field.attr('colspan'), 10),
	            field_modifiers = JSON.parse($field.attr('modifiers') || '{}');
	
	        if ($field.attr('nolabel') === '1')
	            return;
	        $field.attr('nolabel', '1');
	        var found = false;
	        this.$form.find('label[for="' + name + '"]').each(function(i ,el) {
	            $(el).parents().each(function(unused, tag) {
	                var name = tag.tagName.toLowerCase();
	                if (name === "field" || name in self.tags_registry.map)
	                    found = true;
	            });
	        });
	        if (found)
	            return;
	
	        var $label = $('<label/>').attr({
	            'for' : name,
	            "modifiers": JSON.stringify({invisible: field_modifiers.invisible}),
	            "string": $field.attr('string'),
	            "help": $field.attr('help'),
	            "class": $field.attr('class'),
	            "accesskey": $field.attr('accesskey'),
	            "ulkey": $field.attr('ulkey')
	        });
	        $label.insertBefore($field);
	        if (field_colspan > 1) {
	            $field.attr('colspan', field_colspan - 1);
	        }
	        return $label;
	    },
	});
})