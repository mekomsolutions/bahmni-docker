angular.module('personService', ['ngResource', 'uicommons.common'])
    .factory('Person', function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/person/:uuid", {
            uuid: '@uuid'
        },{
            query: { method:'GET', isArray:false } // OpenMRS RESTWS returns { "results": [] }
        });
    })
    .factory('PersonService', function(Person) {

        return {

            /**
             * Fetches Persons
             *
             * @param params to search against
             * @returns $promise of array of matching Persons (REST ref representation by default)
             */
            getPersons: function(params) {
                return Person.query(params).$promise.then(function(res) {
                    return res.results;
                });
            }
        }
    });