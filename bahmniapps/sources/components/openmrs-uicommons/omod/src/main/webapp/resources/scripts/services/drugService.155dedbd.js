angular.module('drugService', ['ngResource', 'uicommons.common'])
    .factory('Drug', function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/drug/:uuid", {
            uuid: '@uuid'
        },{
            query: { method:'GET', isArray:false } // OpenMRS RESTWS returns { "results": [] }
        });
    })
    .factory('DrugService', function(Drug) {

        return {
            /**
             * Fetches Drugs
             *
             * @param params to search against
             * @returns $promise of array of matching Drugs (REST ref representation by default)
             */
            getDrugs: function(params) {
                return Drug.query(params).$promise.then(function(res) {
                    return res.results;
                });
            }
        }
    });