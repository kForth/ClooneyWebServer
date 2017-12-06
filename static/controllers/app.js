var app = angular.module('app', ['ngRoute', 'ngFileSaver', 'ngAnimate', 'ui.bootstrap', 'ngStorage', 'ui.sortable'])
    .config(function ($routeProvider, $locationProvider) {
        $locationProvider.html5Mode(false).hashPrefix('');
        $routeProvider
            .when('/', {
                templateUrl: '../../../static/views/pages/home.html',
                controller: 'HomeController'
            })

            .when('/a', {
                templateUrl: '../../../static/views/pages/event/home.html',
                controller: 'AnalysisHomeController'
            })
            .when('/a/a', {
                templateUrl: '../../../static/views/pages/event/averages.html',
                controller: 'AnalysisAveragesController'
            })
            .when('/a/m', {
                templateUrl: '../../../static/views/pages/event/matches.html',
                controller: 'AnalysisMatchesController'
            })
            .when('/a/e', {
                templateUrl: '../../../static/views/pages/event/entries.html',
                controller: 'AnalysisEntriesController'
            })

            .when('/s', {
                templateUrl: '../../../static/views/pages/settings/event_settings.html',
                controller: 'SettingsHomeController'
            })
            .when('/s/c', {
                templateUrl: '../../../static/views/pages/settings/edit_calculations.html',
                controller: 'SettingsCalculationsController'
            })

            .when('/setup', {
                templateUrl: '../../../static/views/pages/settings/event_setup.html',
                controller: 'SetupEventController'
            })

            .when('/sheets', {
                templateUrl: '../../../static/views/pages/sheets/home.html',
                controller: 'SheetsHomeController'
            })
            .when('/sheets/create', {
                templateUrl: '../../../static/views/pages/sheets/edit.html',
                controller: 'SheetsEditController',
                resolve: {
                    appPath: function ($route) {
                        return {'mode': 'create'};
                    }
                }
            })
            .when('/sheets/edit/:id', {
                templateUrl: '../../../static/views/pages/sheets/edit.html',
                controller: 'SheetsEditController',
                resolve: {
                    appPath: function ($route) {
                        return {'mode': 'edit', 'id': $route.current.params.id};
                    }
                }
            })

            .when('/login', {
                templateUrl: '../../../static/views/pages/user/login.html',
                controller: 'UserLoginController'
            })
            .when('/logout', {
                templateUrl: '../../../static/views/pages/user/login.html',
                controller: 'UserLogoutController'
            })
            .when('/register', {
                templateUrl: '../../../static/views/pages/user/register.html',
                controller: 'UserRegisterController'
            })

            .otherwise({
                redirectTo: '/'
            });
    });

app.filter('orderDataBy', function () {
    function getData(obj, keys) {
        if (obj === undefined || keys === undefined) return obj;
        keys.split(".").forEach(function (e) {
            obj = obj[e];
        });
        return obj;
    }

    return function(items, field, reverse) {
        var filtered = [];
        items.forEach(function(e){filtered.push(e);});

        filtered.sort(function(a, b) {
            if(getData(a, field) > getData(b, field)) {
                return 1;
            }
            else if(getData(a, field) > getData(b, field)){
                return -1;
            }
            else{
                return 0;
            }
        });

        if (reverse)
            filtered.reverse();

        return filtered;
    }
});


app.factory('EventDataService', function ($http, $localStorage, $sessionStorage, $log) {
    if ($localStorage.event_data === undefined) $localStorage.event_data = {};
    var service = {};

    service.isTrackingEvent = function(){
        return $sessionStorage.tracked_event != undefined && typeof $sessionStorage.tracked_event == typeof {};
    };

    service.getTrackedEvent = function(){
        return $sessionStorage.tracked_event;
    };

    service.setTrackedEvent = function(event){
        $sessionStorage.tracked_event = event;
    };

    service.loadEventAnalysis = function (){
        loadData(service.getTrackedEvent().key, '/get/event_analysis/', 'avg');
    };

    service.loadEventEntries = function (){
        loadData(service.getTrackedEvent().key, '/get/raw_entries/', 'raw');
    };

    service.getEventData = function(key){
        return $localStorage.event_data[key][$sessionStorage.tracked_event.key];
    };

    service.getPageData = function(path){
        switch(path){
            default:
                return undefined;
            case '/a/a':
                return service.getEventData('avg');
            case '/a/e':
                return service.getEventData('raw');
        }
    };

    service.getTeamAnalysis = function(team){
        var analysis_data = service.getEventData('avg');
        console.log(analysis_data);
    };

    service.resetLocalData = function(){
        $localStorage.event_data = {};
    };

    service.loadAvailableEvents = function () {
        $http.get('/get/available_events').then(function (resp) {
            $localStorage.available_events = resp.data;
        });
    };

    service.getAvailableEvents = function(){
        return $localStorage.available_events;
    };

    function loadData(event_key, url, path){
        if ($localStorage.event_data[path] === undefined) $localStorage.event_data[path] = {};
        $log.info("Trying to " + url + " for " + event_key);
        $http.get(url + (event_key || ""))
            .then(function (response) {
                $log.info("Successfully " + url + " for " + event_key);
                $localStorage.event_data[path][event_key] = response.data;
            },
            function(ignored){
                $log.warn("Could not " + url + " for " + event_key);
                $localStorage.event_data[path][event_key] = [];
            });
    }

    return service;

});


