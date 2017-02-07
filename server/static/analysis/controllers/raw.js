var app = angular.module('app');

app.controller('RawController', function ($scope, $cookies, $http, $sce) {
    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };

    $http.get("/api/headers/" + $scope.event.key + "/stats_raw")
        .then(function (response) {
            $scope.headers = response.data;
        });

    $http.get('/api/event/' + $cookies.get('selected-event-id') + '/stats/raw')
        .then(function (response) {
            $scope.data = response.data;
            if (response.data.length < 1) {
                angular.element(document.querySelector("#table"))[0].innerHTML = "No data available."
            }
        });

    $scope.trust = function (obj) {
        obj = String(obj);
        obj = $sce.trustAsHtml(obj);
        return obj;
    };

});