app.controller('AnalysisHomeController', function ($scope, $location, EventDataService) {
    if (!EventDataService.isTrackingEvent()) $location.path("/");
});

app.controller('AnalysisAveragesController', function ($scope, $localStorage, $location, EventDataService, AuthenticationService) {
    if (!EventDataService.isTrackingEvent()) $location.path("/");

    $scope.headers = AuthenticationService.GetUserSettings().headers[$location.path()];
    $scope.data = EventDataService.getEventData($location.path());
});

app.controller('AnalysisEntriesController', function ($scope, $localStorage, $location, EventDataService) {
    if (!EventDataService.isTrackingEvent()) $location.path("/");

    $scope.headers = $localStorage.userSettings.headers[$location.path()];
    $scope.data = EventDataService.getEventData($location.path());
});

app.controller('AnalysisInsightsController', function ($scope, $location, EventDataService) {
    if (!EventDataService.isTrackingEvent()) $location.path("/");
});

app.controller('AnalysisMatchesController', function ($scope, $location, EventDataService) {
    if (!EventDataService.isTrackingEvent()) $location.path("/");
});