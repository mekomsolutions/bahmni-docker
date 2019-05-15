angular.module('appFramework', ['ngResource'])

    .factory('ExtensionResource', [ "$resource", function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH + "/ws/rest/v1/extension", {
            uuid: '@uuid'
        },{
            query: { method:'GET', isArray:false, cache:true } // OpenMRS RESTWS returns { "results": [] }
        });
    }])

    .factory('AppResource', [ "$resource", function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH + "/ws/rest/v1/app", {
            uuid: '@uuid'
        },{
            query: { method:'GET', isArray:false, cache:true } // OpenMRS RESTWS returns { "results": [] }
        });
    }])

    .factory('AppFrameworkService', [ "ExtensionResource", "AppResource", function(ExtensionResource, AppResource) {
        return {
            // returns a promise
            getUserExtensionsFor: function(extensionPoint) {
                // TODO handle multiple pages
                var extensionPointId = extensionPoint.uuid || extensionPoint;
                return ExtensionResource.query({v:"default", scope:"user", extensionPoint: extensionPointId }).
                    $promise.then(function(response) {
                        return response.results;
                    });
            }
        }
    }]);