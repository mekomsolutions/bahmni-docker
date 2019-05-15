/*
 * Base prototype for field validators
 */
function FieldValidator() {};
FieldValidator.prototype = {
    constructor: FieldValidator,
    validate: function(field) {
        var value = field.value();
        //For radios, check if there is a checked radio in the group in the fieldset
        if ($(field.element).attr('type') == 'radio'){
            var fieldName = field.element.attr('name');
            var groupRadios = field.element.parent().parent().find("input:radio[name="+fieldName+"]");
            _.each(groupRadios, function(groupRadio){
                //ignore the radio that this validator was triggered for
                if($(groupRadio).val() != field.element.val()){
                    if($(groupRadio).is(':checked')){
                        value = field.element.val();
                    }
                }
            });
        }
        if(!this.isValid(value)) {
            return emrMessages[this.messageIdentifier];
        }
        return null;
    }
}

/*
 * Base prototype for question validators
 */
function QuestionValidator() {};
QuestionValidator.prototype = {
    constructor: QuestionValidator,
    validate: function(question) {}
}

function RequiredFieldValidator() {
    this.messageIdentifier = "requiredField";
}
RequiredFieldValidator.prototype = new FieldValidator();
RequiredFieldValidator.prototype.constructor = RequiredFieldValidator;
RequiredFieldValidator.prototype.isValid = function(fieldValue) {
    return fieldValue != null && fieldValue.length > 0;
}


function DateFieldValidator() {
    this.messageIdentifier = "dateField";
    this.futureDateMessageIdentifier = "dateInFuture";
    this.selectedMonthHas30Days="selectedMonthHas30Days";
    this.februaryDaysOutOfRange="februaryDaysOutOfRange";
}
DateFieldValidator.prototype = new FieldValidator();
DateFieldValidator.prototype.constructor = DateFieldValidator;
DateFieldValidator.prototype.validate = function(field){
    return this.validateInternal(field.value(), $(field.element).hasClass('use-time'), $(field.element).hasClass('no-future-date'));
}
DateFieldValidator.prototype.validateInternal = function(value, hasTime, rejectFutureDates){

    if(value && $.trim(value).length > 0) {
        value = $.trim(value);
        var dateRegex = /^(\d{1,2})-(\d{1,2})-(\d{4})$/;
        if (hasTime)
            dateRegex = /^(\d{1,2})-(\d{1,2})-(\d{4})\s(\d{1,2}):(\d{1,2})$/;

        var regexResult = dateRegex.exec(value);
        if(!regexResult)
            return emrMessages[this.messageIdentifier];

        var day=regexResult[1], month=regexResult[2], year=regexResult[3];
        if(day < 1 || day > 31 || month < 1 || month > 12){
            return emrMessages[this.messageIdentifier];
        }else if(month == 2 && (day > 29 || (day > 28 && year % 4 != 0))){
                return emrMessages[this.februaryDaysOutOfRange];
        }else if(day > 30 && (month == 4 || month == 6 || month == 9 || month == 11)){
            return emrMessages[this.selectedMonthHas30Days];
        }

        if(rejectFutureDates){
            var dateObject;
            if(hasTime)
                dateObject = new Date(year, month-1, day, regexResult[4], regexResult[5]);
            else
                dateObject = new Date(year, month-1, day);

            if(dateObject > new Date())
                return emrMessages[this.futureDateMessageIdentifier];
        }
    }
    return null;
}

function IntegerFieldValidator() {
    this.messageIdentifier = "integerField";
}
IntegerFieldValidator.prototype = new FieldValidator();
IntegerFieldValidator.prototype.constructor = IntegerFieldValidator;
IntegerFieldValidator.prototype.isValid = function(fieldValue) {
    var integerRegex = /^-?\d+$/;
    if (fieldValue && fieldValue.length > 0) {
        return integerRegex.test(fieldValue);
    }
    return true;
}


function NumberFieldValidator() {
    this.messageIdentifier = "numberField";
}
NumberFieldValidator.prototype = new FieldValidator();
NumberFieldValidator.prototype.constructor = NumberFieldValidator;
NumberFieldValidator.prototype.isValid = function(fieldValue) {
    var numberRegex = /^-?((\d+(\.\d+)?)|(\.\d+))$/;
    if (fieldValue && fieldValue.length > 0) {
        return numberRegex.test(fieldValue);
    }
    return true;
}


