var app = angular.module('app');

app.controller('OprsController', function ($scope, $cookies, $http, $sce) {
    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };

    $http.get("/api/headers/" + $scope.event.key + "/oprs")
        .then(function (response) {
            $scope.headers = response.data;
        });

    $http.get('/api/event/' + $cookies.get('selected-event-id') + '/oprs')
        .then(function (response) {
            $scope.data = response.data;
            console.log(response.data);
            if (response.data.length < 1) {
                angular.element(document.querySelector("#table"))[0].innerHTML = "No OPRs found."
            }
        });
    $scope.trust = function (obj) {
        obj = String(obj);
        obj = $sce.trustAsHtml(obj);
        return obj;
    };

});