define( [
    'jquery'
], function ( $ ) {

    var ExtensionRenderer = function () {

        var appListUrl = '/openmrs/module/appframework/extensions.json',
            renderFunctions = {
                'link': drawLink,
                'img': drawImg
            };

        function getQueryString( params ) {
            return '?' + Object.keys( params ).map(
                function ( key ) {
                    return encodeURIComponent( key ) + '=' + encodeURIComponent( params[key] );
                }
            ).join( '&' );
        }

        function tagReplace( fragment, contextMap ) {
            return Object.keys( contextMap ).reduce( function ( accum, key ) {
                return accum.replace( '{{' + key + '}}', contextMap[key] );
            }, fragment );
        }

        function drawLink( extension, contextMap ) {
            return '<a href="' + tagReplace( extension.url, contextMap ) + '">' + extension.label + '</a>'
        }

        function drawImg( extension, contextMap ) {
            return '<img>';
        }

        function renderHtml( extension, contextMap ) {
            return renderFunctions[extension.type]( extension, contextMap );
        }

        this.registerRenderer = function( type, renderFunction ) {
            renderFunctions[type] = renderFunction;
        }

        this.renderExtensions = function ( appId, extensionPointId, domElementSelector, contextMap ) {
            // TODO: Make these links dynamic
            var extensions = JSON.parse(
                $.ajax( {
                    type: "GET",
                    url: appListUrl + getQueryString( { 'appId': appId, 'extensionPointId': extensionPointId } ),
                    async: false
                } ).responseText
            );

            extensions.forEach( function ( extension ) {
                var html = renderHtml( extension, contextMap );
                $( domElementSelector ).append( html );
            } );
        }
    };

    return ExtensionRenderer;
} );
