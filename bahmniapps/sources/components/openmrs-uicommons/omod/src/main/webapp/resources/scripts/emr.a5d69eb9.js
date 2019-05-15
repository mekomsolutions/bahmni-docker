var emr = (function($) {

    var accentMap = {
        "ä": "a", "á": "a", "à": "a", "â": "a", "ã": "a",
        "Ä": "A", "Á": "A", "À": "A", "Â": "A", "Ã": "A",
        "é": "e", "è": "e", "ê": "e", "ë": "e", "œ": "e","æ":"e",
        "É": "E", "È": "E", "Ê": "E", "Ë": "E",
        "ï": "i", "ì": "i", "í": "i", "î": "i",
        "Ï": "I", "Ì": "I", "Í": "I", "Î": "I",
        "ö": "o", "ó": "o", "ò": "o", "ô": "o", "õ": "o",
        "Ö": "O", "Ó": "O", "Ò": "O", "Ô": "O", "Õ": "O",
        "ü": "u", "ú": "u", "ù": "u", "û": "u",
        "Ü": "U", "Ú": "U", "Ù": "U", "Û": "U",
        "ÿ": "y", "Ÿ": "Y", "ñ": "n", "Ñ": "N",
        "ç": "c", "Ç": "C", "ß": "s"
    };

    var toQueryString = function(options) {
        var ret = "?";
        if (options) {
            for (key in options) {
                var val = options[key];
                if ($.isArray(val)) {
                    for (ind in val) {
                        ret += key + '=' + encodeURIComponent(val[ind]) + '&';
                    }
                } else {
                    ret += key + '=' + encodeURIComponent(val) + '&';
                }
            }
        }
        return ret;
    };

    var requireOptions = function() {
        var opts = arguments[0];
        for (var i = 1; i < arguments.length; ++i) {
            if (!opts[arguments[i]]) {
                throw "Missing option: " + arguments[i];
            }
        }
    };

    var jqObject = $();

    return {

        // just used in testing so we can replace the instance with a mock or spy as needed
        setJqObject: function(jqueryInstanceToSet)  {
            jqObject = jqueryInstanceToSet;
        },

        loadMessages: function(codes, callback) {
            if (!window.messages) {
                window.messages = {};
            }
            emr.getFragmentActionWithCallback("uicommons", "messages", "get", { codes: codes }, function(response) {
                for (var code in response) {
                    window.messages[code] = response[code];
                }
                if (callback) {
                    callback(window.messages);
                }
            });
        },

        loadGlobalProperties: function(properties, callback) {
            if (!window.globalProperties) {
                window.globalProperties = {};
            }
            emr.getFragmentActionWithCallback("uicommons", "globalProperties", "get", {properties: properties}, function(response) {
                for (var property in response) {
                    window.globalProperties[property] = response[property];
                }
                if (callback) {
                    callback(window.globalProperties);
                }
            });
        },

        message: function(code, defaultText) {
            if (window.messages) {
                var translated = window.messages[code];
                return translated ? translated : (defaultText ? defaultText : code);
            } else {
                return defaultText ? defaultText : code;
            }
        },

        serverValidationErrorMessage: function(response) {
            var errorMessages = [];
            if (response.data && response.data.error) {
                var errors = response.data.error;
                errorMessages.push(errors.message);
                if (errors.globalErrors) {
                    jq.each(errors.globalErrors, function(i, ele){
                        errorMessages.push(ele.message);
                    });
                }

                if (errors.fieldErrors) {
                    jq.map(errors.fieldErrors, function(fErrors, fName){
                        jq.each(fErrors, function(i, ele){
                            errorMessages.push(ele.message);
                        });
                    });
                }
            }

            var foundMessage = false;
            if(errorMessages.length > 0){
                jq.each(errorMessages, function(i, errMessage){
                    if(errMessage && jq.trim(errMessage) != ''){
                        if(foundMessage == false){
                            foundMessage = true;
                        }
                        emr.errorMessage(errMessage);
                    }
                });
            }

            if(foundMessage == false) {
                emr.errorMessage(this.message("uicommons.generalError.message", "An error has occurred"));
            }
        },

        serverGeneralErrorMessage: function() {
            emr.errorMessage(this.message("uicommons.generalError.message", "An error has occurred"));
        },

        navigateTo: function(opts) {
            var url = opts.url;
            if (opts.applicationUrl) {
                url = '/' + OPENMRS_CONTEXT_PATH
                    + (opts.applicationUrl.charAt(0) == '/' ? '' : '/')
                    + opts.applicationUrl;
            }
            if (opts.page) {
                var provider = opts.provider;
                if (provider == null) {
                    provider = "*"
                }
                url = this.pageLink(provider, opts.page, opts.query);
            }
            location.href = url;
        },

        pageLink: function(providerName, pageName, options) {
            var ret = '/' + OPENMRS_CONTEXT_PATH + '/' + providerName + '/' + pageName + '.page';
            return ret + toQueryString(options);
        },

        resourceLink: function(providerName, resourceName) {
            if (providerName == null)
                providerName = '*';
            return '/' + OPENMRS_CONTEXT_PATH + '/ms/uiframework/resource/' + providerName + '/' + resourceName;
        },

        fragmentActionLink: function(providerName, fragmentName, actionName, options) {
            var ret = '/' + OPENMRS_CONTEXT_PATH + '/' + providerName + '/' + fragmentName + '/' + actionName + '.action';
            return ret += toQueryString(options);
        },

        getFragmentActionWithCallback: function(providerName, fragmentName, actionName, options, callback, errorCallback) {
            if (!errorCallback) {
                errorCallback = function(xhr) {
                    emr.handleError(xhr);
                };
            }
            var url = this.fragmentActionLink(providerName, fragmentName, actionName, options);
            $.getJSON(url).success(callback).error(errorCallback);
        },

        /*
         * opts should contain:
         *   provider (defaults to '*')
         *   fragment
         *   action
         *   query, e.g. { q: "bob", checkedInAt: 5 }
         *   resultTarget e.g. '#search-results'
         *   resultTemplate (should be an underscore template)
         */
        ajaxSearch: function(opts) {
            var provider = opts.provider;
            if (!provider) {
                provider = '*';
            }
            var url = this.fragmentActionLink(provider, opts.fragment, opts.action);
            var target = $(opts.resultTarget);
            $.getJSON(url, opts.query)
                .success(function(data) {
                    target.html('');
                    jq.each(data, function(i, result) {
                        jq(opts.resultTemplate(result)).appendTo(target);
                    });
                })
                .error(function(err) {
                    emr.errorMessage(err);
                });
        },

        successMessage: function(message) {
            jqObject.toastmessage( 'showToast', { type: 'success',
                                              position: 'top-right',
                                              text:  emr.message(message) } );
        },

        errorMessage: function(message) {
            jqObject.toastmessage( 'showToast', { type: 'error',
                                              position: 'top-right',
                                              sticky: true,
                                              text:  emr.message(message) } );
        },

        alertMessage: function(message) {
            jqObject.toastmessage( 'showToast', { type: 'alert',
                                              position: 'top-right',
                                              text:  emr.message(message) } );
        },

        successAlert: function(message, options) {
            jqObject.toastmessage( 'showToast', { type: 'success',
                position: 'top-right',
                text:  emr.message(message),
                stayTime: 8000,
                close: options && options.close ? options.close : null } );
        },

        errorAlert: function(message, options) {
            jqObject.toastmessage( 'showToast', { type: 'error',
                position: 'top-right',
                text:  emr.message(message),
                stayTime: 8000,
                close: options && options.close ? options.close : null } )
        },

        handleError: function(xhr) {
            emr.handleParsedError(jq.parseJSON(xhr.responseText), xhr.status);
        },

        handleParsedError: function(data, status) {
            if (!emr.redirectOnAuthenticationFailure(status)) {
                if (data.globalErrors) {
                    emr.errorAlert(data.globalErrors[0]);
                } else if (data.error.message) {
                    emr.errorAlert(data.error.message);
                } else {
                    emr.errorAlert("Error!");
                }
            }
        },

        redirectOnAuthenticationFailure: function (status) {
            if (status == 403) {
                window.location = '/' + OPENMRS_CONTEXT_PATH;
                return true;
            }
            return false;
        },

        updateBreadcrumbs: function(extraBreadcrumbs) {
            if (!Array.isArray(breadcrumbs)) {
                // In case the page defines no JS var called breadcrumbs, but does have an html element with that id
                return;
            }
            var toUse = breadcrumbs;
            if (extraBreadcrumbs) {
                toUse = _.clone(breadcrumbs);
                if (extraBreadcrumbs == null || extraBreadcrumbs.length == 0) {
                    var index = toUse.length - 1;
                    var modified = _.clone(toUse[index]);
                    if(modified.link !=null){
                        modified.link = null;
                    }
                    toUse[index] = modified;
                }
                _.each(extraBreadcrumbs, function(item) {
                    toUse.push(item);
                })
            }
            $('#breadcrumbs').html(this.generateBreadcrumbHtml(toUse));
        },

        generateBreadcrumbHtml: function(breadcrumbs) {
            var breadcrumbTemplate = _.template($('#breadcrumb-template').html());
            var html = "";

            _.each(breadcrumbs, function(item, index) {
                html += breadcrumbTemplate({ breadcrumb: item, first: index == 0, last: index == breadcrumbs.length-1 });
            });
            return html;
        },

        /*
         * returns an object with show() and close() functions
         */
        setupConfirmationDialog: function(opts) {
            requireOptions(opts, 'selector');
            var element = $(opts.selector);
            element.hide();
            if (opts.actions) {
                if (opts.actions.confirm) {
                    element.find(".confirm").unbind('click');
                    element.find(".confirm").click(opts.actions.confirm);
                }
                if (opts.actions.cancel) {
                    element.find(".cancel").unbind('click');
                    element.find(".cancel").click(opts.actions.cancel);
                }
            }

            var dialogApi = {};
            var dialogOpts = {
                overlayClose: true,
                overlayId: "modal-overlay",
                opacity: 80,
                persist: true,
                closeClass: "cancel"
            };
            if (opts.dialogOpts) {
                $.extend(dialogOpts, opts.dialogOpts);
            }

            dialogApi.show = function() {
                $(opts.selector).modal(dialogOpts);
            };
            dialogApi.close = function() {
                $.modal.close();
            };

           return dialogApi;
        },

        stripAccents: function(term) {
            var ret = "";
            for ( var i = 0; i < term.length; i++ ) {
                ret += accentMap[ term.charAt(i) ] || term.charAt(i);
            }
            return ret;
        },

        formatAsHtml: function(str) {
            return str.replace(/\n/g,'<br/>')
        },

        isFeatureEnabled: function(key) {
            return featureToggles[key];
        },

        applyContextModel: function(input, contextModel) {
            if (contextModel) {

                $.each(contextModel, function(key, value) {
                    var pattern = new RegExp('{{\\s*' + key + '\\s*}}', 'g');
                    input = input.replace(pattern, value);
                });

                // handle substitions for patterns that have already been escaped
                $.each(contextModel, function(key, value) {
                    var pattern = new RegExp('%7B%7Bs*' + key + 's*%7D%7D', 'g');
                    input = input.replace(pattern, value);
                });
            }
            return input;
        },

		getJSON: function(url, data, success) {
			var settings = {
				dataType: "json",
				url: url,
				data: data,
				success: success,
				beforeSend: function(xhr) {
					xhr.setRequestHeader('Disable-WWW-Authenticate', 'true');
				}
			};

			return jq.ajax(settings).fail(emr.handleNotLoggedIn);
		},

        handleNotLoggedIn: function(jqXHR) {
           if (jqXHR.status == 401 || jqXHR.status == 404) {
               if (confirm(emr.message("uicommons.notLoggedIn", "The operation cannot be completed, because you are no longer logged in. Do you want to go to login page?"))) {
                   window.location = "/" + OPENMRS_CONTEXT_PATH + "/login.htm";
               }
           }
        },

        domId: function(useIfNotNull, prefix, suffix) {
            if (useIfNotNull) {
                return useIfNotNull;
            }
            return (prefix ? prefix : 'id-') + Math.floor(Math.random() * 10000) + (suffix ? suffix : '');
        },

        isCompatibleWithSessionLocale: function(locale) {
            return window.sessionContext.locale.slice(0, locale.length) === locale ||
                locale.slice(0, window.sessionContext.locale.length) === window.sessionContext.locale;
        },

        focusNextElement: function(within, afterThisOne) {
            var fields = within.find('button,input,textarea,select');
            var index = fields.index(afterThisOne);
            if (index > -1 && (index + 1) < fields.length) {
                fields.eq(index + 1).focus();
            }
        },

        startsWithIgnoreCase: function(string, lookFor) {
            return string.toLowerCase().indexOf(lookFor.toLowerCase()) === 0;
        },

        hasMapping: function(concept, sourceName, code) {
            if (concept.mappings) {
                // this quick hack implementation presumes the concept mapping's display property is like "CIEL: 1513"
                var lookForDisplay = sourceName + ": " + code;
                return _.findWhere(concept.mappings, {display: lookForDisplay})
            }
            return null;
        },

        findConceptWithMapping: function(conceptArray, sourceName, code) {
            return _.find(conceptArray, function(concept) {
                return emr.hasMapping(concept, sourceName, code);
            });
        },

        // given a JS Date object, an existing Moment object, or ISO 8601 string,
        // returns a String properly formatted for a OpenMRS REST request
        // ** requires moment.js to be included on the page **
        formatDatetimeForREST: function(date) {
            return moment(date).format("YYYY-MM-DDTHH:mm:ss.SSSZZ");
        }

    };

})(jQuery);

var jq = jQuery;
_.templateSettings = {
    interpolate : /{{=(.+?)}}/g ,
    escape : /{{-(.+?)}}/g ,
    evaluate : /{{(.+?)}}/g
};
