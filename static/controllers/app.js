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

app.controller('ApplicationController', function ($scope, $location, $http) {
    $scope.$on('$routeChangeStart', function($event, next, current) {
        $scope.tracking_input_data.event = $scope.tracked_event;
    });

    $scope.available_events = [];
    $scope.update_available_events = function(){
        $http.get('/get/available_events').then(function(resp){
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
        if(typeof($scope.tracking_input_data.event) == 'object'){
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

app.controller('AnalysisHomeController', function ($scope) {

});

app.controller('AnalysisAveragesController', function ($scope) {

});

app.controller('AnalysisInsightsController', function ($scope) {

});

app.controller('AnalysisMatchesController', function ($scope) {

});

app.controller('AnalysisEntriesController', function ($scope) {

});

app.controller('SettingsHomeController', function ($scope) {
});

app.controller('SettingsCalculationsController', function ($scope) {
    $scope.calculations = [
        {'name': 'a', 'key': 'a', 'formula': 'x*x', 'type': 'float'},
        {'name': 'b', 'key': 'b', 'formula': 'x+y', 'type': 'float'},
        {'name': 'c', 'key': 'c', 'formula': 'x+y*x-y/x/x', 'type': 'float'},
        {'name': 'd', 'key': 'd', 'formula': 'x+2', 'type': 'float'}
    ];
});

app.controller('SetupEventController', function ($scope, $location, $http) {
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
    $scope.closeAlert = function(){$scope.alert = false};

    //Step 0 - Ask if we should use TBA
    $scope.setup_with_tba_button = function () {
        $scope.setup_step = 1;
        $scope.searchable_events = [];
        $http.get('/get/search_events').then(function(resp){
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
            .then(function(resp){
                if(resp.status === 200){
                    $scope.update_available_events();
                    $scope.tracked_event = event;
                    $scope.tracked_event_okay = true;
                    $location.path('/s');
                }
            },
            function(resp){
                if(resp.status === 409){
                    $scope.alert = { type: 'danger', msg: event.key + ' has already been setup.' };
                }
                else{
                    $scope.alert = { type: 'danger', msg: 'Some kind of error occurred with ' + event.key + '. Try again?' };
                }
            });
    };

    //Step 2 - Edit the event information
    $scope.input_data = {};
    $scope.submit_manual_data = function () {
        console.log($scope.input_data);
        if (true) {
            $location.path('/s/e');
        }
    };


});