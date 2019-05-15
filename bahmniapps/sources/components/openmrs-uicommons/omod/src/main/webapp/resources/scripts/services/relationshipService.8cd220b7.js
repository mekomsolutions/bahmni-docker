angular.module('relationshipService', ['ngResource', 'uicommons.common'])
    .factory('Relationship', function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/relationship/:uuid", {
            uuid: '@uuid'
        },{
            query: { method:'GET', isArray:false } // OpenMRS RESTWS returns { "results": [] }
        });
    })
    .factory('RelationshipService', function(Relationship) {

        return {

            /**
             * Fetches Relationships
             *
             * @param params to search against
             * @returns $promise of array of matching Relationships (REST ref representation by default)
             */
            getRelationships: function(params) {
                return Relationship.query(params).$promise.then(function(res) {
                    return res.results;
                });
            },

            /**
             * Creates a new relationship
             *
             * @param relationship
             * @returns {Relationship}
             */
            createRelationship: function(relationship) {
                var created = new Relationship(relationship);
                created.$save();
                return created;
            },

            /**
             * Soft-deletes a relationship
             * @param relationship must have a uuid property, but may be a minimal representation
             */
            deleteRelationship: function(relationship) {
                var toDelete = new Relationship({ uuid: relationship.uuid });
                toDelete.$delete();
            }
        }
    });