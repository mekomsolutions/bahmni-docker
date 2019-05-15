angular.module('uicommons.widget.coded-or-free-text-answer', [ 'conceptSearchService', 'ui.bootstrap' ])

    .directive('codedOrFreeTextAnswer', ['ConceptSearchService', function(ConceptSearchService) {

        function isExactMatch(candidate, query) {
            query = emr.stripAccents(query.toLowerCase());
            return candidate.conceptName && emr.stripAccents(candidate.conceptName.display.toLowerCase()) === query;
        }

        return {
            restrict: 'E',
            scope: {
                ngModel: '=', // the field whose value you want to set to the selected person
                id: '@',
                conceptClasses: '@',
                selection: '@' // default behavior is "ConceptName", but specify "Concept" if you won't be keeping the specific chosen name
            },
            controller: function($scope) {
                var conceptOnly = $scope.selection === "Concept";

                $scope.inputId = ($scope.id ? $scope.id : 'coded-or-free-text-answer-' + Math.floor(Math.random() * 10000)) + '-input';

                $scope.search = function(term) {
                    // if it starts/ends with " (e.g. the user chose a free-text value) we trim those before searching
                    if (term.slice(0, 1) === '"') {
                        term = term.slice(1);
                    }
                    if (term.slice(term.length - 1, 1) === '"') {
                        term = term.slice(0, term.length - 1);
                    }
                    var extraParams = { };
                    if ($scope.conceptClasses) {
                        extraParams.conceptClasses = $scope.conceptClasses.split(',');
                    }
                    var promise = ConceptSearchService.search(term, extraParams).then(function(results) {
                        var list = [];
                        var exactMatch = false;
                        angular.forEach(results, function(item) {
                            list.push(item);
                            if (!exactMatch && isExactMatch(item, term)) {
                                exactMatch = true;
                            }
                        });
                        if (!exactMatch) {
                            list.push({
                                concept: null,
                                conceptName: null,
                                word: term,
                                transientWeight: Number.MAX_VALUE
                            });
                        }
                        return list;
                    });
                    return promise;
                };

                $scope.format = function(result) {
                    if (!result) {
                        return "";
                    }
                    
                    if (result.concept) {
                    	var key = "ui.i18n.Concept.name." + result.concept.uuid;
	                    var value = emr.message(key);
	                    if (value != key) {
	                    	return value;
	                    }
                    }
                    
                    if (result.conceptName) {
                        if (result.conceptName.display === result.concept.display) {
                            return result.conceptName.display;
                        } else {
                            if (conceptOnly) {
                                return result.conceptName.display + " → " + result.concept.display;
                            } else {
                                return result.conceptName.display + " (" + emr.message("uicommons.conceptSearch.synonymFor", "→") + " " + result.concept.display + ")";
                            }
                        }
                    }
                    else if (result.concept) {
                        return result.concept.display;
                    }
                    else {
                        return '"' + result.word + '"';
                    }
                }

                $scope.onSelect = function($item, $model, $label) {
                    if (conceptOnly && $model.conceptName) {
                        var withoutName = angular.extend({}, $model);
                        withoutName.conceptName = null;
                        withoutName.word = withoutName.concept.display;
                        $scope.ngModel = withoutName;
                    }
                }

                $scope.verify = function(){
                    if(!$scope.ngModel){
                        $('#'+$scope.inputId).val('');
                    }
                }
            },
            template: '<input type="text" id="{{ inputId }}" ng-model="ngModel" ng-blur="verify()" ' +
                'typeahead="result as format(result) for result in search($viewValue)" ' +
                'typeahead-editable="false" typeahead-on-select="onSelect($item, $model, $label)" autocomplete="off" ' +
                'typeahead-wait-ms="20" typeahead-min-length="2" style="min-width: 500px" />'
        };
    }]);