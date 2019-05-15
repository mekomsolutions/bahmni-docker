/*
 * Base prototype for selectable models
 */

function SelectableModel(elem) {
    this.element = $(elem);
    this.isSelected = false;
    this.toggleSelection = this.select;
    this.id = this.element.attr("id");
}
SelectableModel.prototype = {
    constructor: SelectableModel,
    select: function() {
        this.isSelected = true;
        this.element.addClass("focused");
        this.toggleSelection = this.unselect;
        this.element.triggerHandler("select", this);
    },
    unselect: function() {
        this.isSelected = false;
        this.element.removeClass("focused");
        this.toggleSelection = this.select;
        this.element.triggerHandler("unselect", this);
    },
    enable: function() {
        this.element.removeAttr('disabled');
        this.element.removeClass("disabled");
        this.element.triggerHandler("enable", this);
    },
    disable: function() {
        this.element.attr('disabled', 'true');
        this.element.addClass("disabled");
        this.element.triggerHandler("disable", this);
    },
    show: function() {
        this.enable();
        if (this.isSelected) {
            this.select();
        }
        this.element.triggerHandler("show", this);
    },
    hide: function() {
        this.disable();
        // TODO do we want to unselect here if selected? probably...
        this.element.triggerHandler("hide", this);
    },
    onExit: function() {
        // override this to provide onExit functionality
        this.element.triggerHandler("exit", this);
        return true;
    },
    isDisabled: function() {
        return this.element.is(":disabled") || this.element.hasClass("disabled");
    }
}

// TODO so it looks like exit handlers can only be applied to fields, but validators can be applied to fields and questions--is this correct?

/*
 * Prototype for fields
 */
function FieldModel(elem, container, parentQuestion, messagesContainer) {
    SelectableModel.apply(this, [elem]);
    this.container = container;
    this.parentQuestion = parentQuestion;
    this.messagesContainer = messagesContainer;
    this.validators = [];this.exitHandlers = [];
    this.label = $('label[for="' + this.element.attr('id') + ' "], label[for="' + this.element.parent().attr('id') + '"]').text().trim();

    // you can specify validators directly on the element, or the parent p or fieldset
    var classes = this.element.attr("class") + " "
                    + this.element.closest("p").attr("class") + " "
                    + this.element.closest("field").attr("class") + " "
                    + this.element.closest("fieldset").attr("class");

    if(classes) {
        _.each(classes.split(' '), function(klass) {
            Validators[klass] && this.validators.push(Validators[klass]);
            ExitHandlers[klass] && this.exitHandlers.push(ExitHandlers[klass]);
        }, this);
    }
}
FieldModel.prototype = new SelectableModel();
FieldModel.prototype.constructor = FieldModel;

FieldModel.prototype.select = function() {
    SelectableModel.prototype.select.apply(this);
    this.element.focus();
}
FieldModel.prototype.unselect = function() {
    SelectableModel.prototype.unselect.apply(this);
    this.element.removeClass("error");
    this.element.blur();
}

FieldModel.prototype.click = function() {
    if(this.element) {
        this.element.mousedown();  // triggers click event that is handled by handler in navigatorHandlers.js
    }
}

FieldModel.prototype.disable = function() {
    SelectableModel.prototype.disable.apply(this);
    this.container.addClass("disabled");
    this.resetValue();
}

FieldModel.prototype.enable = function() {
    SelectableModel.prototype.enable.apply(this);
    this.container.removeClass("disabled");
}

FieldModel.prototype.hide = function() {
    SelectableModel.prototype.hide.apply(this);
    this.container.hide();
}

FieldModel.prototype.show = function() {
    SelectableModel.prototype.show.apply(this);
    this.container.show();
}

FieldModel.prototype.isValid = function() {
    var validationMessages = this.isDisabled() ? [] : _.reduce(this.validators, function(memo, validator) {
        var validationMessage = validator.validate(this);
        if (validationMessage) {
            memo.push(validationMessage);
        }
        return memo;
    }, [], this);

    this.messagesContainer.empty();
    if(validationMessages.length > 0) {
        _.each(validationMessages, function(message) {
           this.messagesContainer.append(message);
        }, this);
        this.element.addClass("error");
        this.messagesContainer.show();
        return false;
    }
    return true;
}

FieldModel.prototype.onExit = function ()  {
    var exit = _.reduce(this.exitHandlers, function(memo, exitHandler) {
        return memo && exitHandler.handleExit(this);
    }, true, this);

    return exit;
}

