angular.module('relationshipTypeService', ['ngResource', 'uicommons.common'])
    .factory('RelationshipType', function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/relationshiptype/:uuid", {
            uuid: '@uuid'
        },{
            query: { method:'GET', isArray:false } // OpenMRS RESTWS returns { "results": [] }
        });
    })
    .factory('RelationshipTypeService', function(RelationshipType) {

        return {

            /**
             * Fetches RelationshipTypes
             *
             * @param params to search against
             * @returns $promise of array of matching RelationshipTypes (REST ref representation by default)
             */
            getRelationshipTypes: function(params) {
                return RelationshipType.query(params).$promise.then(function(res) {
                    return res.results;
                });
            }
        }
    });