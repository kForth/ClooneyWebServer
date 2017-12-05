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
            .when('/a/i', {
                templateUrl: '../../../static/views/pages/event/insights.html',
                controller: 'AnalysisInsightsController'
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


app.directive('highlightTable', function ($location, $sessionStorage) {
    function link(scope) {
        if ($sessionStorage.colours == undefined) $sessionStorage.colours = {};
        scope.colours = $sessionStorage.colours[$location.path()] || {};

        scope.$watch('colours', function () {
            $sessionStorage.colours[$location.path()] = scope.colours;
        });

        scope.$watch(function () {
            return angular.toJson($sessionStorage);
        }, function () {
            scope.colours = $sessionStorage.colours[$location.path()];
        });

        scope.clearColours = function(event){
            if(event.shiftKey || event.ctrlKey || event.metaKey){
                scope.colours = {};
            }
        };

        scope.cycleColour = function (event, index) {
            if (scope.colours[index] === undefined)
                scope.colours[index] = 0;
            if (event.shiftKey) {
                scope.colours[index] = 0;
            }
            else if (event.ctrlKey || event.metaKey) {
                scope.colours[index] -= 1;
            }
            else {
                scope.colours[index] += 1;
            }
        };
    }

    return {
        link: link,
        restrict: 'A'
    };
});

app.directive('datacell', function(){
    function getData(obj, keys) {
        keys.split(".").forEach(function (key) {
            if (obj === undefined || keys === undefined) return obj;
            obj = obj[key];
        });
        return obj;
    }

    function link(scope){
        scope.value = getData(scope.dcElement, scope.dcHeader.data_key);
        if(parseFloat(scope.value) == scope.value && parseInt(scope.value) != scope.value){
            scope.value = scope.value.toFixed(2);
        }
    }

    return {
        link: link,
        restrict: 'E',
        template: "<span ng-class='dcHeader.data_class'>{{ value }}</span>",
        scope: {
            'dcHeader': '=',
            'dcElement': '='
        }
    }
});

app.directive('multiSortTable', function ($location, $sessionStorage) {

    function link(scope) {
        if ($sessionStorage.sorts == undefined) $sessionStorage.sorts = {};
        scope.sorts = $sessionStorage.sorts[$location.path()];
        if (scope.sorts === undefined)
            scope.sorts = [];

        scope.$watch('sorts', function () {
            $sessionStorage.sorts[$location.path()] = scope.sorts;
        });

        scope.$watch(function () {
            return angular.toJson($sessionStorage);
        }, function () {
            scope.sorts = $sessionStorage.sorts[$location.path()];
        });


        scope.getData = function (obj, keys) {
            keys.split(".").forEach(function (e) {
                if (obj === undefined || keys === undefined) return obj;
                obj = obj[e];
            });
            return obj;
        };

        scope.sortData = function (event, key) {
            if (event.shiftKey) {
                scope.sorts = [];
            }
            if (scope.sorts.indexOf("-" + key) > -1) {
                if (event.ctrlKey || event.metaKey) {
                    scope.sorts.splice(scope.sorts.indexOf(key), 1);
                }
                else {
                    scope.sorts[scope.sorts.indexOf("-" + key)] = key;
                }
            }
            else if (scope.sorts.indexOf(key) > -1) {
                if (event.ctrlKey || event.metaKey) {
                    scope.sorts[scope.sorts.indexOf(key)] = "-" + key;
                }
                else {
                    scope.sorts.splice(scope.sorts.indexOf(key), 1);
                }
            }
            else {
                scope.sorts.push("-" + key);
            }
        };
    }

    return {
        link: link,
        restrict: 'A'
    };
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
        return $sessionStorage.tracked_event != undefined;
    };

    service.getTrackedEvent = function(){
        return $sessionStorage.tracked_event;
    };

    service.setTrackedEvent = function(event){
        $sessionStorage.tracked_event = event;
    };

    service.loadEventAnalysis = function (){
        loadData(service.getTrackedEvent().key, '/get/event_analysis/', '/a/a');
    };

    service.loadEventEntries = function (){
        loadData(service.getTrackedEvent().key, '/get/raw_entries/', '/a/e');
    };

    service.getEventData = function(path){
        return $localStorage.event_data[path][$sessionStorage.tracked_event.key];
    };

    service.resetLocalData = function(){
        $localStorage.event_data = {};
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


app.factory('AuthenticationService', function ($http, $localStorage) {
    var service = {};

    service.Login = Login;
    service.SetCredentials = SetCredentials;
    service.GetUserSettings = GetUserSettings;
    service.ClearCredentials = ClearCredentials;
    service.isAuthorized = isAuthorized;

    return service;

    function Login(username, password, success_callback, fail_callback) {
        $http.post('/login', {username: username, password: password})
            .then(function (resp) {
                    SetCredentials(resp.data);
                    success_callback(resp);
                    GetUserSettings(username);
                },
                function (resp) {
                    fail_callback(resp);
                });

    }

    function GetUserSettings(username) {
        $http.get('/get/user_settings/' + username)
            .then(function (response) {
                    $localStorage.userSettings = response.data;
                },
                function (ignored) {
                    console.error("Cannot get user settings");
                });
    }

    function SetCredentials(user) {
        $localStorage.currentUser = user;

        $http.defaults.headers.common['Authorization'] = user.key;
    }

    function ClearCredentials() {
        $localStorage.currentUser = undefined;
        $localStorage.userSettings = undefined;
        $http.defaults.headers.common.Authorization = '';
        GetUserSettings('');
    }

    function isAuthorized(min_level) {
        return $localStorage.currentUser != undefined && $localStorage.userSettings != undefined &&
            $localStorage.currentUser.user.role >= min_level;

    }
});

app.controller('ApplicationController', function ($scope, $rootScope, $localStorage, $sessionStorage, $location, $http, AuthenticationService, EventDataService) {
    AuthenticationService.GetUserSettings('');
    $rootScope.data_loading = 0;

    $scope.$on('$routeChangeStart', function () {
        $rootScope.data_loading = 0;
        $scope.tracked_event = EventDataService.getTrackedEvent();
        $scope.tracking_input_data.event = $scope.tracked_event.data;

        if ($localStorage.currentUser != undefined) {
            $scope.user_data = $localStorage.currentUser;
        }
    });

    $scope.available_events = [];
    $scope.update_available_events = function () {
        $http.get('/get/available_events').then(function (resp) {
            $scope.available_events = resp.data;
        });
    };
    $scope.update_available_events();

    $scope.tracking_input_data = {
        'event': '',
        'team': ''
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