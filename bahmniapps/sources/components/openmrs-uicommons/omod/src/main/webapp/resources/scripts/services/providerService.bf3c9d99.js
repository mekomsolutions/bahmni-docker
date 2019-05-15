angular.module('providerService', ['ngResource','uicommons.common'])
    .factory('Provider', function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/provider/:uuid", {
        },{
            query: { method:'GET' }     // override query method to specify that it isn't an array that is returned
        });
    })
    .factory('ProviderService', function(Provider) {

        return {

            /**
             * Fetches Providers
             *
             * @param params to search against
             * @returns $promise of array of matching Providers (REST ref representation by default)
             */
            getProviders: function(params) {
                return Provider.query(params).$promise
                    .then(function(res) {
                        return res.results;
                    }, emr.handleNotLoggedIn);
            }
        }
    });