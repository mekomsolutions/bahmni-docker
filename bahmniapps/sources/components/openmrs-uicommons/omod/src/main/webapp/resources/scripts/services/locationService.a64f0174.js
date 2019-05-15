angular.module('locationService', ['ngResource', 'uicommons.common'])
    .factory('Location', function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/location/:uuid", {
            uuid: '@uuid'
        },{
            query: { method:'GET' }     // override query method to specify that it isn't an array that is returned
        });
    })
    .factory('LocationService', function(Location) {

        return {

            /**
             * Fetches Locations
             *
             * @param params to search against
             * @returns $promise of array of matching Locations (REST ref representation by default)
             */
            getLocations: function(params) {
                return Location.query(params).$promise
                    .then(function(res) {
                        return res.results;
                    }, emr.handleNotLoggedIn);
            },

            // if location has uuid property this will update, else it will create new
            saveLocation: function(location) {
                return new Location(location).$save();
            },

            retireLocation: function(location) {
                var uuid = typeof location === "string" ? location : location.uuid;
                return new Location({ uuid: uuid }).$delete();
            },

            unretireLocation: function(location) {
                var uuid = typeof location === "string" ? location : location.uuid;
                return new Location({ uuid: uuid, retired: false }).$save();
            }
        }
    });