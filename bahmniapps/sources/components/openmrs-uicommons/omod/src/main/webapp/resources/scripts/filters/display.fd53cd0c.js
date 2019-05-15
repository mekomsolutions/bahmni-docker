angular.module('uicommons.filters').

    /*
     * If input is an object with a 'display' property, return that property.
     * Otherwise, use the emr.js function to translate (optional) prefix + input, and return the translation.
     * If no translation is found, just return input.
     * (If input is an array, these rules will be applied to each element, and they'll be joined with ", ".)
     */
    filter('omrsDisplay', function() {
        var displayOne = function(input, prefix) {
            if (input && input.display) {
                return input.display;
            }
            if (input && input.uuid) {
                input = input.uuid;
            }
            var code = prefix ? prefix + input : input;
            return emr.message(code, input);
        }

        return function(input, prefix) {
            if (angular.isArray(input)) {
                return _.map(input, function(item) {
                    return displayOne(item, prefix);
                }).join(", ");
            }
            else {
                return displayOne(input, prefix);
            }
        }
    });