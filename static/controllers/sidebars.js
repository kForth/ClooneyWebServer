app.controller('SidebarController', function ($scope, $localStorage, $location) {
    $scope.nav = function (path) {
        $location.path(path);
    }
});

app.controller('SettingsSidebarController', function ($scope, $sessionStorage, $localStorage, $location, $http) {
    $scope.nav = function (path) {
        $location.path(path);
    };

    $scope.update_event = function () {
        $http.post('/update/event_analysis/' + $sessionStorage.tracked_event.key);
        console.log("update");
    };

    $scope.update_tba = function () {
        $http.get('/update/tba/' + $sessionStorage.tracked_event.key);
        console.log("update_tba");
    };
});