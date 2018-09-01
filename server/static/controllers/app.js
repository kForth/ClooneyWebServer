String.prototype.toProperCase = function () {
    return this.replace(/\w\S*/g, function (txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
};

String.prototype.replaceAll = function (search, replacement) {
    var target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
};

var app = angular.module('app', ['ngRoute', 'ui.bootstrap', 'ngCookies', 'angular-md5', 'chart.js', 'ngStorage', 'infinite-scroll'])
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
                templateUrl: '../../../static/views/account/logout.html',
                controller: 'LogoutController'
            })
            .when('/account', {
                templateUrl: '../../../static/views/account/edit_account.html',
                controller: 'EditAccountController'
            })
            .when('/register', {
                templateUrl: '../../../static/views/account/register.html',
                controller: 'AddAccountController'
            })
            .when('/accounts', {
                templateUrl: '../../../static/views/account/accounts.html',
                controller: 'ManageAccountsController'
            })
            .when('/', {redirectTo: '/event'})
            // .when('/', {
            //     templateUrl: '../../../static/views/home.html',
            //     controller: 'MainViewController'
            // })
            .otherwise({redirectTo: '/event'});
    })

    .controller('MainViewController', function () {

    })


    .controller('ApplicationController', function ($location, $scope, $cookies, $sessionStorage, AuthService) {
        $scope.event = {
            name: $cookies.get('selected-event-name'),
            key: $cookies.get('selected-event-id')
        };

        AuthService.testCachedUser();

        $scope.currentUser = $sessionStorage.user;
        $scope.$watch(function() {
            return angular.toJson($sessionStorage);
        }, function() {
            $scope.currentUser = $sessionStorage.user;
        });
        $scope.logout = AuthService.logout;
    })
    .factory('EventDataService', function ($http, $sessionStorage, $localStorage, $q, $window) {
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
            if ($localStorage[key][event_key] !== undefined && $localStorage[key][event_key].length > 0) {
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
            $window.location.reload();
        };

        service.getSelectedEventKey = function () {
            if ($sessionStorage.selected_event === undefined) return undefined;
            return service.getSelectedEvent().id;
        };

        service.getSelectedEvent = function () {
            if($sessionStorage.selected_event !== undefined) {
                return $sessionStorage.selected_event;
            }
            return {
                id: '',
                name: ''
            }
        };

        service.getEventData = function () {

        };

        service.updateEventList = function () {
            var headers = {};
            if ($localStorage.event_list !== undefined &&
                $localStorage.event_list.length > 0) {
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
                var data = getCachedData("event_raw");
                if(data !== undefined){
                    data.forEach(function (elem) {
                        if (elem.team_number == team_number) {
                            team_data.push(elem);
                        }
                    });
                }
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
                var data = getCachedData("event_stats");
                if (data !== undefined) {
                    data.forEach(function (elem) {
                        if (elem.team_number == team_number) {
                            team_data.push(elem);
                        }
                    });
                }
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

