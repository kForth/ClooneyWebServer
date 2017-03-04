var app = angular.module('app');

app.directive('sortableTable', function () {
    function link(scope) {
        var lastSortKey;
        var lastSortOrder;
        scope.sortList = function (key) {
            if (key === lastSortKey) {
                lastSortOrder *= -1;
            }
            else {
                lastSortOrder = 1;
            }
            lastSortKey = key;
            scope.data.sort(function (a, b) {
                var value = (scope.getData(a, key) > scope.getData(b, key) ? 1.0 : scope.getData(a, key) < scope.getData(b, key) ? -1 : 0);
                return value * (lastSortOrder > 0 ? -1 : 1);
            });
        };
        scope.getId = function (ids, elem) {
            if (ids === undefined) {
                return "";
            }
            return ids.map(function (obj) {
                return elem[obj];
            }).join("_");
        };
        scope.getData = function (elem, key) {
            if (key.includes(",")) {
                var keys = key.split(",");
                var val = elem;
                keys.forEach(function (key) {
                    val = val[key.trim()];
                });
                return val;
            }
            else {
                return elem[key];
            }
        };
    }

    return {
        link: link,
        restrict: 'A'
    };
});