Handlebars.registerHelper('message', function(code) {
    return emr.message(code);
});

Handlebars.registerHelper('nvl', function(val, ifNull) {
    return val === null || val === '' ? ifNull : val;
});