angular.module('visitService', ['ngResource', 'uicommons.common'])
    .factory('Visit', function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/visit/:uuid", {
            uuid: '@uuid'
        },{
            query: { method:'GET', isArray:false } // OpenMRS RESTWS returns { "results": [] }
        });
    })
    .factory('VisitService', function(Visit, $resource) {

        return {

            /**
             * Fetches Visits
             *
             * @param params to search against
             * @returns $promise of array of matching Visits (REST ref representation by default)
             */
            getVisits: function(params) {
                return Visit.query(params).$promise.then(function(res) {
                    return res.results;
                });
            },

            // if visit has uuid property this will update, else it will create new
            saveVisit: function(visit) {
                return new Visit(visit).$save();
            },

            visitAttributeResourceFor: function(visit) {
                return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/visit/:visitUuid/attribute/:uuid", {
                    visitUuid: visit.uuid,
                    uuid: '@uuid'
                },{
                    query: { method:'GET', isArray:false } // OpenMRS RESTWS returns { "results": [] }
                });
            }
        }
    });