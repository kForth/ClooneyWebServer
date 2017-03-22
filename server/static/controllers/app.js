var app = angular.module('app', ['ngRoute', 'ui.bootstrap', 'ngCookies', 'angular-md5'])
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
            .when('/analysis', {
                templateUrl: '../../../static/views/analysis/graphs.html',
                controller: 'HomeController'
            })
            .when('/login', {
                templateUrl: '../../../static/views/account/login.html',
                controller: 'LoginController'
            })
            .when('/', {
                templateUrl: '../../../static/views/home.html',
                controller: 'MainViewController'
            })
            .otherwise({redirectTo: '/'});
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


    .controller('ApplicationController', function ($scope, $cookies, USER_ROLES, AuthService) {
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
    .controller("LoginController", function ($rootScope, $scope, $cookies, AUTH_EVENTS, AuthService) {
        $scope.credentials = {
            username: '',
            password: ''
        };
        $scope.errors = false;
        $scope.login = function (credentials) {
            AuthService.login(credentials).then(function (user) {
                $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
                $scope.setCurrentUser(user);
            }, function () {
                $scope.errors = true;
                $rootScope.$broadcast(AUTH_EVENTS.loginFailed);
            });
        };
    })
    .factory('AuthService', function ($http, Session, md5) {
        var authService = {};
        authService.login = function (credentials) {
            var user_pass = {
                username: credentials.username,
                password: md5.createHash(credentials.password)
            };
            return $http
                .post('/login', user_pass)
                .then(function (res) {
                    if (res.status === 200) {
                        Session.create(res.data.id, res.data.user.id, res.data.user.role);
                        return res.data.user;
                    }
                    else {
                        return false;
                    }
                });
        };

        authService.isAuthenticated = function () {
            return !!Session.userId;
        };

        authService.isAuthorized = function (authorizedRoles) {
            if (!angular.isArray(authorizedRoles)) {
                authorizedRoles = [authorizedRoles];
            }
            return (authService.isAuthenticated() &&
            authorizedRoles.indexOf(Session.userRole) !== -1);
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
    .controller('SingleTeamController', function ($scope, $http, $location, $cookies) {
        $scope.team_number = parseInt($location.url().split("/")[2]);

        $scope.team_info = {};
        $scope.avg_data = {};
        $scope.raw_data = [];
        $scope.images = [];

        $scope.interval = 5000;
        $scope.noWrapSlides = false;
        $scope.active = 0;

        $http.get("/api/event/" + $scope.event.key + "/team/" + $scope.team_number + "/images")
            .then(function (response) {
                var i = 0;
                response.data.forEach(function(elem){
                    $scope.images.push({
                        image: "../../../static/robot_pics/" + $scope.event.key + "/" + $scope.team_number + "/" + elem,
                        id: i++
                    });
                });
                console.log($scope.images);
            });

        $http.get("/api/event/" + $scope.event.key + "/team/" + $scope.team_number)
            .then(function (response) {
                $scope.team_info = response.data;
            });
        $http.get("/api/event/" + $scope.event.key + "/stats/avg/" + $scope.team_number)
            .then(function (response) {
                $scope.avg_data = response.data;
            });
        $http.get("/api/event/" + $scope.event.key + "/stats/raw/" + $scope.team_number)
            .then(function (response) {
                $scope.raw_data = response.data;
                $scope.raw_data.sort(function (a, b) {
                    return b["match"] - a["match"];
                });
            });


        $http.get("/api/headers/" + $scope.event.key + "/single_team_info", {cache: true})
            .then(function (response) {
                $scope.team_info_headers = response.data;
            });
        $http.get("/api/headers/" + $scope.event.key + "/single_team_data_info", {cache: true})
            .then(function (response) {
                $scope.data_info_headers = response.data;
            });
        $http.get("/api/headers/" + $scope.event.key + "/single_team_data", {cache: true})
            .then(function (response) {
                $scope.data_headers = response.data;
                console.log($scope.data_headers)
            });

        $scope.sortId = $cookies.get('matches-sort-id');
        $scope.sortReverse = $cookies.get('matches-sort-reverse');

        $scope.sortData = function(key){
            if($scope.sortReverse === undefined){
                $scope.sortReverse = true;
            }
            if($scope.sortId === key){
                $scope.sortReverse = !$scope.sortReverse;
            }
            else{
                $scope.sortId = key;
                $scope.sortReverse = true;
            }

            $cookies.put('matches-sort-id', $scope.sortId);
            $cookies.put('matches-sort-reverse', $scope.sortReverse);
        };


        $scope.getData = function (elem, key) {
            if (elem === undefined)
                return "";
            if (key.includes(",")) {
                var keys = key.split(",");
                var val = elem;
                keys.forEach(function (key) {
                    val = val[key.trim()];
                });
                return val;
            }
            else {
                return elem[key];
            }
        };

    });
