
var selectedModel = function(items) {
    return _.find(items, function(i) { return i.isSelected; });
}

function FieldsKeyboardHandler(fieldModels, questionsHandler) {
    var fields = fieldModels;
    var questionsHandler = questionsHandler;

    var delegateIfNoSelectedFieldTo = function(delegatedFunction) {
        if(!selectedModel(fields)) {
            return delegatedFunction();
        }
        return false;
    }

    // TODO add gotoNextQuestin and gotoPrevious question method in question handler and delegate to that?
    var switchActiveQuestions = function(currentQuestion, newQuestion) {
        if(currentQuestion != newQuestion) {

            // test the validator if we navigating forward
            if (questionsHandler.isAfterSelectedQuestion(newQuestion) && !currentQuestion.isValid()) {
                return false;
            }

            currentQuestion.toggleSelection();

            if(currentQuestion.parentSection != newQuestion.parentSection) {
                currentQuestion.parentSection.toggleSelection();
                newQuestion.parentSection.toggleSelection();
            }
            newQuestion.toggleSelection();
        }

        return true;
    };

    var switchActiveField = function(fieldIndexUpdater, showFirstFieldIfNoneIsActive) {
        var currentIndex;
        var newField = null;
        while (newField == null || newField.isDisabled()) {
            var field = selectedModel(fields);
            if(field) {
                if (field.onExit()) {   // call any exit handler, and only continue if it returns true
                    currentIndex = _.indexOf(fields, field);
                    var nextIndex = fieldIndexUpdater(currentIndex, fields);
                    
                    //If we have reached the end of form, just cycle through fields on this section.
                    if (nextIndex == currentIndex && field.parentQuestion instanceof ConfirmationQuestionModel && field.parentQuestion.parentSection) {
                    	newField = field.parentQuestion.parentSection.questions[0].fields[0];
                    }
                    else {
                    	newField = fields[nextIndex];
                    }

                    if(newField) {
                        field.toggleSelection();
                        if(switchActiveQuestions(field.parentQuestion, newField.parentQuestion)) {
                            newField.toggleSelection();
                        }
                        else {
                            field.toggleSelection(); // kind of hacky, but we toggle the field back on if switching the question failed for some reason
                        }
                    } else {
                        return true;
                    }
                } else {
                    return false;
                }
            } else {
                if(showFirstFieldIfNoneIsActive) {
                    questionsHandler.selectedQuestion() || questionsHandler.handleDownKey();
                    questionsHandler.selectedQuestion().fields[0].toggleSelection();
                    return true;
                }
            }
        }

        return newField != null;
    };


    var api = {};
    api.handleUpKey = function() {
        return delegateIfNoSelectedFieldTo(questionsHandler.handleUpKey);
    };
    api.handleDownKey = function() {
        return delegateIfNoSelectedFieldTo(questionsHandler.handleDownKey);
    };
    api.handleTabKey = function() {
        var currentField = selectedModel(fields);
        var isValid = (currentField ? currentField.isValid() : true);
        var activeFieldSwitched = (isValid ? switchActiveField(findNextEnabledElement, true) : false);
        if (!activeFieldSwitched) { currentField.select(); }
        return true;
    };
    api.handleShiftTabKey = function() {
        return switchActiveField(findPreviousEnabledElement, false);
    };
    api.handleEnterKey = function() {
        var currentField = selectedModel(fields);
        var fieldType = currentField.element.attr("type");
        if(fieldType && fieldType.match(/submit|button/)) {
            currentField.element.click();
            return true;
        }
        else if (currentField.element.is('textarea')) {
            // don't prevent default behaviour when within a text area
            return false;
        }
        else {
            return api.handleTabKey();
        }
    };
    api.handleEscKey = function() {
        var field = selectedModel(fields);
        if(field) {
            field.toggleSelection();
            return true;
        }
        return false;
    };
    return api;
}

function QuestionsKeyboardHandler(questionModels) {
    var questions = questionModels;

    var api = {};

    api.isAfterSelectedQuestion = function(newQuestion) {
        return (_.indexOf(questions, selectedModel(questions)) < _.indexOf(questions, newQuestion) ) ? true : false;
    };
    api.selectedQuestion = function() {
        return selectedModel(questions);
    };
    api.handleUpKey = function() {
        var question = selectedModel(questions);
        if(question) {
            if (!question.onExit()) {   // run any exit handler, and don't proceed if it returns false
                return true;
            }
            var idx = _.indexOf(questions, question);
            if(idx > 0) {
                var previousIdx = findPreviousEnabledElement(idx, questions);

                if (idx != previousIdx) {
                    question.toggleSelection();
                    questions[previousIdx].toggleSelection();
                    if(question.parentSection != questions[previousIdx].parentSection) {
                        question.parentSection.toggleSelection();
                        questions[previousIdx].parentSection.toggleSelection();
                    }
                }
                return true;
            }
        }
        return false;
    };
    api.handleDownKey = function() {
        var question = selectedModel(questions);
        if(!question) {
            questions[0].toggleSelection();
            questions[0].parentSection.toggleSelection();
            return true;
        }

        if(!question.isValid() || !question.onExit()) {   // run the validation, if it passes, run the exit handlers; if either returns false, don't proceed
            return true;
        }
        var idx = _.indexOf(questions, question);
        if(idx < questions.length-1) {
            var nextIdx = findNextEnabledElement(idx, questions);

            if (idx != nextIdx) {
                question.toggleSelection();
                questions[nextIdx].toggleSelection();
                if(question.parentSection != questions[nextIdx].parentSection) {
                    question.parentSection.toggleSelection();
                    questions[nextIdx].parentSection.toggleSelection();
                }
            }
            return true;
        }
        return false;
    };
    return api;
}

