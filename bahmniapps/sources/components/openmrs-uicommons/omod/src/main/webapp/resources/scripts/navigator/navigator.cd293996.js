
// TODO we may want to remove this global variable as some point; not sure if it is still used in ref app somewhere
var Navigator = {isReady: false}


// TODO figure out out to set up mocking to test this
function KeyboardController(formElement) {

    var initFormModels = function(formEl) {
        var formElement = formEl;
        if (!formElement) {
            formElement = $('div#content > form').first();
        }
        formElement.prepend('<ul id="formBreadcrumb" class="options"></ul>');
        var breadcrumb = formElement.find('#formBreadcrumb').first();

        var sections = _.map(formElement.find('section'), function(s) {
            return new SectionModel(s, breadcrumb);
        });

        var confirmationSection = new ConfirmationSectionModel($('#confirmation'), breadcrumb, _.clone(sections), formElement.hasClass('skip-confirmation-section'));
        sections.push(confirmationSection);

        var questions = _.flatten( _.map(sections, function(s) { return s.questions; }), true);
        var fields = _.flatten(_.map(questions, function(q) { return q.fields; }), true);
        return [sections, questions, fields];

    }

    var initKeyboardHandlersChain = function(questions, fields) {
        var questionsHandler = QuestionsKeyboardHandler(questions);
        var fieldsHandler = FieldsKeyboardHandler(fields, questionsHandler);
        return fieldsHandler;
    }

    var initMouseHandlers = function(sections, questions, fields) {
        sectionsMouseHandlerInitializer(sections);
        questionsMouseHandlerInitializer(questions);
        fieldsMouseHandlerInitializer(fields);
    }

    var modelsList = initFormModels(formElement);
    var sections=modelsList[0], questions=modelsList[1], fields=modelsList[2];
    initMouseHandlers(sections, questions, fields);
    var handlerChainRoot = initKeyboardHandlersChain(questions, fields);

    handlerChainRoot.handleTabKey();

    $('body').keydown(function(key) {
        switch(key.keyCode ? key.keyCode : key.which) {
            case 38:
                handlerChainRoot.handleUpKey() && key.preventDefault();
                break;
            case 40:
                handlerChainRoot.handleDownKey() && key.preventDefault();
                break;
            case 27:
                handlerChainRoot.handleEscKey() && key.preventDefault();
                break;
            case 9:
                if(key.shiftKey) {
                    handlerChainRoot.handleShiftTabKey();
                } else {
                    handlerChainRoot.handleTabKey();
                }
                key.preventDefault();
                break;
            case 13:
                handlerChainRoot.handleEnterKey() && key.preventDefault();
            default:
                break;
        }
    });

    // TODO we may want to remove this global variable as some point; not sure if it is still used in ref app somewhere
    Navigator.isReady = true;

    var api = {};

    // searches by the id of the widget, e.g. <p><label>...</label><input id="search-for-me"/></p>
    api.getFieldById = function(id) {
        return _.find(fields, function(element) {
            return element.id == id;
        })
    }

    // searches by the id of the <p> around the widget, e.g. <p id="search-for-me"><label>...</label><input/></p>
    api.getFieldByContainerId = function(id) {
        return _.find(fields, function(element) {
            return element.container.attr('id') == id;
        })
    }

    api.getQuestionById = function(id) {
        return _.find(questions, function(element) {
            return element.id == id;
        })
    }

    api.getSectionById = function(id) {
        return _.find(sections, function(element) {
            return element.id == id;
        })
    }

    api.getSections = function() {
        return sections;
    }

    api.getQuestions = function() {
        return questions;
    }

    api.getFields = function() {
        return fields;
    }

    // in an Html Form the Keyboard Controller is exposed as a "NavigatorController" global variable,
    // so, for instance, we can access these API methods via NavigatorController.stepBackward();

    // used to automatically step back and forward throughout the form; note that this just triggers the
    // appropriate underlying key, so therefore all required validation must pass before it it allowed to step forward
    api.stepBackward = function() {
        handlerChainRoot.handleShiftTabKey();
    }

    api.stepForward = function() {
        handlerChainRoot.handleTabKey();
    }


    return api;
}