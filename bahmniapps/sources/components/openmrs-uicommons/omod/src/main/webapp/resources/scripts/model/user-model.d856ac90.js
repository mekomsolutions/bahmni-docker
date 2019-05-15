(function($, _, OpenMRS) {
    // you should always wrap a default/full REST representation of the user (not a ref) to be able to do privilege-checking operations
    OpenMRS.UserModel = function(obj) {
        $.extend(this, obj);
    }

    OpenMRS.UserModel.prototype = {
        constructor: OpenMRS.UserModel,

        hasPrivilege: function(privName) {
            return !! _.findWhere(this.privileges, { display: privName });
        }
    }

})(jQuery, _, window.OpenMRS=window.OpenMRS||{});