angular.module('encounterRoleService', ['ngResource', 'uicommons.common'])
    .factory('EncounterRole', function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/encounterrole/:uuid", {
            uuid: '@uuid'
        },{
            query: { method:'GET' }     // override query method to specify that it isn't an array that is returned
        });
    })
    .factory("EncounterRoleService", function(EncounterRole, RestService) {
    	return {
    		getEncounterRoles: function(params) {
    			return RestService.getAllResults(EncounterRole, params);
    		}
    	}
    });