var app = angular.module('app', ['ngRoute', 'ui.bootstrap', 'ngCookies', 'angular-md5', 'chart.js'])
    .config(function ($routeProvider, $locationProvider) {
        $locationProvider.html5Mode(false).hashPrefix('');
        $routeProvider
            .when('/', {
                templateUrl: '../../../static/views/pages/home.html',
                controller: 'MainViewController'
            })
            .otherwise({
                redirectTo: '/'
            });
    });

app.controller('ApplicationController', function () {
    console.log("App");
});

app.controller('MainViewController', function () {
    console.log("Main");
});

