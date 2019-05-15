(function($, _, OpenMRS) {

    // you should always wrap a full REST representation of the encounter (not a ref or default) if you plan to use the participatedIn or createdBy functionality
    OpenMRS.EncounterModel = function(obj) {
        $.extend(this, obj);
    }

    OpenMRS.EncounterModel.prototype = {
        constructor: OpenMRS.EncounterModel,

        canBeDeletedBy: function(userModel) {
            return userModel.hasPrivilege("Task: emr.patient.encounter.delete");
        },

        canBeEditedBy: function(userModel) {
            return userModel.hasPrivilege("Task: emr.patient.encounter.edit");
        },

        // you should always wrap a full REST representation of the encounter (or a custom rep that includes creator) if you plan to use the createdBy functionality
        createdBy: function(userModel) {

            var creator;

            if (this.creator) {
                creator = this.creator;
            }
            else if (this.auditInfo && this.auditInfo.creator) {
                creator  = this.auditInfo.creator;
            }

            if (!creator) {
                return false; // if we don't know the creator, we can't answer, so default to false
            }

            return creator && creator.uuid == userModel.uuid;
        },

        // you should always wrap a full REST representation of the encounter (or a custom rep that includes at least a default rep of encounterProviders)
        // if you plan to use the participatedIn functionality
        participatedIn: function(provider) {
            if (!provider || !provider.uuid) {
                return false;
            }
            return _.find(this.encounterProviders, function(p) {
                return p.provider && p.provider.uuid == provider.uuid;
            })
        }
    }

})(jQuery, _, window.OpenMRS=window.OpenMRS||{});