var app = angular.module('app');

app.controller('EventSidebarController', function ($scope, $location, $cookies, $http, $route) {
    $scope.isActive = function (viewLocation) {
        return viewLocation.replace("/", "") === $location.path().split('/')[1];
    };

    $scope.getSelectedEvent = function () {
        var event = $cookies.get('selected-event-name');
        if (event === undefined) {
            return 'Select'
        }
        return event;
    };

    $scope.isSelectedEvent = function (event) {
        return event === $cookies.get('selected-event-id');
    };

    $scope.selectEvent = function (event) {
        $cookies.put('selected-event-id', event.id);
        $cookies.put('selected-event-name', event.name);
        $route.reload()
    };

    $scope.match_levels = [
          {
              link: "",
              name: "All Matches"
          },
          {
              link: "qm",
              name: "Qualification"
          },
          {
              link: "qf",
              name: "Quarter-Finals"
          },
          {
              link: "sf",
              name: "Semi-Finals"
          },
          {
              link: "f",
              name: "Finals"
          }
      ];

    $scope.getSelectedLevel = function() {
        if($location.path().split('/')[1] == "m" && $location.path().split('/').length > 2){
            return $location.path().split('/')[2].toUpperCase();
        }
        else{
            return "Select";
        }
    };

    $http.get("/api/events")
        .then(function (response) {
            $scope.events = response.data;
        });

});