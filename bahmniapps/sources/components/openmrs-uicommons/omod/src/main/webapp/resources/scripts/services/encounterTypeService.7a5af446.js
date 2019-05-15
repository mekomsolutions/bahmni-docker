angular.module('encounterTypeService', ['ngResource','uicommons.common'])
    .factory('EncounterType', function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/encountertype/:uuid", {
            uuid: '@uuid'
        },{
            query: { method:'GET' }     // override query method to specify that it isn't an array that is returned
        });
    })
    .factory('EncounterTypeService', function(EncounterType, RestService) {

        return {

            /**
             * Fetches EncounterTypes
             *
             * @param params to search against
             * @returns $promise of array of matching EncounterTypes (REST ref representation by default)
             */
            getEncounterTypes: function(params) {
            	return RestService.getAllResults(EncounterType, params);
            }
        }
    });