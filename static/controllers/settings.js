app.controller('SettingsHomeController', function ($scope, $location, AuthenticationService, $http, EventDataService) {
    if (!EventDataService.isTrackingEvent() || !AuthenticationService.isAuthorized(2)) $location.path("/");

    $scope.saveSettings = function () {
        $http.post('/set/event_settings/' + EventDataService.getTrackedEvent().key, {'settings': $scope.settings})
            .then(function (resp) {
                console.log(resp);
            });
    };

    $scope.revertSettings = function () {
        $scope.settings = angular.copy($scope.backup);
    };

    $http.get('/get/event_settings/' + EventDataService.getTrackedEvent().key)
        .then(function (resp) {
            $scope.settings = resp.data.settings;
            $scope.backup = angular.copy($scope.settings);

        });
    $http.get('/get/sheets')
        .then(function (resp) {
            $scope.sheets = resp.data;
            console.log($scope.sheets);
        });
});

app.controller('SettingsCalculationsController', function ($scope, $location, AuthenticationService, EventDataService) {
    if (!EventDataService.isTrackingEvent() || !AuthenticationService.isAuthorized(2)) $location.path("/");
    $scope.calculations = [
        {'name': 'a', 'key': 'a', 'formula': 'x*x', 'type': 'float'},
        {'name': 'b', 'key': 'b', 'formula': 'x+y', 'type': 'float'},
        {'name': 'c', 'key': 'c', 'formula': 'x+y*x-y/x/x', 'type': 'float'},
        {'name': 'd', 'key': 'd', 'formula': 'x+2', 'type': 'float'}
    ];
});