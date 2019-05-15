angular.module('session', ['ngResource'])

    /*
     * This is just the resource, named this way for consistency with other things in uicommons
     */
    .factory('Session', [ "$resource", function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH + "/ws/rest/v1/appui/session");
    }])

    .factory('SessionInfo', [ "Session", function(Session) {
        var cached = null;
        return {
            get: function() {
                if (!cached) {
                    cached = Session.get();
                }
                return cached;
            },
            hasPrivilege: function(privilege) {
                return new OpenMRS.UserModel(this.get().user).hasPrivilege(privilege);
            },
            logout: function() {
                Session.delete();
            }
        }
    }])