FieldModel.prototype.value = function() {

    // TODO provide integration with the HFE property accessor functionality?

    if (this.element.attr('data-value-from')) {
        return $(this.element.attr('data-value-from')).val();
    } else if (this.container.attr('data-value-from')) {
        return $(this.container.attr('data-value-from')).val();
    }

    var selectedOption = this.element.find('option:selected');
    if (selectedOption.length > 0) {
        return selectedOption.val(); // return the actual value
    }
    else if (this.element.attr('type') == 'radio') {
    	return this.element.is(':checked') ? this.element.val() : "";
    }
    else {
        return this.element.val() ? this.element.val().trim() : "";
    }
}

FieldModel.prototype.resetValue = function() {

    // TODO provide integration with the HFE property accessor functionality?
    // TODO support date widgets?

    // handle the case of dropdown with a selected element
    var selectedOption = this.element.find('option:selected');
    if (selectedOption.length > 0) {
        selectedOption.removeAttr('selected');
    }
    // handle the case of radio set with a checked item
    else if (this.element.attr('type') == 'radio' && this.element.is(':checked')) {
        this.element.removeAttr('checked');
    }
    // handle checkbox
    else if (this.element.attr('type') == 'checkbox') {
        this.element.removeAttr('checked');
    }
    // handle input field
    else {
        this.element.val("");
    }

}

// fwiw, if we ever want to refactor this, the personRelationship widget in the registration app module directly overrides
// this method on a FieldModel instance as a hack around incompatibility with the navigator and angular
// see: https://github.com/openmrs/openmrs-module-registrationapp/commit/3e89927c6993cbc6544ae57ebff4baca3ae8bbb5
FieldModel.prototype.displayValue = function() {

    var value;

    var selectedOption = this.element.find('option:selected');
    if (this.element.attr('data-display-value')) {
        value = this.element.attr('data-display-value');
    }
    else if (this.container.attr('data-display-value')) {
        value = this.container.attr('data-display-value');
    }
    else if (selectedOption.length > 0) {
        if (selectedOption.val() != '') { //if selected non empty value
            value = selectedOption.text(); // return the display text
        }
    }
    else if (this.element.attr('type') == 'radio') {
        value = this.element.is(':checked') ? this.element.val() : " ";
    }
    else if (this.element.attr('type') == 'checkbox') {
    	if (this.element.is(':checked')) {
    		if (this.element.attr('data-display-when-checked')) {
                value = this.element.attr('data-display-when-checked');
            }
    		else {
                var label = $('label[for="' + this.element.attr('id') + '"]');
                if (label.length) {
                    value = label.first().html();
                } else {
                    value = this.element.attr('value');
                }
            }
    	}
    	else {
    		if (this.element.attr('data-display-when-unchecked'))
    			value = this.element.attr('data-display-when-unchecked');
    		else
    			value = "";
    	}
    }
    else {
        value = this.element.val() ? this.element.val() : "";
    }

    // Fix issues w/reflected XSS by sanitizing value (issue: RA-452)
    value = $("<div>").text(value).html();

    if (value) {
        // see if there are units to append
        var append = _.map(this.element.parent().find(".append-to-value, .units").first(), function(item) { return $(item).html() }).join(" ");
        return value + (append ? " <span class='after-value'>" + append + "</span>" : "");
    } else {
        return "";
    }
}
FieldModel.prototype.resetErrorMessages = function() {
    this.messagesContainer.empty();
    this.element.removeClass("error");
}

/*
 * Prototype for questions
 */

