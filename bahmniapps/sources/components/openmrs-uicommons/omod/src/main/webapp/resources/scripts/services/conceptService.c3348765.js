angular.module('conceptService', ['ngResource', 'uicommons.common'])
    .factory('Concept', function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/concept/:uuid", {
            uuid: '@uuid'
        },{
            query: { method:'GET', isArray:false } // OpenMRS RESTWS returns { "results": [] }
        });
    })
    .factory('ConceptService', function(Concept) {

        return {
            /**
             * Fetches Concepts
             *
             * @param params to search against
             * @returns $promise of array of matching Concepts (REST ref representation by default)
             */
            getConcepts: function(params) {
                return Concept.query(params).$promise.then(function(res) {
                    return res.results;
                });
            }
        }
    });