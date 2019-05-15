/*
 * The contents of this file are subject to the OpenMRS Public License
 * Version 1.0 (the "License"); you may not use this file except in
 * compliance with the License. You may obtain a copy of the License at
 * http://license.openmrs.org
 *
 * Software distributed under the License is distributed on an "AS IS"
 * basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
 * License for the specific language governing rights and limitations
 * under the License.
 *
 * Copyright (C) OpenMRS, LLC.  All Rights Reserved.
 */

var ExitHandlers = {

    // a widget can dynamically set "do-not-exit" or "do-not-exit-once" classes on the field to indicate we should not
    // exit the field. "do-not-exit-once" will be cleared after a single exit attempt.
    'manual-exit': {
        handleExit: function(fieldModel) {
            var doNotExit = fieldModel.element.hasClass('do-not-exit') || fieldModel.element.hasClass('do-not-exit-once');
            fieldModel.element.removeClass('do-not-exit-once');
            return !doNotExit;
        }
    },

    'leading-zeros': {
        handleExit: function(fieldModel) {
            var val = fieldModel.element.val();
            if (val) { // if the field is blank, leave it alone
                var maxLength = parseInt(fieldModel.element.attr('maxlength'));
                if (maxLength > 0) {
                    while (val.length < maxLength) {
                        val = "0" + val;
                    }
                    fieldModel.element.val(val);
                }
            }
            return true;
        }
    }

};