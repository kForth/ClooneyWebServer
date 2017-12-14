app.controller('AnalysisHomeController', function ($scope, $location, EventTrackingService) {
    if (!EventTrackingService.isTrackingEvent()) $location.path("/");
});

app.controller('AnalysisAveragesController', function ($scope, $location, EventTrackingService, EventDataService, AuthenticationService) {
    if (!EventTrackingService.isTrackingEvent()) $location.path("/");

    $scope.headers = EventDataService.getPageHeaders($location.path());
    $scope.data = EventDataService.getPageData($location.path());
});

app.controller('AnalysisEntriesController', function ($scope, $localStorage, $location, EventTrackingService, EventDataService) {
    if (!EventTrackingService.isTrackingEvent()) $location.path("/");

    $scope.headers = EventDataService.getPageHeaders($location.path());
    $scope.data = EventDataService.getPageData($location.path());
});

app.controller('AnalysisInsightsController', function ($scope, $location, EventTrackingService) {
    if (!EventTrackingService.isTrackingEvent()) $location.path("/");
});

app.controller('AnalysisMatchesController', function ($scope, $location, EventTrackingService) {
    if (!EventTrackingService.isTrackingEvent()) $location.path("/");
});