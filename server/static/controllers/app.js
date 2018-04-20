String.prototype.toProperCase = function () {
    return this.replace(/\w\S*/g, function (txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
};

String.prototype.replaceAll = function (search, replacement) {
    var target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
};

var app = angular.module('app', ['ngRoute', 'ui.bootstrap', 'ngCookies', 'angular-md5', 'chart.js', 'ngStorage'])
    .config(function ($routeProvider, $locationProvider) {
        $locationProvider.html5Mode(false).hashPrefix('');
        $routeProvider
            .when('/event', {
                templateUrl: '../../../static/views/analysis/home.html',
                controller: 'HomeController'
            })
            .when('/matches', {
                templateUrl: '../../../static/views/analysis/table.html',
                controller: 'MatchesController'
            })
            .when('/matches/:level/:team_number', {
                templateUrl: '../../../static/views/analysis/table.html',
                controller: 'MatchesController'
            })
            .when('/matches/:level', {
                templateUrl: '../../../static/views/analysis/table.html',
                controller: 'MatchesController'
            })
            .when('/match/:key', {
                templateUrl: '../../../static/views/analysis/match.html',
                controller: 'MatchPreviewController'
            })
            .when('/teams', {
                templateUrl: '../../../static/views/analysis/table.html',
                controller: 'TeamsController'
            })
            .when('/team/:team_number', {
                templateUrl: '../../../static/views/analysis/team.html',
                controller: 'SingleTeamController'
            })
            .when('/stats', {
                templateUrl: '../../../static/views/analysis/table.html',
                controller: 'StatsController'
            })
            .when('/raw', {
                templateUrl: '../../../static/views/analysis/table.html',
                controller: 'RawController'
            })
            .when('/oprs', {
                templateUrl: '../../../static/views/analysis/table.html',
                controller: 'OprsController'
            })
            .when('/event_oprs', {
                templateUrl: '../../../static/views/analysis/table.html',
                controller: 'EventOprsController'
            })
            .when('/login', {
                templateUrl: '../../../static/views/account/login.html',
                controller: 'LoginController'
            })
            .when('/logout', {
                templateUrl: '../../../static/views/account/login.html',
                controller: 'LogoutController'
            })
            .when('/', {redirectTo: '/event'})
            // .when('/', {
            //     templateUrl: '../../../static/views/home.html',
            //     controller: 'MainViewController'
            // })
            .otherwise({redirectTo: '/event'});
    })
    .constant('AUTH_EVENTS', {
        loginSuccess: 'auth-login-success',
        loginFailed: 'auth-login-failed',
        logoutSuccess: 'auth-logout-success',
        sessionTimeout: 'auth-session-timeout',
        notAuthenticated: 'auth-not-authenticated',
        notAuthorized: 'auth-not-authorized'
    })
    .constant('USER_ROLES', {
        all: '*',
        admin: 'admin',
        user: 'user',
        guest: 'guest'
    })

    .controller('MainViewController', function () {

    })


    .controller('ApplicationController', function ($location, $scope, $cookies, USER_ROLES, AuthService) {
        $scope.event = {
            name: $cookies.get('selected-event-name'),
            key: $cookies.get('selected-event-id')
        };

        $scope.currentUser = null;
        $scope.userRoles = USER_ROLES;
        $scope.isAuthorized = AuthService.isAuthorized;

        $scope.setCurrentUser = function (user) {
            $scope.currentUser = user;
        };
    })
    .factory('EventDataService', function ($http, $sessionStorage, $localStorage, $q, $route) {

        function getCurrentDateString() {
            return new Date().toISOString();
        }

        function getCachedData(key) {
            var event_key = service.getSelectedEventKey();
            return $localStorage[key][event_key];
        }

        function getDataIfModified(url, key) {
            var event_key = service.getSelectedEventKey();
            var name = key.replaceAll("_", " ").toProperCase();
            var headers = {};
            if ($localStorage[key][event_key] !== undefined) {
                headers = {'If-Modified-Since': $localStorage.last_modified[key][event_key]};
            }
            return $http.get(url, {
                headers: headers
            })
                .then(
                    function (response) {
                        console.info("Got New " + name);
                        $localStorage[key][event_key] = response.data;
                        $localStorage.last_modified[key][event_key] = getCurrentDateString();
                        return $localStorage[key][event_key];
                    },
                    function (response) {
                        if (response.status === 304) {
                            // console.info(name + " Not Modified");
                        }
                        else {
                            console.error("Weird " + name + " Response", response);
                        }
                        return $localStorage[key][event_key];
                    });
        }

        var service = {};

        service.clearStorage = function () {
            $sessionStorage.avg = undefined;
            $sessionStorage.avg_headers = undefined;
            $sessionStorage.avg_best = undefined;
            $sessionStorage.sa_avg = undefined;
            $sessionStorage.match_headers = undefined;
            $sessionStorage.matches = undefined;
            $sessionStorage.opr_headers = undefined;
            $sessionStorage.oprs = undefined;
            $sessionStorage.event_oprs = undefined;
            $sessionStorage.raw_headers = undefined;
            $sessionStorage.raw = undefined;
            $sessionStorage.teams_headers = undefined;
            $sessionStorage.teams = undefined;
            $sessionStorage.events = undefined;
            $sessionStorage.match_single_team_data_headers = undefined;
            $sessionStorage.single_team_data_headers = undefined;
            $sessionStorage.single_team_data_info_headers = undefined;
            $sessionStorage.single_team_info_headers = undefined;
            $sessionStorage.team_info = {};
            $sessionStorage.team_stats_avg = {};
            $sessionStorage.team_raw_data = {};
            $sessionStorage.team_images = {};
        };

        service.init = function () {
            var cache_vars = [
                "last_modified",
                "event_opr",
                "best_opr",
                "event_stats",
                "event_raw",
                "event_teams",
                "event_matches",
                "team_info",
                "event_list"
            ];
            cache_vars.forEach(function (elem) {
                if (!($localStorage[elem] instanceof Object) || $localStorage[elem] === undefined) {
                    $localStorage[elem] = {};
                }
            });
            cache_vars.forEach(function (elem) {
                if (!($localStorage.last_modified[elem] instanceof Object) || $localStorage.last_modified[elem] === undefined) {
                    $localStorage.last_modified[elem] = {};
                }
            });
            $localStorage.last_modified.event_list = getCurrentDateString();
            service.updateEventList();

        };

        service.selectEvent = function (event) {
            $sessionStorage.selected_event = event;
            $http.get('/api/event/' + event.id + '/team_images')
                .then(function (response) {
                    $sessionStorage.team_images = response.data;
                });
        };

        service.getSelectedEventKey = function () {
            if ($sessionStorage.selected_event === undefined) return undefined;
            return $sessionStorage.selected_event.id;
        };

        service.getSelectedEvent = function () {
            return $sessionStorage.selected_event;
        };

        service.getEventData = function () {

        };

        service.updateEventList = function () {
            var headers = {};
            if ($localStorage.event_list !== undefined) {
                headers = {'If-Modified-Since': $localStorage.last_modified.event_list};
            }
            return $http.get('/api/events', {headers: headers})
                .then(
                    function (response) {
                        console.info("Got New Event List");
                        $localStorage.event_list = response.data;
                        $localStorage.last_modified.event_list = getCurrentDateString();
                        return $localStorage.event_list;
                    },
                    function (response) {
                        if (response.status === 304) {
                            // console.info("Event List Not Modified");
                        }
                        else {
                            console.error("Weird Event List Response", response);
                        }
                        return $localStorage.event_list;
                    });
        };

        service.getEventList = function (cached_callback) {
            if (cached_callback !== undefined) {
                cached_callback($localStorage.event_list);
            }
            return $q(service.updateEventList);
        };

        service.getEventStats = function (cached_callback) {
            var event_key = service.getSelectedEventKey();
            if (cached_callback !== undefined) {
                cached_callback(getCachedData("event_stats"));
            }
            return getDataIfModified('/api/event/' + event_key + '/stats/avg', "event_stats");
        };

        service.getEventRaw = function (cached_callback) {
            var event_key = service.getSelectedEventKey();
            if (cached_callback !== undefined) {
                cached_callback(getCachedData("event_raw"));
            }
            return getDataIfModified('/api/event/' + event_key + '/stats/raw', "event_raw");
        };

        service.getEventOprs = function (cached_callback) {
            var event_key = service.getSelectedEventKey();
            if (cached_callback !== undefined) {
                cached_callback(getCachedData("event_opr"));
            }
            return getDataIfModified('/api/event/' + event_key + '/event_oprs', "event_opr");
        };

        service.getBestOprs = function (cached_callback) {
            var event_key = service.getSelectedEventKey();
            if (cached_callback !== undefined) {
                cached_callback(getCachedData("best_opr"));
            }
            return getDataIfModified('/api/event/' + event_key + '/oprs', "best_opr");
        };

        service.getEventTeams = function (cached_callback) {
            var event_key = service.getSelectedEventKey();
            if (cached_callback !== undefined) {
                cached_callback(getCachedData("event_teams"));
            }
            return getDataIfModified('/api/event/' + event_key + '/teams', "event_teams");
        };

        service.getEventMatches = function (cached_callback) {
            var event_key = service.getSelectedEventKey();
            if (cached_callback !== undefined) {
                cached_callback(getCachedData("event_matches"));
            }
            return getDataIfModified('/api/event/' + event_key + '/matches', "event_matches");
        };

        service.getTeamRaw = function (team_number, cached_callback) {
            if (cached_callback !== undefined) {
                var team_data = [];
                getCachedData("event_raw").forEach(function (elem) {
                    if (elem.team_number == team_number) {
                        team_data.push(elem);
                    }
                });
                cached_callback(team_data);
            }
            return service.getEventRaw()
                .then(function (data) {
                    var team_data = [];
                    data.forEach(function (elem) {
                        if (elem.team_number == team_number) {
                            team_data.push(elem);
                        }
                    });
                    return team_data;
                });
        };

        service.getTeamStats = function (team_number, cached_callback) {
            if (cached_callback !== undefined) {
                var team_data = [];
                getCachedData("event_stats").forEach(function (elem) {
                    if (elem.team_number == team_number) {
                        team_data.push(elem);
                    }
                });
                cached_callback(team_data);
            }
            return service.getEventStats()
                .then(function (data) {
                    var output = {};
                    data.forEach(function (elem) {
                        if (elem.team_number.value == team_number) {
                            output = elem;
                        }
                    });
                    return output;
                });
        };

        service.getTeamInfo = function (team_number, cached_callback) {
            if (cached_callback !== undefined) {
                cached_callback($localStorage.team_info[team_number]);
            }
            return $http.get('/api/event/' + service.getSelectedEventKey() + '/team/' + team_number, {
                headers: {'If-Modified-Since': $localStorage.last_modified.team_info[team_number]}
            }).then(
                function (response) {
                    console.info("Got New Team Info (" + team_number + ")");
                    $localStorage.team_info[team_number] = response.data;
                    $localStorage.last_modified.team_info[team_number] = getCurrentDateString();
                    return $localStorage.team_info[team_number];
                },
                function (response) {
                    if (response.status === 304) {
                        // console.info(name + "Team Info (" + team_number + ") Not Modified");
                    }
                    else {
                        console.error("Weird Team Info (" + team_number + ") Response", response);
                    }
                    return $localStorage.team_info[team_number];
                });
        };

        service.init();
        service.clearStorage();
        return service;
    })
    .factory('AuthService', function ($http, Session, md5, $sessionStorage) {
        var authService = {};
        authService.login = function (credentials) {
            var user_pass = {
                username: credentials.username,
                password: md5.createHash(credentials.password)
            };
            return $http
                .post('/user/login', user_pass)
                .then(function (res) {
                    return true;
                })
                .then(function (res) {
                    return false;
                });
        };

        authService.isAuthorized = function (minUserLevel) {
            return {
                'allowed': $sessionStorage.user_info['user-level'] >= minUserLevel,
                'level': $sessionStorage.user_info['user-level']
            };
        };

        return authService;
    })
    .service('Session', function () {
        this.create = function (sessionId, userId, userRole) {
            this.id = sessionId;
            this.userId = userId;
            this.userRole = userRole;
        };
        this.destroy = function () {
            this.id = null;
            this.userId = null;
            this.userRole = null;
        };
    })
    .controller("LoginController", function ($rootScope, $scope, $cookies, $location, AUTH_EVENTS, AuthService) {
        $scope.credentials = {
            username: '',
            password: ''
        };
        $scope.errors = false;
        $scope.login = function (credentials) {
            AuthService.login(credentials).then(function (user) {
                $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
                $scope.setCurrentUser(user);
                $location.path('/');
            }, function () {
                $scope.errors = true;
                $rootScope.$broadcast(AUTH_EVENTS.loginFailed);
            });
        };
    });


app.directive('fixedTableHeaders', ['$timeout', function ($timeout) {
    return {
        restrict: 'A',
        link: function (scope, element, attrs) {
            $timeout(function () {
                var container = element.parentsUntil(attrs.fixedTableHeaders);
                element.stickyTableHeaders({scrollableArea: container, "fixedOffset": 2});
            }, 0);
        }
    }
}]);

