var restUtils = angular.module( "uicommons.RESTUtils", [] );

restUtils.factory("RESTErrorResponse", function() {

    function RESTErrorResponse(response) {
        this.response = response;
    }

    RESTErrorResponse.prototype = {

        getStatus: function () {
            return this.response.status;
        },

        /**
         * Returns an array of the messages
         * associated with the response (suitable, for instance, for display via an angular ng-repeat)
         *
         * If this response object has global or field level errors, it will return all those display messages to the array,
         * otherwise it will add the top-level message
         *
         * Note that we do *not* return the top-level message if global or field-level errors are found; the idea
         * is that in this case the global and field level errors are more specific, and what we want to display
         * to the user
         *
         * @param response
         * @returns Array
         */
        getDisplayMessages: function () {

            var errorMessages = [];

            if (!this.response || !this.response.data || !this.response.data.error) {
                return;
            }

            if (this.response.data.error.globalErrors) {
                $.each(this.response.data.error.globalErrors, function (key, globalError) {
                    errorMessages.push(globalError.message)
                })
            }

            if (this.response.data.error.fieldErrors) {
                $.each(this.response.data.error.fieldErrors, function(key, field) {
                    $.each(field, function(key, fieldError) {
                        errorMessages.push(fieldError.message)
                    })
                })
            }

            if (errorMessages.length == 0) {
                errorMessages.push(this.response.data.error.message);
            }

            return errorMessages;
        }

    }

    return ( RESTErrorResponse );
})