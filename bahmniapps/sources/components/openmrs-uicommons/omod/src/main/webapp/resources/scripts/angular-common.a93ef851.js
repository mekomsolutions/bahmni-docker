angular.module('uicommons.common', []).

    factory('http-auth-interceptor', function($q, $rootScope) {
        return {
            responseError: function(response) {
                if (response.status === 401 || response.status === 403) {
                    $rootScope.$broadcast('event:auth-loginRequired');
                }
                return $q.reject(response);
            }
        }
    }).
    
    factory("RestService", function($q) {
    	function populateResults(resource, params, deferred, results) {
			resource.query(params).$promise.then(function(res) {
				results = results.concat(res.results);
				
				var hasMoreResults = false;
				
				if (res.links) {
					for (i = 0; i < res.links.length; i++) {
						if (res.links[i].rel == "next") {
							var startIndexRe = /startIndex=([0-9]*)/;
							var startIndex = startIndexRe.exec(res.links[i].uri);
							params["startIndex"] = startIndex[1];
							
							hasMoreResults = true;
							populateResults(resource, params, deferred, results);
							
							break;
						}
					}
				}
				
				if (!hasMoreResults) {
					deferred.resolve(results);
				}
			}, function(error) {
				deferred.reject(error);
			});
		}
    	
    	return {		
    		getAllResults: function(resource, params) {
    			var deferred = $q.defer();
    			var results = [];
    			
    			populateResults(resource, params, deferred, results);
    			
    			return deferred.promise;
    		}
    	}
    }).

    config(function($httpProvider) {
        $httpProvider.interceptors.push('http-auth-interceptor');

        // to prevent the browser from displaying a password pop-up in case of an authentication error
        $httpProvider.defaults.headers.common['Disable-WWW-Authenticate'] = 'true';
    }).

    run(['$rootScope', '$window', function ($rootScope, $window) {
        $rootScope.$on('event:auth-loginRequired', function () {
            if (confirm(emr.message("uicommons.notLoggedIn", "The operation cannot be completed, because you are no longer logged in. Do you want to go to login page?"))) {
                window.location = "/" + OPENMRS_CONTEXT_PATH + "/login.htm";
            }
        });
    }]);