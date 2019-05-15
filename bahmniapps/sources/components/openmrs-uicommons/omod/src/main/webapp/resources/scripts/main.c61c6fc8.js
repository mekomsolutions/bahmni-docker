
function getMyUrl() {
    // Not using Array.forEach and similar methods since they might not be supported on older browsers
    var myUrl;
    var scripts = document.getElementsByTagName('script');
    for(var i = 0; i < scripts.length; i++) {
        var match = scripts[i]['src'].match(/.*uicommons\/scripts\/main\.js/);
        if(match != null) {
            myUrl = match[0];
            break;
        }
    }
    if (!myUrl) {
        console.log('FATAL! Unable to find self URL for configuring requirejs')
    }
    return myUrl.substr(0, myUrl.lastIndexOf('/') + 1);
}

require.config({
    shim: {
        underscore: {
            exports: '_'
        }
    },

    paths: {
        jquery: getMyUrl() + 'jquery-1.12.4.min',
        underscore: getMyUrl() + 'underscore-min',
        text: getMyUrl() + 'require/text',

        uiCommons: getMyUrl(),

        // The resourceBaseUrl URL would typically end up being something like
        //      http://localhost:8080/openmrs/moduleResources
        //
        // This would enable developers to conveniently include code using
        //
        //      eg., require([resourceBaseUrl/myModuleName/my/path/to/my/resource])
        //
        resourceBaseUrl: getMyUrl() + '../../',

        // The main URL would be the main scripts directory in UI Commons Library,
        // so all module using it can refer to files inside it as
        //
        //      eg., require(['main/emr.js'])
        //
        main: '.'
    }

});

define([
    'jquery',
    'underscore'
], function( $, _ ) {

    // Initial bootstrap code can be written here.
    console.log('Application main loaded.')
    console.log('jquery ' + $.fn.jquery)

});
