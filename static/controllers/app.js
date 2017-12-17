String.prototype.toProperCase = function () {
    return this.replace(/\w\S*/g, function (txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
};

String.prototype.replaceAll = function (str1, str2, ignore) {
    return this.replace(new RegExp(str1.replace(/([\/\,\!\\\^\$\{\}\[\]\(\)\.\*\+\?\|\<\>\-\&])/g, "\\$&"), (ignore ? "gi" : "g")), (typeof(str2) == "string") ? str2.replace(/\$/g, "$$$$") : str2);
};

var app = angular.module('app', ['ngRoute', 'ngFileSaver', 'ngAnimate', 'ui.bootstrap', 'ngStorage', 'ui.sortable'])
    .config(function ($routeProvider, $locationProvider) {
        $locationProvider.html5Mode(false).hashPrefix('');
        $routeProvider
        // Home
            .when('/', {
                templateUrl: '../../../static/views/pages/home.html',
                controller: 'HomeController'
            })
            // Analysis
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
            // Settings
            .when('/s', {
                templateUrl: '../../../static/views/pages/settings/event_settings.html',
                controller: 'SettingsHomeController'
            })
            .when('/s/c', {
                templateUrl: '../../../static/views/pages/settings/edit_calculations.html',
                controller: 'SettingsCalculationsController'
            })
            .when('/s/h', {
                templateUrl: '../../../static/views/pages/settings/edit_headers.html',
                controller: 'SettingsHeadersController'
            })
            // Setup
            .when('/setup', {
                templateUrl: '../../../static/views/pages/settings/event_setup.html',
                controller: 'SetupEventController'
            })
            // Sheets
            .when('/sheets', {
                templateUrl: '../../../static/views/pages/sheets/home.html',
                controller: 'SheetsHomeController'
            })
            .when('/sheets/create', {
                templateUrl: '../../../static/views/pages/sheets/edit.html',
                controller: 'SheetsEditController',
                resolve: {
                    appPath: function () {
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
            // User
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

    return function (items, params) {
        if (params === undefined) return items;


        var fields = [];
        var reverses = [];
        params[0].forEach(function (e) {
            var reverse = e.startsWith('-');
            reverses.push(reverse);
            if (reverse)
                fields.push(e.slice(1, e.length));
            else
                fields.push(e);
        });
        var headers = params[1];
        var filtered = [];
        items.forEach(function (e) {
            filtered.push(e);
        });

        if (fields === undefined || headers === undefined) return items;

        function sortData(a, b, i) {
            if (i === undefined) i = 0;
            var key = fields[i];
            var reverse = reverses[i];

            var a_val = parseFloat(getData(a, key));
            var b_val = parseFloat(getData(b, key));

            if (a_val > b_val) {
                return reverse ? -1 : 1;
            }
            else if (a_val < b_val) {
                return reverse ? 1 : -1;
            }
            else if (++i < fields.length) {
                return sortData(a, b, i);
            }
            return 0;
        }

        filtered.sort(sortData);

        return filtered;
    }
});

app.factory('EventTrackingService', function ($http, $localStorage, $sessionStorage, $log) {
    var service = {};

    service.getEventKey = function(){
        return service.getTrackedEvent().key;
    };

    service.isTrackingEvent = function () {
        return $sessionStorage.tracked_event != undefined && typeof $sessionStorage.tracked_event == typeof {};
    };

    service.getTrackedEvent = function () {
        return $sessionStorage.tracked_event;
    };

    service.setTrackedEvent = function (event) {
        $sessionStorage.tracked_event = event;
    };

    return service;
});


app.factory('EventDataService', function ($http, $localStorage, $sessionStorage, $log, EventTrackingService) {
    if ($localStorage.event_data === undefined) $localStorage.event_data = {};
    var service = {};

    service.loadEventAnalysis = function () {
        loadData('/get/event_analysis/', 'avg');
    };

    service.loadEventEntries = function () {
        loadData('/get/raw_entries/', 'raw');
    };

    service.loadEventInfo = function () {
        loadData('/get/event/', 'info')
    };

    service.loadEventHeaders = function () {
        loadData('/get/event_headers/', 'headers')
    };

    service.getEventData = function (key) {
        return getData(key);
    };

    service.getPageData = function (path) {
        switch (path) {
            default:
                return undefined;
            case '/a/a':
                return getData('avg');
            case '/a/e':
                return getData('raw');
        }
    };

    service.getPageHeaders = function (path) {
        return getData('headers')[path];
    };

    service.getTeamAnalysis = function (team) {
        var data = service.getEventData('avg');
        for (var i in data) {
            var elem = data[i];
            if (elem.team.mode === team) {
                return elem;
            }
        }
        return undefined;
    };

    service.getTeamEntries = function (team) {
        var data = service.getEventData('raw');
        var output = [];
        for (var i in data) {
            var elem = data[i];
            if (elem.team === team) {
                output.push(elem);
            }
        }
        return output;
    };

    service.resetLocalData = function () {
        $localStorage.event_data = {};
    };

    service.loadAvailableEvents = function () {
        $http.get('/get/available_events').then(function (resp) {
            $localStorage.available_events = resp.data;
        });
    };

    service.getAvailableEvents = function () {
        return $localStorage.available_events;
    };

    function getEventKey() {
        return EventTrackingService.getTrackedEvent().key;
    }

    function getData(key) {
        return $localStorage.event_data[key][getEventKey()];
    }

    function loadData(url, key) {
        if ($localStorage.event_data[key] === undefined) $localStorage.event_data[key] = {};
        $log.info("Trying to " + url.replaceAll('/', ' ').replaceAll('_', ' ') + "for " + getEventKey());
        $http.get(url + (getEventKey() || ""))
            .then(function (response) {
                    $log.info("Successfully " + url.replaceAll('/', ' ').replaceAll('_', ' ').trim() + " for " + getEventKey());
                    $localStorage.event_data[key][getEventKey()] = response.data;
                },
                function (ignored) {
                    $log.warn("Could not " + url.replaceAll('/', ' ').replaceAll('_', ' ').trim() + " for " + getEventKey());
                    $localStorage.event_data[key][getEventKey()] = [];
                });
    }

    return service;

});


app.factory('AuthenticationService', function ($http, $localStorage, $location, $route, $log) {
    var service = {};

    service.initGuestUser = function () {
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
                    console.log(resp);
                    success_callback(resp);
                },
                function (resp) {
                    fail_callback(resp);
                });

    };

    service.Logout = function (redirect) {
        $http.post('/logout')
            .then(function (ignored) {
                service.ClearCredentials();
                if (redirect === true) {
                    $location.path('/');
                }
            });
    };

    service.SetUserSettings = function (settings) {
        $localStorage.userSettings = settings;
    };

    service.LoadUserSettings = function () {
        $http.get('/get/user_settings/' + service.getUser().username)
            .then(function (response) {
                    service.SetUserSettings(response.data);
                },
                function (ignored) {
                    $log.error("Cannot get user settings");
                });
    };

    service.GetUserSettings = function () {
        return $localStorage.userSettings;
    };

    service.SetCredentials = function (user) {
        $localStorage.currentUser = user;
        updateUserRole();

        $http.defaults.headers.common['UserID'] = user.id;
        $http.defaults.headers.common['UserKey'] = user.key;
        service.LoadUserSettings();
    };

    function updateUserRole() {
        var roles = ['Guest', 'User,', 'Editor', 'Admin'];
        $localStorage.currentUser.role_index = roles.indexOf($localStorage.currentUser.role);
    }

    service.ClearCredentials = function () {
        $localStorage.currentUser = undefined;
        $localStorage.userSettings = undefined;
        $http.defaults.headers.common['UserID'] = '';
        $http.defaults.headers.common['UserKey'] = '';
    };

    service.testUser = function () {
        $http.post('/test_user', service.getUser())
            .then(function (resp) {
                    if (resp.status == 204) {
                        service.initGuestUser();
                    }
                    else {
                        service.SetCredentials(resp.data);
                    }
                },
                function (ignored) {
                    service.Logout();
                    service.initGuestUser();
                    $route.reload();
                });
    };

    service.getUser = function () {
        return $localStorage.currentUser;
    };

    service.getUserId = function(){
        return service.getUser().id;
    };

    service.getUserPermissions = function(){
        return service.getUser().permissions;
    };

    service.hasPermission = function(perm){
        return service.getUserPermissions().indexOf(perm) > 0;
    };

    service.isAuthorized = function (min_level) {
        return min_level < 1 || (service.getUser() != undefined && service.getUser().role_index >= min_level);

    };

    return service;
});

app.controller('ApplicationController', function ($scope, $rootScope, $localStorage, $sessionStorage, $location, $http,
                                                  $log, AuthenticationService, EventDataService, EventTrackingService) {

    if (AuthenticationService.getUser() === undefined || AuthenticationService.getUser().role_index < 1) {
        AuthenticationService.initGuestUser();
    }
    else {
        AuthenticationService.testUser();
    }

    $rootScope.data_loading = 0; // hide loading overlay

    EventDataService.loadAvailableEvents(); //
    $scope.available_events = EventDataService.getAvailableEvents(); // Add events to search box typeahead

    $scope.tracking_input_data = { // Set up the event search box.
        event: EventTrackingService.getTrackedEvent(),
        team: ''
    };

    $scope.$on('$routeChangeStart', function () {
        $rootScope.data_loading = 0;
        $scope.tracked_event = EventTrackingService.getTrackedEvent();
        $scope.tracking_input_data.event = EventTrackingService.getTrackedEvent() ? EventTrackingService.getTrackedEvent().info.data : '';
        $scope.user_data = AuthenticationService.getUser();
    });

    $scope.isNavCollapsed = true;
    $scope.select_event_button = function () {
        if (typeof($scope.tracking_input_data.event) == 'object') {
            $http.get('/get/event/' + $scope.tracking_input_data.event.key)
                .then(function (resp) {
                        EventTrackingService.setTrackedEvent(resp.data);
                        EventDataService.loadEventAnalysis();
                        EventDataService.loadEventEntries();
                        EventDataService.loadEventHeaders();
                        EventDataService.loadEventInfo();
                        $location.path('/a');
                    },
                    function (ignored) {
                        $log.error("Couldn't get event" + $scope.tracking_input_data.event.key);
                    });
        }
    };

});

app.controller('HomeController', function ($scope, $localStorage) {

});