function QuestionModel(elem, section, titleListElem, messagesContainer) {
    SelectableModel.apply(this, [elem]);
    this.parentSection = section;
    this.messagesContainer = messagesContainer;
    this.validators = [];
    var fieldContainers;

    // we allow delimiting fields using a <p> or a custom <field> tag
    fieldContainers = this.element.find("field");
    if (!fieldContainers || fieldContainers.length == 0) {
        fieldContainers = this.element.find("p").has("input, textarea, select, button");
    }

    this.fields = _.map(fieldContainers, function(container) {
        var cnt = $(container);
        var fieldErrorsElement = cnt.find("span.field-error").first();
        //since radio buttons represent the same property/request param, we need
        //to use the same error element for all radio buttons in the same group
        var radioButtonElements = cnt.find("input:radio");
        if(radioButtonElements && radioButtonElements.length > 0){
            fieldErrorsElement = $('#'+radioButtonElements[0].name+'-field-error');
        }
        return new FieldModel(cnt.find("input, textarea, select, button").first(), cnt, this, fieldErrorsElement);
    }, this);
    this.questionLegend = this.element.find('legend').first();
    var label = $('<span/>').html(this.questionLegend.text());
    var spanId = this.questionLegend.attr('id');
    if (spanId) {
    	label.attr('id', spanId);
    }
    this.questionLi = $('<li class="question-legend"><i class="icon-ok"></i></li>').append(label);
    this.questionLi.appendTo(titleListElem);
    this.fieldSeparator = this.element.attr('field-separator') ? this.element.attr('field-separator') : ', ';
    var displayTemplate = this.element.attr('display-template');
    if (displayTemplate) {
        this.displayTemplate = Handlebars.compile(displayTemplate);
    }

    var classes = this.element.attr("class");
    if(classes) {
        _.each(classes.split(' '), function(klass) {
            QuestionValidators[klass] && this.validators.push(QuestionValidators[klass]);
        }, this);
    }
    this.determineDisplayValue();
}
QuestionModel.prototype = new SelectableModel();
QuestionModel.prototype.constructor = QuestionModel;

QuestionModel.prototype.click = function() {
    if(this.questionLi) {
        this.questionLi.click();  // triggers click event that is handled by handler in navigatorHandlers.js
    }
}

QuestionModel.prototype.enable = function() {
    SelectableModel.prototype.enable.apply(this);
    this.questionLi.removeClass("disabled");
    _.each(this.fields, function(field) { field.enable(); });
}

QuestionModel.prototype.disable = function() {
    SelectableModel.prototype.disable.apply(this);
    this.questionLi.addClass("disabled"); // disable the menu item as well
    _.each(this.fields, function(field) { field.disable(); });
}

QuestionModel.prototype.hide = function() {
    SelectableModel.prototype.hide.apply(this);
    this.questionLi.hide(); // hide the menu item as well
    _.each(this.fields, function(field) { field.hide(); });
}

QuestionModel.prototype.show = function() {
    SelectableModel.prototype.show.apply(this);
    this.questionLi.show();  // show the menu item (regardless if the element has been selected or not)
    _.each(this.fields, function(field) { field.show(); });
}
QuestionModel.prototype.determineDisplayValue = function() {

    var fieldDisplayValues = _.map(_.filter(this.fields, function (field) {
            return field.displayValue()
        }), function (field) {
            return field.displayValue()
        }, this);

    if (this.displayTemplate) {
        this.valueAsText = this.displayTemplate({
            fields: this.fields,
            field: fieldDisplayValues
        });
    }
    else {
        this.valueAsText = fieldDisplayValues.join(this.fieldSeparator);
    }
}
QuestionModel.prototype.select = function() {
    SelectableModel.prototype.select.apply(this);
    this.valueAsText = "";
    this.questionLi.addClass("focused");
    _.each(this.fields, function(field) { field.resetErrorMessages(); });
}
QuestionModel.prototype.unselect = function() {
    SelectableModel.prototype.unselect.apply(this);

    this.determineDisplayValue();

    _.each(this.fields, function(field) { field.unselect(); });

    this.questionLi.removeClass("focused");

    // see if any of the fields for this question have a value
    var anyFieldHasValue =  _.any(this.fields, function(field) {
        return field.displayValue() ? true : false;
    })

    // see if any fields marked as expected are missing a value
    var expectedFieldMissingValue = _.any(this.fields, function(field) {
        return field.element.hasClass("expected") ? (!field.displayValue() ? true : false) : false;
    })

    // mark the question as done if at least one of the fields has a value, and all the expected fields have a value
    anyFieldHasValue && !expectedFieldMissingValue ? this.questionLi.addClass("done") :
          this.questionLi.removeClass("done");

}

QuestionModel.prototype.isValid = function() {
    if (this.isDisabled()) {
        return true;
    }
    var allFieldsAreValid =  _.reduce(this.fields, function(memo, field) {
        return field.isValid() && memo;
    }, true);

    if(!allFieldsAreValid) {
        return false;
    }

    var validationMessages = _.reduce(this.validators, function(memo, validator) {
        var validationMessage = validator.validate(this);
        if (validationMessage) {
            memo.push(validationMessage);
        }
        return memo;
    }, [], this);

    if(this.messagesContainer)
        this.messagesContainer.empty();
    if(validationMessages.length > 0) {
        _.each(validationMessages, function(message) {
            this.messagesContainer.append(message);
        }, this);
        this.messagesContainer.show();
        return false;
    }

    return true;
}

