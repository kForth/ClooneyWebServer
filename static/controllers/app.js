var app = angular.module('app', ['ngRoute', 'ui.bootstrap', 'ngCookies', 'angular-md5', 'ui.sortable', 'chart.js'])
    .config(function ($routeProvider, $locationProvider) {
        $locationProvider.html5Mode(false).hashPrefix('');
        $routeProvider
            .when('/', {
                templateUrl: '../../../static/views/pages/home.html',
                controller: 'HomeController'
            })
            .when('/a', {
                templateUrl: '../../../static/views/pages/averages.html',
                controller: 'AveragesController'
            })
            .when('/i', {
                templateUrl: '../../../static/views/pages/insights.html',
                controller: 'InsightsController'
            })
            .when('/m', {
                templateUrl: '../../../static/views/pages/matches.html',
                controller: 'MatchesController'
            })
            .when('/e', {
                templateUrl: '../../../static/views/pages/entries.html',
                controller: 'EntriesController'
            })
            .when('/s/c', {
                templateUrl: '../../../static/views/pages/config/edit_calculations.html',
                controller: 'ConfigController'
            })
            .otherwise({
                redirectTo: '/'
            });
    });

app.controller('ApplicationController', function ($scope, $cookies) {
    if($cookies.get('tracked_event') != undefined){
        $scope.tracked_event = $cookies.get('tracked_event');
    }
});

app.controller('SidebarController', function ($scope, $cookies, $location) {
    if($cookies.get('tracked_team') != undefined){
        $scope.tracked_team = $cookies.get('tracked_team');
    }
    if($cookies.get('tracked_event') != undefined){
        $scope.event_name = $cookies.get('tracked_event');
    }
    $scope.nav = function(path){
        $location.path(path);
        $cookies.put('tracked_team', $scope.tracked_team);
    }
});

app.controller('HomeController', function ($scope, $location, $cookies) {
    $scope.selected_event = "";
    $scope.events = [{'key': '2017onwa', 'name': 'Waterloo'}, {'key': '2017onham', 'name': 'McMaster'}, {'key': '2017obar', 'name': 'Georgian'}]

    if($cookies.get('tracked_event') != undefined){
        $scope.selected_event = $cookies.get('tracked_event').name;
    }

    $scope.select_event = function(){
        if($scope.selected_event == "") return;
        console.log($scope.selected_event);
        $scope.events.forEach(function(elem){
            if(elem.name === $scope.selected_event){
                $cookies.put('tracked_event', elem.key);
                $scope.tracked_event = elem.key;
                $location.path("/a");
            }
        });
    };
});

app.controller('AveragesController', function ($scope) {

});

app.controller('InsightsController', function ($scope) {

});

app.controller('MatchesController', function ($scope) {

});

app.controller('EntriesController', function ($scope) {

});

app.controller('EditCalculationsController', function ($scope) {
    $scope.calculations = [
        {'name': 'a', 'key': 'a', 'formula':'x*x', 'type': 'float'},
        {'name': 'b', 'key': 'b', 'formula':'x+y', 'type': 'float'},
        {'name': 'c', 'key': 'c', 'formula':'x+y*x-y/x/x', 'type': 'float'},
        {'name': 'd', 'key': 'd', 'formula':'x+2', 'type': 'float'}
    ];
});

app.controller('ConfigController', function ($scope) {

});