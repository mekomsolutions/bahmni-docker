angular.module('uicommons.widget.select-drug', [ 'drugService', 'ui.bootstrap' ])

    .directive('selectDrug', [ 'DrugService', '$timeout', function(DrugService, $timeout) {

        return {
            restrict: 'E',
            scope: {
                ngModel: '=',
                id: '@',
                placeholder: '@',
                onSelectCallback: '&'
            },
            link: function($scope, element, attrs) {
                $scope.required = attrs.hasOwnProperty('required'); // required attribute has no value
                $scope.inputId = emr.domId($scope.id, 'sel-drug', 'input');
                $scope.size = attrs.size ? attrs.size : 40;

                $scope.search = function(term) {
                    return DrugService.getDrugs({ q: term }).then(function(results) {
                        // Corresponding html attribute is support-free-text if one wants to support non coded
                        // the directive would be like <select-drug support-free-text ...other attributes></select-drug>
                        if(attrs.hasOwnProperty('supportFreeText') && results.length == 0) {
                            return [{
                                uuid: null,
                                display: '"' + term + '"' + ' (NON CODED)',
                                nonCodedValue: term
                            }];
                        }
                        return results;
                    });
                };

                $scope.verify = function() {
                    if(!$scope.ngModel) {
                        $('#'+$scope.inputId).val('');
                    }
                }

                $scope.onSelect = function($item, $model, $label) {
                    if (attrs.onSelectCallback) {
                        $scope.onSelectCallback({ '$item':$item, '$model':$model, '$label':$label });
                    } else {
                        $timeout(function() {
                            emr.focusNextElement(element.closest('body'), element.find('#'+$scope.inputId));
                        }, 10);
                    }
                }
            },
            template: '<input type="text" id="{{ inputId }}" ng-model="ngModel" ng-blur="verify()" ' +
                'typeahead="drug as drug.display for drug in search($viewValue) " ' +
                'typeahead-on-select="onSelect($item, $model, $label)" ' +
                'typeahead-editable="false" autocomplete="off" placeholder="{{ placeholder }}" autocomplete="off" ' +
                'ng-required="{{ required }}" size="{{ size }}" ' +
                'typeahead-wait-ms="20" typeahead-min-length="3" />'
        };
    }]);