var sectionsMouseHandlerInitializer = function(sections) {
    _.each(sections, function(section) {
        section.title.click( function(event) {
            clickedSectionHandler(sections, section, event);
        });
    });
};
var clickedSectionHandler = function(sections, section, event) {
    event.stopPropagation();
    var currentSection = selectedModel(sections);
    if(currentSection == section) {
        return;
    }

    var currentSectionIndex = _.indexOf(sections, currentSection);
    var clickedSectionIndex = _.indexOf(sections, section);
    var shouldSelectClickedSection = true;
    var goToSectionInstead = null;
    if(clickedSectionIndex > currentSectionIndex) {
        // only need to call validation if moving ahead
        for(var i=currentSectionIndex; i<clickedSectionIndex; i++) {
            shouldSelectClickedSection = sections[i].isValid() && shouldSelectClickedSection;
            if (!shouldSelectClickedSection) {
                if (i > currentSectionIndex) {
                    goToSectionInstead = sections[i];
                }
                break;
            }
        }
    }

    // call exit handler no matter if we are moving forward or backwards
    var exitCurrentSection = (shouldSelectClickedSection || goToSectionInstead) && currentSection.onExit();
    if (!exitCurrentSection) {
        shouldSelectClickedSection = false;
        goToSectionInstead = false;
    }

    if(!shouldSelectClickedSection) {
        if (goToSectionInstead) {
            currentSection.toggleSelection();
            goToSectionInstead.toggleSelection();
            var goToQuestion = goToSectionInstead.firstInvalidQuestion() || goToSectionInstead.questions[0];
            var goToField = goToQuestion.firstInvalidField() || goToQuestion.fields[0];
            goToQuestion.toggleSelection();
            goToField.toggleSelection();
        } else {
            var selectedQuestion = selectedModel(currentSection.questions);
            var selectedField = selectedModel(selectedQuestion.fields);
            selectedField && selectedField.select();
        }
    } else {
        currentSection.toggleSelection();
        section.toggleSelection();
        section.questions[0].toggleSelection();
        section.questions[0].fields[0].toggleSelection();
    }
};

var questionsMouseHandlerInitializer = function(questions) {
    _.each(questions, function(question) {
        if(question.questionLi) {
            question.questionLi.click(function(event) {
                clickedQuestionHandler(questions, question, event);
            });
        }
    });
};
var clickedQuestionHandler = function(questions, question, event) {
    event.stopPropagation();
    var currentQuestion = selectedModel(questions);
    if(currentQuestion == question) {
        return;
    }

    var currentQuestionIndex = _.indexOf(questions, currentQuestion);
    var clickedQuestionIndex = _.indexOf(questions, question);
    var shouldSelectClickedQuestion = true;
    if(clickedQuestionIndex > currentQuestionIndex) {
        for(var i=currentQuestionIndex; i<clickedQuestionIndex; i++) {
            shouldSelectClickedQuestion = questions[i].isValid() && shouldSelectClickedQuestion;
        }
    }

    // call exit handler if validation has passed
    shouldSelectClickedQuestion = shouldSelectClickedQuestion && currentQuestion.onExit();

    if(!shouldSelectClickedQuestion) {
        var selectedField = selectedModel(currentQuestion.fields);
        selectedField && selectedField.select();
    } else {
        currentQuestion.toggleSelection();
        question.toggleSelection();
        question.fields[0].toggleSelection();
        if(currentQuestion.parentSection != question.parentSection) {
            currentQuestion.parentSection.toggleSelection();
            question.parentSection.toggleSelection();
        }
    }
};

var fieldsMouseHandlerInitializer = function(fields) {
    _.each(fields, function(field) {
        field.element.mousedown(function(event) {
            clickedFieldHandler(fields, field, event);
        });
    });
};

var clickedFieldHandler = function(fields, field, event) {
    var currentField = selectedModel(fields);
    if(currentField == field) {
        currentField.select();
        return;
    }

    var currentFieldIndex = _.indexOf(fields, currentField);
    var clickedFieldIndex = _.indexOf(fields, field);
    var shouldSelectClickedField = true;
    if(clickedFieldIndex > currentFieldIndex) {
        for(var i=currentFieldIndex; i<clickedFieldIndex; i++) {
            shouldSelectClickedField = fields[i].isValid() && shouldSelectClickedField;
        }
    }

    // call exit handler if validation has passed
    shouldSelectClickedField = shouldSelectClickedField && currentField.onExit();

    if(!shouldSelectClickedField) {
        currentField.select();
    } else {
        currentField.toggleSelection();
        field.toggleSelection();
    }
    event.preventDefault();
};

var findNextEnabledElement = function (i, elements) {
    var nextEnabledElement = i + 1;
    while (nextEnabledElement < elements.length && elements[nextEnabledElement].isDisabled()) { nextEnabledElement++; }
    return nextEnabledElement != elements.length ? nextEnabledElement : i;  // if we reached the end without finding an enabled element, just return the passed-in index
}

var findPreviousEnabledElement = function (i, elements) {
    var previousEnabledElement = i - 1;
    while (previousEnabledElement >= 0 && elements[previousEnabledElement].isDisabled()) { previousEnabledElement--; }
    return previousEnabledElement != -1 ? previousEnabledElement : i;  // if we reached the end without finding an enabled element, just return the passed-in index
}