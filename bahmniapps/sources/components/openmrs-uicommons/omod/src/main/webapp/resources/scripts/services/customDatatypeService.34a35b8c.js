angular.module('customDatatypeService', ['ngResource', 'uicommons.common'])
    .factory('CustomDatatype', function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/customdatatype/:uuid", {
        },{
            query: { method:'GET', isArray:false }
        });
    })
    .factory('CustomDatatypeService', function(CustomDatatype) {

        return {

            /**
             * Fetches custom datatypes
             *
             * @param params to search against
             * @returns $promise of array of matching CustomDatatypes (REST ref representation by default)
             */
            getCustomDatatypes: function(params) {
                return CustomDatatype.query(params).$promise
                    .then(function(res) {
                        return res.results;
                    }, emr.handleNotLoggedIn);
            }
        }
    });