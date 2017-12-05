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
        $localStorage.event_data['/a/a'][$sessionStorage.tracked_event.key] = undefined;
        $http.post('/update/event_analysis/' + $sessionStorage.tracked_event.key);
        console.log("update");
    };

    $scope.update_tba = function () {
        console.log("update_tba");
    };
});