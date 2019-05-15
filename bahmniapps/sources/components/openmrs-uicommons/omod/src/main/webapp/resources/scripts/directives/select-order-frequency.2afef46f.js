angular.module('uicommons.widget.select-order-frequency', [ 'ui.bootstrap' ])

    .directive('selectOrderFrequency', [ '$timeout', function($timeout) {

        return {
            restrict: 'E',
            scope: {
                ngModel: '=',
                id: '@',
                locale: '@',
                placeholder: '@',
                frequencies: '&'
            },
            link: function($scope, element, attrs) {
                $scope.required = attrs.hasOwnProperty('required'); // required attribute has no value
                $scope.inputId = emr.domId($scope.id, 'sel-freq', 'input');
                $scope.size = attrs.size ? attrs.size : 20;

                var options = [];
                _.each($scope.frequencies(), function(frequency) {
                    var concept = frequency.concept;
                    _.each(concept.names, function(name) {
                        if (emr.isCompatibleWithSessionLocale(name.locale)) {
                            var display = name.name === concept.display ?
                                name.name :
                                name.name + " &rarr; " + concept.display;
                            options.push({
                                display: display,
                                searchOn: name.name,
                                frequency: frequency
                            });
                        }
                    });
                });
                $scope.options = _.sortBy(options, function(item) {
                    return item.display.length;
                });

                $scope.verify = function() {
                    if(!$scope.ngModel){
                        $('#'+$scope.inputId).val('');
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
                'ng-required="{{ required }}" size="{{ size }}" ' +
                'typeahead-on-select="onSelect($item, $model, $label)" ' +
                'typeahead="opt.frequency as opt.display for opt in options | filter:{searchOn:$viewValue}:startsWith" ' +
                'typeahead-editable="false" autocomplete="off" placeholder="{{ placeholder }}" />'
        };
    }]);