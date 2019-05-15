angular.module('uicommons.common.error', []). 
	
	factory('http-server-error-interceptor', function($q, $rootScope) {
	    return {
	    	responseError: function(response) {
	            if (response.status === 400) {
	                $rootScope.$broadcast('event:server-validation-error', response);
	            }
	            else if (response.status !== 401 && response.status !== 403) {
	                $rootScope.$broadcast('event:server-general-error');
	            }
	            return $q.reject(response);
	        }
	    }
	}).

    config(function($httpProvider) {
        $httpProvider.interceptors.push('http-server-error-interceptor');
    }).

    run(['$rootScope', function ($rootScope) {
        $rootScope.$on('event:server-validation-error', function (event, response) {
            emr.serverValidationErrorMessage(response);
        });
        $rootScope.$on('event:server-general-error', function () {
            emr.serverGeneralErrorMessage();
        });
    }]);