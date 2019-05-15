angular.module('uicommons.widget.select-person', [ 'personService', 'ui.bootstrap' ])

    .directive('selectPerson', ['PersonService', function(PersonService) {

        return {
            restrict: 'E',
            scope: {
                ngModel: '=', // the field whose value you want to set to the selected person
                id: '@',
                excludePerson: '@' // a uuid
            },
            controller: function($scope) {
                $scope.inputId = ($scope.id ? $scope.id : 'select-person-' + Math.floor(Math.random() * 10000)) + '-input';
                $scope.search = function(term) {
                    var promise = PersonService.getPersons({ q: term });
                    if ($scope.excludePerson) {
                        // e.g. if a patient page wants to let you search for any _other_ person
                        return promise.then(function(result) {
                            return _.reject(result, function(item) {
                                return item.uuid == $scope.excludePerson;
                            });
                        });
                    } else {
                        return promise;
                    }
                }
            },
            template: '<input type="text" id="{{ inputId }}" ng-model="ngModel" ' +
                'typeahead="person as person.display for person in search($viewValue) | filter:$viewValue" ' +
                'typeahead-editable="false" autofocus />'
        };
    }]);