app.factory('AuthenticationService', function ($http, $localStorage, $location) {
    var service = {};

    service.initGuestUser = function(){
        service.ClearCredentials();
        service.SetCredentials({
            'id': -1,
            'key': '',
            'user': {
                'id': -1,
                'username': 'guest',
                'role': 'Guest',
                'first_name': 'Guest',
                'last_name': 'Guestington'
            }
        });
    };

    service.Login = function (username, password, success_callback, fail_callback) {
        $http.post('/login', {username: username, password: password})
            .then(function (resp) {
                    service.SetCredentials(resp.data);
                    success_callback(resp);
                },
                function (resp) {
                    fail_callback(resp);
                });

    };

    service.Logout = function(redirect){
        $http.post('/logout')
            .then(function(ignored){
                service.ClearCredentials();
                if(redirect === true) {
                    $location.path('/');
                }
            });
    };

    service.SetUserSettings = function(settings){
        $localStorage.userSettings = settings;
    };

    service.LoadUserSettings = function (){
        $http.get('/get/user_settings/' + service.getUser().username)
            .then(function (response) {
                    service.SetUserSettings(response.data);
                },
                function (ignored) {
                    console.error("Cannot get user settings");
                });
    };

    service.GetUserSettings = function(){
        return $localStorage.userSettings;
    };

    service.SetCredentials = function (user) {
        $localStorage.currentUser = user;
        updateUserRole();

        $http.defaults.headers.common['UserID'] = user.id;
        $http.defaults.headers.common['UserKey'] = user.key;
        service.LoadUserSettings();
    };

    function updateUserRole(){
        var roles = ['Guest', 'User,', 'Editor', 'Admin'];
        $localStorage.currentUser.role_index = roles.indexOf($localStorage.currentUser.user.role);
    }

    service.ClearCredentials = function(){
        $localStorage.currentUser = undefined;
        $localStorage.userSettings = undefined;
        $http.defaults.headers.common['UserID'] = '';
        $http.defaults.headers.common['UserKey'] = '';
    };

    service.testUser = function(){
        $http.post('/test_user', service.getUser())
            .then(function(resp){
                if(resp.status == 204) {
                    service.initGuestUser();
                }
                else{
                    service.SetCredentials(resp.data);
                }
            },
            function(ignored){
                service.Logout();
            });
    };

    service.getUser = function(){
        return $localStorage.currentUser;
    };

    service.isAuthorized = function (min_level) {
        return $localStorage.currentUser != undefined && $localStorage.userSettings != undefined &&
            $localStorage.currentUser.user.role >= min_level;

    };

    return service;
});

app.controller('ApplicationController', function ($scope, $rootScope, $localStorage, $sessionStorage, $location, $http, AuthenticationService, EventDataService) {
    console.log(AuthenticationService.getUser());
    if(AuthenticationService.getUser() === undefined || AuthenticationService.getUser().user.role == 'Guest'){
        AuthenticationService.initGuestUser();
    }
    else{
        AuthenticationService.testUser();
    }

    EventDataService.loadAvailableEvents();
    $rootScope.data_loading = 0;

    $scope.$on('$routeChangeStart', function () {
        $rootScope.data_loading = 0;
        $scope.tracked_event = EventDataService.getTrackedEvent();
        $scope.tracking_input_data.event = EventDataService.getTrackedEvent() ? EventDataService.getTrackedEvent().info.data : '';
        $scope.user_data = AuthenticationService.getUser();
    });

    $scope.available_events = EventDataService.getAvailableEvents();

    $scope.tracking_input_data = {
        event: EventDataService.getTrackedEvent(),
        team: ''
    };

    $scope.isNavCollapsed = true;
    $scope.select_event_button = function () {
        if (typeof($scope.tracking_input_data.event) == 'object') {
            $http.get('/get/event/' + $scope.tracking_input_data.event.key)
                .then(function (resp) {
                        EventDataService.setTrackedEvent(resp.data);
                        EventDataService.loadEventAnalysis();
                        EventDataService.loadEventEntries();
                        $location.path('/a');
                    },
                    function (ignored) {
                        console.error("Couldn't get event" + $scope.tracking_input_data.event.key);
                    });
        }
    };


    String.prototype.toProperCase = function () {
        return this.replace(/\w\S*/g, function (txt) {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        });
    };

});

app.controller('HomeController', function ($scope, $localStorage) {

});