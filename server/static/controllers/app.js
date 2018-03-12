String.prototype.toProperCase = function () {
    return this.replace(/\w\S*/g, function (txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
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
            .when('/pred/:team_number', {
                templateUrl: '../../../static/views/analysis/table.html',
                controller: 'PredictionController'
            })
            .when('/pred', {
                templateUrl: '../../../static/views/analysis/table.html',
                controller: 'PredictionController'
            })
            .when('/analysis', {
                templateUrl: '../../../static/views/analysis/graphs.html',
                controller: 'DoubleAnalysisController'
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
                    if (res.status === 200) {
                        return true;
                    }
                    return false;
                });
        };

        authService.isAuthorized = function (minUserLevel) {
            if ($sessionStorage.user_info === undefined) {
                return $http.get('/user/check_auth').then(function (response) {
                    $sessionStorage.user_info = response.data;
                    if (response)
                        return {
                            'allowed': response.data['user-level'] >= minUserLevel,
                            'level': response.data['user-level']
                        };
                    else
                        return {
                            'allowed': false,
                            'level': 0
                        };
                });
            }
            else {
                return {
                    'allowed': $sessionStorage.user_info['user-level'] >= minUserLevel,
                    'level': $sessionStorage.user_info['user-level']
                };
            }
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

