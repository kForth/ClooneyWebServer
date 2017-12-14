app.service('EventSettingsService', function ($http, $localStorage, $sessionStorage, $log, EventTrackingService) {
    var service = {};

    service.loadEventSettings = function(){
        return loadData('/get/event_settings/', 'settings');
    };

    service.getEventSettings = function(){
        return getData('settings');
    };

    service.setEventSettings = function(new_settings){
        $log.info("Trying to set event settings for " + getEventKey());
        $http.post('/set/event_settings/' + getEventKey(), new_settings)
            .then(function(resp){
                $log.info("Successfully set event settings for " + getEventKey());
            },
            function(resp){
                $log.info("Failed to set event settings for " + getEventKey());
            });
    };

    function getEventKey(){
        return EventTrackingService.getTrackedEvent().key;
    }

    function getData(key){
        return $localStorage.event_settings[key][getEventKey()];
    }

    function loadData(url, key){
        if ($localStorage.event_settings === undefined) $localStorage.event_settings = {};
        if ($localStorage.event_settings[key] === undefined) $localStorage.event_settings[key] = {};
        $log.info("Trying to" + url.replaceAll('/', ' ').replaceAll('_', ' ') + "for " + getEventKey());
        $http.get(url + (getEventKey() || ""))
            .then(function (response) {
                $log.info("Successfully" + url.replaceAll('/', ' ').replaceAll('_', ' ') + "for " + getEventKey());
                $localStorage.event_settings[key][getEventKey()] = response.data;
            },
            function(ignored){
                $log.warn("Could not" + url.replaceAll('/', ' ').replaceAll('_', ' ') + "for " + getEventKey());
                $localStorage.event_settings[key][getEventKey()] = [];
            });
    }

    return service;

});

app.controller('SettingsHomeController', function ($scope, $location, AuthenticationService, $http, EventDataService,
                                                   EventTrackingService, EventSettingsService, SheetsService) {

    EventSettingsService.loadEventSettings();
    SheetsService.loadEventSheets();

    if (!EventTrackingService.isTrackingEvent() || !AuthenticationService.isAuthorized(2)){
        $location.path("/");
        return;
    }

    $scope.saveSettings = function () {
        EventSettingsService.setEventSettings($scope.settings)
    };

    $scope.revertSettings = function () {
        $scope.settings = angular.copy($scope.backup);
    };

    $scope.settings = EventSettingsService.getEventSettings();
    $scope.backup = angular.copy($scope.settings);
    $scope.sheets = SheetsService.getEventSheets();
});

app.controller('SettingsCalculationsController', function ($scope, $location, AuthenticationService, EventDataService, EventTrackingService) {
    if (!EventTrackingService.isTrackingEvent() || !AuthenticationService.isAuthorized(2)) $location.path("/");


    $scope.calculations = [
        {'name': 'a', 'key': 'a', 'formula': 'x*x', 'type': 'float'},
        {'name': 'b', 'key': 'b', 'formula': 'x+y', 'type': 'float'},
        {'name': 'c', 'key': 'c', 'formula': 'x+y*x-y/x/x', 'type': 'float'},
        {'name': 'd', 'key': 'd', 'formula': 'x+2', 'type': 'float'}
    ];
});