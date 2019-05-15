angular.module('visitAttributeTypeService', ['ngResource', 'uicommons.common'])
    .factory('VisitAttributeType', function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/visitattributetype/:uuid", {
        	uuid: "@uuid"
        },{
            query: { method:'GET', isArray:false }
        });
    })
    .factory('VisitAttributeTypeService', function(VisitAttributeType, RestService) {

        return {
        	
            /**
             * Fetches VisitAttributeTypes
             *
             * @param params to search against
             * @returns $promise of array of matching EncounterTypes (REST ref representation by default)
             */
            getVisitAttributeTypes: function(params) {
                return RestService.getAllResults(VisitAttributeType, params);
            }
        }
    });