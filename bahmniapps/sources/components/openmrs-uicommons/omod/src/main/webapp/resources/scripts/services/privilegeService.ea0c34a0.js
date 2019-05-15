angular.module('privilegeService', ['ngResource', 'uicommons.common'])
	.factory('Privilege', function($resource) {
	    return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/privilege/:uuid", {
	        uuid: '@uuid'
	    },{
	        query: { method:'GET' }     // override query method to specify that it isn't an array that is returned
	    });
	})
    .factory("PrivilegeService", function(Privilege, RestService) {
        return {
            getPrivileges: function(params) {
                return RestService.getAllResults(Privilege, params);
            }
        }
    });