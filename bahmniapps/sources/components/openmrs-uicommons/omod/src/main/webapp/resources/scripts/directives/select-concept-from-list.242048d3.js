angular.module('uicommons.widget.select-concept-from-list', [ 'ui.bootstrap' ])

    .directive('selectConceptFromList', [ '$timeout', function($timeout) {

        return {
            restrict: 'E',
            scope: {
                ngModel: '=',
                id: '@',
                locale: '@',
                placeholder: '@',
                requiredIf: '=',
                concepts: '&'
            },
            link: function($scope, element, attrs) {
                $scope.required = attrs.hasOwnProperty('required'); // required attribute has no value
                $scope.inputId = emr.domId($scope.id, 'sel-concept', 'input');
                $scope.size = attrs.size ? attrs.size : 40;

                var options = [];
                _.each($scope.concepts(), function(concept) {
                    _.each(concept.names, function(name) {
                        if (emr.isCompatibleWithSessionLocale(name.locale)) {
                            var display = name.name === concept.display ?
                                name.name :
                                name.name + " &rarr; " + concept.display;
                            options.push({
                                display: display,
                                searchOn: name.name,
                                concept: concept
                            });
                        }
                    });
                });
                $scope.options = _.sortBy(options, function(item) {
                    return item.display.length;
                });

                $scope.verify = function() {
                    if(!$scope.ngModel) {
                        angular.element('#'+$scope.inputId).val('');
                    }
                }

                $scope.startsWith = function(actual, expected) {
                    return emr.startsWithIgnoreCase(actual, expected);
                }

                $scope.onSelect = function($item, $model, $label) {
                    $timeout(function() {
                        emr.focusNextElement(element.closest('body'), element.find('#'+$scope.inputId));
                    }, 10);
                }
            },
            template: '<input type="text" id="{{ inputId }}" ng-model="ngModel" ng-blur="verify()" ' +
                'ng-required="{{ required || requiredIf }}" size="{{ size }}" ' +
                'typeahead-on-select="onSelect($item, $model, $label)" ' +
                'typeahead="opt.concept as opt.display for opt in options | filter:{searchOn:$viewValue}:startsWith" ' +
                'typeahead-editable="false" autocomplete="off" placeholder="{{ placeholder }}" />'
        };
    }]);