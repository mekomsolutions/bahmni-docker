angular.module('userService', ['ngResource', 'uicommons.common'])
    .factory('User', function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/user/:uuid", {
            uuid: '@uuid'
        },{
            query: { method:'GET', isArray:false }
        });
    });