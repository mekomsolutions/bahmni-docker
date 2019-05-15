angular.module('conceptSearchService', ['ngResource', 'uicommons.common'])
    .factory('ConceptSearch', function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/conceptsearch", null, {
            query: { method:'GET', isArray:false } // OpenMRS RESTWS returns { "results": [] }
        });
    })
    .factory('ConceptSearchService', function(ConceptSearch) {

        return {

            /**
             * Searches for concepts
             *
             * @param q main search parameter
             * @param params (optional) additional parameters
             * @returns $promise of array of matching Concepts (REST ref representation by default)
             */
            search: function(q, params) {
                var query = angular.extend({ q: q }, params);
                return ConceptSearch.query(query).$promise.then(function(res) {
                    return res.results;
                });
            }
        }
    });