QuestionModel.prototype.firstInvalidField = function() {
    return _.find(this.fields, function(field) {
        return !field.isValid();
    });
}

QuestionModel.prototype.onExit = function() {
    return _.reduce(this.fields, function(memo, field) {
        return field.onExit() && memo;
    }, true);
}

QuestionModel.prototype.title = function() {
    return this.questionLegend;
}

QuestionModel.prototype.resetErrorMessages = function() {
    this.messagesContainer.empty();
}

QuestionModel.prototype.showInConfirmation = function() {
    return !this.element.hasClass('no-confirmation');
}

QuestionModel.prototype.multiLineInConfirmation = function() {
    return this.element.hasClass('multi-line-confirmation');
}


//QuestionModel.prototype.

/*
 * Specific model for the Yes/No confirmation question
 */
function ConfirmationQuestionModel(elem, section, titleListElem) {
    QuestionModel.apply(this, [elem, section, titleListElem]);

    this.confirm = _.find(this.fields, function (field) {
        return field.element.hasClass('confirm');
    });
    this.cancel = _.find(this.fields, function (field) {
        return field.element.hasClass('cancel');
    });
    this.skipConfirmation = section.skipConfirmation ? section.skipConfirmation : false;

    // return to beginning of form (by triggering on the first enabled section) if user hits cancel
    if (this.cancel) {
        this.cancel.element.click(function () {
            var sec = _.find(section.sections, function (s) {
                return !s.isDisabled();
            });
            if (sec != null) {
                sec.click();
            }
        });
    }
}

ConfirmationQuestionModel.prototype = new QuestionModel();
ConfirmationQuestionModel.prototype.constructor = ConfirmationQuestionModel;
ConfirmationQuestionModel.prototype.select = function() {
    // if we are in "skip confirmation", then selecting the confirmation question should just trigger a submit
    // otherwise, defer to the standard Question select functionality
    if (this.skipConfirmation) {
        this.confirm.element.click();
    }
    else {
        QuestionModel.prototype.select.apply(this);
    }
}

/*
 * Prototype for sections
 */
function SectionModel(elem, formMenuElem) {
    SelectableModel.apply(this, [elem]);

    var title = this.element.find("span.title").first();
    var label = $('<span/>').html(title.text());
    var spanId = title.attr('id');
    if (spanId) {
    	label.attr('id', spanId);
    }
    var newTitle = $("<li/>").append(label);
    var questionsTitlesList = $("<ul></ul>");
    newTitle.append(questionsTitlesList);
    formMenuElem.append(newTitle);
    title.remove();

    this.title = newTitle;
    if(this.element.hasClass('non-collapsible')) {
        this.title.addClass("doing");
    }
    this.questions = _.map(this.element.find("fieldset"), function(questionElement) {
        return new QuestionModel(questionElement, this, questionsTitlesList,$(questionElement).find("span.field-error").first());
    }, this);
}
SectionModel.prototype = new SelectableModel();
SectionModel.prototype.constructor = SectionModel;

SectionModel.prototype.click = function() {
    this.title.click();   // triggers click event which is handled in navigatorHandlers
}

SectionModel.prototype.enable = function() {
    SelectableModel.prototype.enable.apply(this);
    this.title.removeClass("disabled");
    _.each(this.questions, function(question) { question.enable(); });
}

SectionModel.prototype.disable = function() {
    SelectableModel.prototype.disable.apply(this);
    this.title.addClass("disabled");
    _.each(this.questions, function(question) { question.disable(); });
}

SectionModel.prototype.hide = function() {
    SelectableModel.prototype.hide.apply(this);
    this.title.hide(); // hide the title as well
    _.each(this.questions, function(question) { question.hide(); });
}

SectionModel.prototype.show = function() {
    SelectableModel.prototype.show.apply(this);
    this.title.show();  // show the title (regardless of whether or not the section is selected)
    _.each(this.questions, function(question) { question.show(); });
}