function NumericRangeFieldValidator() {
    this.lowMessageIdentifier = "numericRangeLow";
    this.highMessageIdentifier = "numericRangeHigh";
}
NumericRangeFieldValidator.prototype = new FieldValidator();
NumericRangeFieldValidator.prototype.constructor = NumericRangeFieldValidator;
NumericRangeFieldValidator.prototype.validate = function(field) {
    var asNumber = parseFloat(field.value());
    if (asNumber != null && !isNaN(asNumber)) {
        var rangeMin = parseFloat(field.element.attr("min"));
        if (rangeMin != null && !isNaN(rangeMin)) {
            if (asNumber < rangeMin) {
                return emrMessages[this.lowMessageIdentifier].replace("{0}", rangeMin);
            }
        }
        var rangeMax = parseFloat(field.element.attr("max"));
        if (rangeMax != null && !isNaN(rangeMax)) {
            if (asNumber > rangeMax) {
                return emrMessages[this.highMessageIdentifier].replace("{0}", rangeMax);
            }
        }
    }
    return null;
}

function RegexFieldValidator(){
    this.messageIdentifier = "invalid";
}
RegexFieldValidator.prototype = new FieldValidator();
RegexFieldValidator.prototype.constructor = RegexFieldValidator;
RegexFieldValidator.prototype.validate = function(field) {
    var regex = field.element.attr('regex');
    if(!new RegExp(regex).test(field.value()))
        return emrMessages[this.messageIdentifier];
    return null;
}

function PhoneFieldValidator() {
    this.messageIdentifier = "phoneField";
}
PhoneFieldValidator.prototype = new FieldValidator();
PhoneFieldValidator.prototype.constructor = PhoneFieldValidator;
PhoneFieldValidator.prototype.isValid = function(fieldValue) {
    var phoneRegex = /^\+?[\d \-\(\)]+$/;
    if (fieldValue && fieldValue.length > 0) {
        return phoneRegex.test(fieldValue);
    }
    return true;
}

var Validators = {
    required: new RequiredFieldValidator(),
    date: new DateFieldValidator(),
    integer: new IntegerFieldValidator(),
    number: new NumberFieldValidator(),
    "numeric-range": new NumericRangeFieldValidator(),
    regex: new RegexFieldValidator(),
    phone: new PhoneFieldValidator()
}

/****************   QUESTION VALIDATORS   *****/

function RequireAtLeastOneFieldQuestionValidator(){
    this.messageIdentifier = "atleastOneFieldRequired";
}
RequireAtLeastOneFieldQuestionValidator.prototype = new FieldValidator();
RequireAtLeastOneFieldQuestionValidator.prototype.constructor = RequireAtLeastOneFieldQuestionValidator;
RequireAtLeastOneFieldQuestionValidator.prototype.validate = function(questionModel) {
    var anyFieldHasValue =  _.any(questionModel.fields, function(field) {
        return field.value() && $.trim(field.value()).length > 0;
    });
    if(!anyFieldHasValue)
        return emrMessages[this.messageIdentifier];
    return null;
}

function MultipleInputDateQuestionValidator(){}
MultipleInputDateQuestionValidator.prototype = new QuestionValidator();
MultipleInputDateQuestionValidator.prototype.constructor = MultipleInputDateQuestionValidator;
MultipleInputDateQuestionValidator.prototype.validate = function(questionModel) {
    var dayValue = $.trim(questionModel.element.find('input.day').first().val());
    var monthValue = $.trim(questionModel.element.find('select.month').first().val());
    var yearValue = $.trim(questionModel.element.find('input.year').first().val());

    var estimatedDateEnabled = (questionModel.element.find('input.years') != null);

    var yearsValue = '';
    var monthsValue = '';

    if (estimatedDateEnabled) {
        yearsValue = $.trim(questionModel.element.find('input.years').first().val());
        monthsValue = $.trim(questionModel.element.find('input.months').first().val());
    }

    if(dayValue.length > 0 || monthValue.length > 0 || yearValue.length > 0){
        var fullDate = dayValue+'-'+monthValue+'-'+yearValue;
        var rejectFutureDates = questionModel.element.hasClass('no-future-date');
        return new DateFieldValidator().validateInternal(fullDate, false, rejectFutureDates);
    } else if (questionModel.element.hasClass('date-required') && yearsValue.length == 0 && monthsValue.length == 0) {
        return emrMessages['requiredField'];
    }
    return null;
}

var QuestionValidators = {
    requireOne: new RequireAtLeastOneFieldQuestionValidator(),
    "multiple-input-date": new MultipleInputDateQuestionValidator()
}