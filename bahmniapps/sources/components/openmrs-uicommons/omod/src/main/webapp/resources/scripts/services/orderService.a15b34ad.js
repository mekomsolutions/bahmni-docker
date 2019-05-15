angular.module('orderService', ['ngResource', 'uicommons.common'])
    .factory('Order', function($resource) {
        return $resource("/" + OPENMRS_CONTEXT_PATH  + "/ws/rest/v1/order/:uuid", {
            uuid: '@uuid'
        },{
            query: { method:'GET', isArray:false } // OpenMRS RESTWS returns { "results": [] }
        });
    })
    .factory('OrderService', function(Order) {

        return {

            /**
             * Fetches Orders
             *
             * @param params to search against
             * @returns $promise of array of matching Orders (REST ref representation by default)
             */
            getOrders: function(params) {
                return Order.query(params).$promise.then(function(res) {
                    return res.results;
                });
            }
        }
    });