SectionModel.prototype.select = function() {
    SelectableModel.prototype.select.apply(this);
    this.title.addClass("doing");
    _.each(this.questions, function(question) { question.resetErrorMessages(); });
}
SectionModel.prototype.unselect = function() {
    SelectableModel.prototype.unselect.apply(this);
    if(!this.element.hasClass('non-collapsible')) {
        this.title.removeClass("doing");
    }
    _.each(this.questions, function(question) { question.unselect() });
}
SectionModel.prototype.isValid = function() {
    return this.isDisabled() || _.reduce(this.questions, function(memo, question) {
        return question.isValid() && memo;
    }, true);
}

SectionModel.prototype.onExit = function() {
    return _.reduce(this.questions, function(memo, question) {
        return question.onExit() && memo;
    }, true);
}

SectionModel.prototype.firstInvalidQuestion = function() {
    return _.find(this.questions, function(question) {
        return !question.isValid();
    });
}


function ConfirmationSectionModel(elem, formMenuElem, regularSections, skipConfirmation) {
    SelectableModel.apply(this, [elem]);
    this.sections = regularSections;
    this.skipConfirmation = skipConfirmation ? skipConfirmation : false;

    var title = this.element.find("span.title").first();
    var label = $('<span/>').html(title.text());
    var spanId = title.attr('id');
    if (spanId) {
    	label.attr('id', spanId);
    }
    this.title = $("<li/>").append(label);

    if (!this.skipConfirmation) {
        formMenuElem.append(this.title);
    }
    title.remove();
    this.dataCanvas = this.element.find('#dataCanvas');

    // allows other elements to inject messages into the confirmation display
    // all divs with class="confirmation-message" will be prepended to the confirmation page display
    var messages = $('.confirmation-message')
    this.element.find('#confirmation-messages').append(messages);

    this.questions = [ new ConfirmationQuestionModel(this.element.find("#confirmationQuestion"), this) ];
}
ConfirmationSectionModel.prototype = new SelectableModel();
ConfirmationSectionModel.prototype.constructor = ConfirmationSectionModel;
ConfirmationSectionModel.prototype.select = function() {
    SelectableModel.prototype.select.apply(this);
    this.title.addClass("doing");

    if (!this.skipConfirmation) {
        // scan through the form and confirm that at least one of the fields has a value
        // TODO: move all this out into a separate validator at some point? is the assumption that all forms must have data true?
        // TODO: makes sure this works for radio buttons and checkboxes (once we add them)
        var hasData = _.some(this.sections, function (section) {
            return _.some(section.questions, function (question) {
                return _.some(question.fields, function (field) {
                    return (field.value() && field.value().length > 0)
                })
            })
        })

        if (!hasData) {
            this.questions[0].confirm.disable();
            this.element.find(".error").show();
        }
        else {
            this.questions[0].confirm.enable();
            this.element.find(".error").hide();
        }

        // create the div that shows the summary of entered information
        var summaryDiv = $("<div></div>");
        this.dataCanvas.append(summaryDiv);
        _.each(this.sections, function (section) {
            _.each(section.questions, function (question) {
                if (!question.isDisabled() && question.showInConfirmation()) {

                    // question title is header, line per labeled field
                    if (question.multiLineInConfirmation()) {
                        summaryDiv.append("<h3>" + question.title().text() + "</h3>");
                        var displayLines = [];
                        _.each(question.fields, function (field) {
                            if (!field.isDisabled() && field.displayValue()) {
                                if (field.label) {
                                    displayLines.push(field.label + ": " + field.displayValue());
                                }
                                else {
                                    displayLines[displayLines.length - 1] += question.fieldSeparator + field.displayValue();
                                }
                            }
                        });
                        _.each(displayLines, function (line) {
                            summaryDiv.append("<p>" + line + "</p>");
                        });
                    }
                    // question title is label, all fields on single line
                    else {
                        summaryDiv.append("<p><span class='title'>" + question.title().text() + ": </span>"
                            + (question.valueAsText && !/^\s*$/.test(question.valueAsText) ? question.valueAsText : "--") + "</p>");

                    }
                }

            })
        });
    }
}
ConfirmationSectionModel.prototype.unselect = function() {
    SelectableModel.prototype.unselect.apply(this);
    this.title.removeClass("doing");
    this.dataCanvas.empty();
    _.each(this.questions, function(question) { question.unselect() });
}
ConfirmationSectionModel.prototype.isValid = function() {
    return true;
}