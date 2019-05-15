angular.module('uicommons.filters').

    /*
     * Angular's "date" filter displays the date in the client's timezone. This filter assumes that the ISO-formatted
     * time string passed in is in the server's timezone, and drops timezone information before formatting it.
     */
    filter('serverDate', ['$filter', function($filter) {
        return function(isoString, format) {
            if (!isoString) {
                return null;
            }
            if (isoString.length > 23) {
                isoString = isoString.substring(0, 23);
            }
            return $filter('date')(isoString, format || "dd-MMM-yyyy H:mm");
        }
    }])

    .filter('serverDateForRESTSubmit', ['$filter', function($filter) {
        return function(isoString) {
            return $filter('serverDate')(isoString, "YYYY-MM-DDTHH:mm:ss.SSS");
        }
    }])