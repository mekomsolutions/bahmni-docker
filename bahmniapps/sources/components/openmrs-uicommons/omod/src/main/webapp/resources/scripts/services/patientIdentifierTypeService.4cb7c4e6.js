angular.module('patientIdentifierTypeService', ['ngResource', 'uicommons.common'])
    .factory('PatientIdentifierType', function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/patientidentifiertype/:uuid", {
            uuid: '@uuid'
        },{
            query: { method:'GET' }     // override query method to specify that it isn't an array that is returned
        });
    })
    .factory("PatientIdentifierTypeService", function(PatientIdentifierType, RestService){
    	return {
    		getPatientIdentifierTypes: function(params) {
    			return RestService.getAllResults(PatientIdentifierType, params);
    		}
    	}
    });