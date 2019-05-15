angular.module('roleService', ['ngResource', 'uicommons.common'])
	.factory('Role', function($resource) {
	    return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/role/:uuid", {
	        uuid: '@uuid'
	    },{
	        query: { method:'GET' }     // override query method to specify that it isn't an array that is returned
	    });
    })
    .factory("RoleService", function(Role, RestService) {
    	return {
    		getRoles: function(params) {
    			return RestService.getAllResults(Role, params);
    		}
    	}
    });