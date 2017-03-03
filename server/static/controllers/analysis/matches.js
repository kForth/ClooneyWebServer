var app = angular.module('app');

app.controller('MatchesController', function ($scope, $cookies, $http, $sce, $location, $routeParams) {

    var level = "";
    if($routeParams.level != undefined){
        level = "/" + $routeParams.level;
    }

    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };

    $http.get("/api/headers/" + $scope.event.key + "/matches")
        .then(function (response) {
            $scope.headers = angular.copy(response.data);
        });

    $http.get('/api/event/' + $scope.event.key + '/matches' + level)
        .then(function (response) {
            if (response.data.length < 1) {
                angular.element(document.querySelector("#table"))[0].innerHTML = "No matches found.";
            }
            $scope.data = angular.copy(response.data);
        });

    $scope.trust = function (obj) {
        obj = String(obj);
        obj = $sce.trustAsHtml(obj);
        return obj;
    };

});