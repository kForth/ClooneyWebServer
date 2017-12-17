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

    $scope.avg_headers = [];
    $scope.raw_headers = [];
    $scope.team_raw_headers = [];
    $http.get('/get/header_groups/' + EventTrackingService.getEventKey())
        .then(function (resp) {
            for(var i in resp.data){
                var elem = resp.data[i];
                switch(elem['path']){
                    case '/a/a':
                        $scope.avg_headers.push(elem);
                        break;
                    case '/a/e':
                        $scope.raw_headers.push(elem);
                        break;
                    case '/a/t/e':
                        $scope.team_raw_headers.push(elem);
                        break;
                }
            }
        });

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

app.controller('SettingsHeadersController', function ($scope, $location, $http, AuthenticationService, EventDataService, EventTrackingService) {
    if (!EventTrackingService.isTrackingEvent() || !AuthenticationService.isAuthorized(2)) $location.path("/");

    var backup_groups = [];
    $scope.header_groups = [];

    $http.get('/get/header_groups/' + EventTrackingService.getEventKey())
        .then(function (resp) {
            $scope.header_groups = resp.data;
            backup_groups = angular.copy($scope.header_groups);
        });

    $scope.saveGroups = function(){
        $http.post('/post/header_groups/' + EventTrackingService.getEventKey(), $scope.header_groups)
            .then(function () {
                backup_groups = angular.copy($scope.header_groups);
            });
    };

    $scope.resetGroups = function(){
        $scope.header_groups = angular.copy(backup_groups);
    };

    $scope.getPageGroups = function(page){
        var groups = [];
        for(var i in $scope.header_groups){
            var elem = $scope.header_groups[i];
            if(elem.path == page.path){
                groups.push(elem);
            }
        }
        return groups;
    };

    $scope.createGroup = function(page){
        $http.post('/post/create_header_group/' + EventTrackingService.getEventKey(), {'path': page.path})
            .then(function(resp){
                $scope.header_groups.push(resp.data);
                $scope.selected_group = $scope.header_groups[$scope.header_groups.length - 1];
            });
    };

    var backup_selected_group = undefined;

    $scope.selectGroup = function(group){
        $scope.selected_group = group;
        $scope.canDeleteGroup = group.creator_id == AuthenticationService.getUser().id;
        $scope.canSetGlobalDefault = AuthenticationService.isAuthorized(3) || AuthenticationService.hasPermission('settings/header_groups/set_global_default');
        backup_selected_group = angular.copy(group);
    };

    $scope.saveGroup = function(){

    };

    $scope.resetGroup = function(){
        $scope.selected_group = angular.copy(backup_selected_group);
    };

    $scope.deleteGroup = function(){

    };

    $scope.setDefault = function(){
        if(group.creator_id == AuthenticationService.getUser().id){

        }
    };

    $scope.setGlobalDefault = function(){
        if(AuthenticationService.isAuthorized(3)){

        }
    };

    $scope.header_pages = [
        {
            'name': 'Averages',
            'path': '/a/a'
        },
        {
            'name': 'Entries',
            'path': '/a/e'
        },
        {
            'name': 'Team Entries',
            'path': '/a/t/e'
        }
    ];

    $scope.headers = [
        {"data_key": "match.count", "class": "", "title": "M#", "data_class": "", "tooltip": ""},
        {"data_key": "match.count", "class": "", "title": "Team", "data_class": "", "tooltip": ""}
    ];
});