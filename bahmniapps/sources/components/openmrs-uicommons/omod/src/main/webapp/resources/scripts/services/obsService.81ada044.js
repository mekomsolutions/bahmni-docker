angular.module('obsService', ['ngResource', 'uicommons.common'])
    .factory('Obs', function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/obs/:uuid", {
            uuid: '@uuid'
        },{
            query: { method:'GET', isArray:false } // OpenMRS RESTWS returns { "results": [] }
        });
    })
    .factory('ObsService', function(Obs) {

        return {

            /**
             * Fetches Obs
             *
             * @param params to search against
             * @returns $promise of array of matching Obs (REST ref representation by default)
             */
            getObs: function(params) {
                return Obs.query(params).$promise.then(function(res) {
                    return res.results;
                });
            }
        }
    });