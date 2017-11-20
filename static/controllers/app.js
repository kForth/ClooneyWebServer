var app = angular.module('app', ['ngRoute', 'ngAnimate', 'ui.bootstrap', 'ngCookies', 'ui.sortable'])
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
                controller: 'SheetsCreateController'
            })
            .when('/sheets/edit', {
                templateUrl: '../../../static/views/pages/sheets/edit.html',
                controller: 'SheetsEditController'
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


app.directive('highlightTable', function ($location, $cookies) {
    function link(scope) {
        var cookie_prefix = $location.$$path.replace("/", "-");
        try {
            scope.colours = JSON.parse($cookies.get(cookie_prefix + ":highlighted-rows"));
        }
        catch (ex) {
        }
        if (scope.colours === undefined)
            scope.colours = {};

        scope.cycleColour = function (index) {
            if (scope.colours[index] === undefined)
                scope.colours[index] = 0;
            scope.colours[index]++;
            $cookies.put(cookie_prefix + ":highlighted-rows", JSON.stringify(scope.colours));
        };
    }

    return {
        link: link,
        restrict: 'A'
    };
});

app.directive('multiSortTable', function ($location, $cookies) {

    function link(scope) {
        var cookie_prefix = $location.$$path.replace("/", "");
        try {
            scope.sorts = JSON.parse($cookies.get(cookie_prefix + '-table-sort'));
        }
        catch (ex) {
        }

        if (scope.sorts === undefined)
            scope.sorts = [];

        scope.sortData = function (event, key) {
            if (event.shiftKey) {
                scope.sorts = [];
            }
            if (scope.sorts.indexOf("-" + key) > -1) {
                scope.sorts[scope.sorts.indexOf("-" + key)] = key;
            }
            else if (scope.sorts.indexOf(key) > -1) {
                scope.sorts.splice(scope.sorts.indexOf(key), 1);
            }
            else {
                scope.sorts.push("-" + key);
            }

            $cookies.put(cookie_prefix + '-table-sort', JSON.stringify(scope.sorts));
        };
    }

    return {
        link: link,
        restrict: 'A'
    };
});

app.controller('ApplicationController', function ($scope, $location, $http, $rootScope) {
    $scope.data_loading = false;

    $scope.$on('$routeChangeStart', function () {
        $scope.data_loading = false;
        $scope.tracking_input_data.event = $scope.tracked_event;
        if ($rootScope.globals != undefined && $rootScope.globals.currentUser != undefined) {
            $scope.user_data = $rootScope.globals.currentUser;
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
    $scope.tracked_event_okay = false;
    $scope.select_event_button = function () {
        if (typeof($scope.tracking_input_data.event) == 'object') {
            $scope.tracked_event = $scope.tracking_input_data.event;
            $scope.tracked_event_okay = true;
            $location.path('/a');
        }
    };

});

app.controller('SidebarController', function ($scope, $location) {
    $scope.nav = function (path) {
        $location.path(path);
    }
});

app.controller('HomeController', function ($scope) {

});

app.factory('AuthenticationService', function ($http, $cookies, $rootScope) {
    var service = {};

    service.Login = Login;
    service.SetCredentials = SetCredentials;
    service.ClearCredentials = ClearCredentials;
    service.isAuthorized = isAuthorized;

    return service;

    function Login(username, password, success_callback, fail_callback) {
        $http.post('/login', {username: username, password: password})
            .then(function (resp) {
                    success_callback(resp);
                },
                function (resp) {
                    fail_callback(resp);
                });

    }

    function SetCredentials(user) {

        $rootScope.globals = {
            currentUser: user
        };

        $http.defaults.headers.common['Authorization'] = 'Basic ' + user.key;

        var cookieExp = new Date();
        cookieExp.setDate(cookieExp.getDate() + 7);
        $cookies.putObject('globals', $rootScope.globals, {expires: cookieExp});
    }

    function ClearCredentials() {
        $rootScope.globals = {};
        $cookies.remove('globals');
        $http.defaults.headers.common.Authorization = 'Basic';
    }

    function isAuthorized(min_level) {
        return $rootScope.globals != undefined && $rootScope.globals.currentUser != undefined &&
            $rootScope.globals.currentUser.user.role >= min_level;

    }
});

app.controller('UserLogoutController', function ($scope, $location, AuthenticationService) {
    AuthenticationService.ClearCredentials();
    $location.path("/login");
});

app.controller('UserLoginController', function ($scope, $location, AuthenticationService) {
    if (AuthenticationService.isAuthorized(0)) $location.path("/");
    $scope.input = {
        'username': '',
        'password': ''
    };
    AuthenticationService.ClearCredentials();

    $scope.closeAlert = function () {
        $scope.alert = undefined;
    };

    $scope.login = function () {
        $scope.data_loading = true;
        AuthenticationService.Login($scope.input.username, $scope.input.password,
            function (response) {
                AuthenticationService.SetCredentials(response.data);
                $location.path('/');
            },
            function (ignored) {
                $scope.alert = 'Error. Try Again.';
                $scope.data_loading = false;
            });
    }

});

app.controller('UserRegisterController', function ($scope, $location, $http) {
    $scope.input = {
        'first_name': '',
        'last_name': '',
        'username': '',
        'password': ''
    };

    $scope.closeAlert = function () {
        $scope.alert = undefined;
    };

    $scope.register = function () {
        $scope.data_loading = true;
        $http.post('/users/create/', $scope.input)
            .then(function (ignored) {
                    $location.path('/login');
                },
                function (ignored) {
                    $scope.alert = 'Error. Try Again.';
                    $scope.data_loading = false;
                });
    }
});

app.controller('AnalysisHomeController', function ($scope, $location) {
    if ($scope.tracked_event === undefined) $location.path("/");
});

app.controller('AnalysisAveragesController', function ($scope, $location) {
    if ($scope.tracked_event === undefined) $location.path("/");
});

app.controller('AnalysisInsightsController', function ($scope, $location) {
    if ($scope.tracked_event === undefined) $location.path("/");
});

app.controller('AnalysisMatchesController', function ($scope, $location) {
    if ($scope.tracked_event === undefined) $location.path("/");
});

app.controller('AnalysisEntriesController', function ($scope, $location) {
    if ($scope.tracked_event === undefined) $location.path("/");
});

app.controller('SettingsHomeController', function ($scope, $location, AuthenticationService) {
    if ($scope.tracked_event === undefined || !AuthenticationService.isAuthorized(2)) $location.path("/");
});

app.controller('SettingsCalculationsController', function ($scope, $location, AuthenticationService) {
    if ($scope.tracked_event === undefined || !AuthenticationService.isAuthorized(2)) $location.path("/");
    $scope.calculations = [
        {'name': 'a', 'key': 'a', 'formula': 'x*x', 'type': 'float'},
        {'name': 'b', 'key': 'b', 'formula': 'x+y', 'type': 'float'},
        {'name': 'c', 'key': 'c', 'formula': 'x+y*x-y/x/x', 'type': 'float'},
        {'name': 'd', 'key': 'd', 'formula': 'x+2', 'type': 'float'}
    ];
});

app.controller('SetupEventController', function ($scope, $location, $http, AuthenticationService) {
    if (!AuthenticationService.isAuthorized(2)) $location.path("/");
    $scope.setup_step = 0;
    $scope.default_data =
        [
            {
                "id": "key",
                "label": "Event Key",
                "default_value": "",
                "type": "text"
            },
            {
                "id": "name",
                "label": "Event Name",
                "default_value": "",
                "type": "text"
            },
            {
                "id": "short_name",
                "label": "Short Name",
                "default_value": "",
                "type": "text"
            }
        ];

    $scope.alert = false;
    $scope.closeAlert = function () {
        $scope.alert = false
    };

    //Step 0 - Ask if we should use TBA
    $scope.setup_with_tba_button = function () {
        $scope.setup_step = 1;
        $scope.searchable_events = [];
        $http.get('/get/search_events').then(function (resp) {
            $scope.searchable_events = resp.data;
        });
    };

    $scope.setup_manually_button = function () {
        $scope.setup_step = 2;
    };

    //Step 1 - (TBA Only) Search for the event.
    $scope.event_search = {'input': ''};
    $scope.setup_tba_event = function () {
        $scope.alert = false;
        var event = $scope.event_search.input;
        $http.post('/setup_tba_event', {'key': event.key})
            .then(function (resp) {
                    if (resp.status === 200) {
                        $scope.update_available_events();
                        $scope.tracked_event = event;
                        $scope.tracked_event_okay = true;
                        $location.path('/s');
                    }
                },
                function (resp) {
                    if (resp.status === 409) {
                        $scope.alert = {type: 'danger', msg: event.key + ' has already been setup.'};
                    }
                    else {
                        $scope.alert = {
                            type: 'danger',
                            msg: 'Some kind of error occurred with ' + event.key + '. Try again?'
                        };
                    }
                });
    };

    //Step 2 - Edit the event information
    $scope.input_data = {};
    $scope.submit_manual_data = function () {
        console.log($scope.input_data);
        // $location.path('/s/e');
    };


});


app.controller('SheetsHomeController', function ($scope, $location, $http, AuthenticationService) {
    // if (!AuthenticationService.isAuthorized(2)) $location.path("/");
    $scope.sheets = [];
    $http.get('/get/sheets')
        .then(function (resp) {
            $scope.sheets = resp.data;

        });
});

app.controller('SheetsEditController', function ($scope, $location, $http, AuthenticationService) {
    $scope.sheet_mode = 'edit';
});

app.controller('SheetsCreateController', function ($scope, $location, $http, AuthenticationService) {
    $scope.sheet_mode = 'create';
    $scope.expanded = {};

    $scope.fields = [];

    $scope.saveEditField = function(){
        $scope.fields[$scope.selected_field_index] = $scope.selected_field;
        $scope.cancelEditField();
    };

    $scope.cancelEditField = function(){
        $scope.selected_field = undefined;
    };

    $scope.editField = function(field){
        $scope.selected_field_index = $scope.fields.indexOf(field);
        $scope.selected_field = angular.copy(field);
    };

    $scope.addField = function(type, field){
        var new_field = {
            'type': type
        };
        for(var i in field){
            var option = field[i];
            switch(option.type){
                default:
                case 'text':
                    new_field[option.id] = option.value || "";
                    break;
                case 'number':
                    new_field[option.id] = option.value || 0;
                    break;
                case 'checkbox':
                    new_field[option.id] = option.value || false;
                    break;
            }
        }

        var existing_keys = [];
        $scope.fields.forEach(function(e){ existing_keys.push(e.key || []);});
        var i = 0;
        if(existing_keys.indexOf(new_field.key) !== -1) new_field.key = new_field.key + "_" + (++i);
        while(existing_keys.indexOf(new_field.key) !== -1){
            new_field.key = new_field.key.substring(0, new_field.key.length - 1 - (++i).toString().length) + "_" + i.toString();
        }
        new_field.name = new_field.key.replace(/_/g, " ").toProperCase();

        $scope.fields.push(new_field);
    };

    $http.get("/get/default_fields")
        .then(function(resp){
            $scope.default_fields = resp.data;
        });

    String.prototype.toProperCase = function () {
        return this.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
    };
});