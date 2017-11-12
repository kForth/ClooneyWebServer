var app = angular.module('app', ['ngRoute', 'ngAnimate', 'ui.bootstrap', 'ngCookies', 'ui.sortable'])
    .config(function ($routeProvider, $locationProvider) {
        $locationProvider.html5Mode(false).hashPrefix('');
        $routeProvider
            .when('/', {
                templateUrl: '../../../static/views/pages/home.html',
                controller: 'HomeController'
            })
            .when('/e', {
                templateUrl: '../../../static/views/pages/event/home.html',
                controller: 'EventHomeController'
            })
            .when('/e/a', {
                templateUrl: '../../../static/views/pages/event/averages.html',
                controller: 'AveragesController'
            })
            .when('/e/i', {
                templateUrl: '../../../static/views/pages/event/insights.html',
                controller: 'InsightsController'
            })
            .when('/e/m', {
                templateUrl: '../../../static/views/pages/event/matches.html',
                controller: 'MatchesController'
            })
            .when('/e/e', {
                templateUrl: '../../../static/views/pages/event/entries.html',
                controller: 'EntriesController'
            })
            .when('/s', {
                templateUrl: '../../../static/views/pages/settings/event_settings.html',
                controller: 'EventSettingsController'
            })
            .when('/s/c', {
                templateUrl: '../../../static/views/pages/settings/edit_calculations.html',
                controller: 'EditCalculationsController'
            })
            .when('/setup/:setup_step?', {
                templateUrl: '../../../static/views/pages/settings/event_setup.html',
                controller: 'EventSetupController'
            })
            .otherwise({
                redirectTo: '/'
            });
    });

app.directive('highlightTable', function ($location, $cookies) {
    function link(scope) {
        // var cookie_prefix = $location.$$path.replace("/", "");
        try {
            scope.colours = JSON.parse($cookies.get("highlighted-rows"));
        }
        catch (ex) {
        }
        if (scope.colours === undefined)
            scope.colours = {};

        scope.cycleColour = function (index) {
            if (scope.colours[index] === undefined)
                scope.colours[index] = 0;
            scope.colours[index]++;
            $cookies.put("highlighted-rows", JSON.stringify(scope.colours));
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

app.controller('ApplicationController', function ($scope, $cookies) {
    if ($cookies.get('tracked_event') != undefined) {
        $scope.tracked_event = $cookies.get('tracked_event');
    }
});

app.controller('NavbarController', function ($scope) {
    $scope.isNavCollapsed = false;
});

app.controller('SidebarController', function ($scope, $cookies, $location) {
    if ($cookies.get('tracked_team') != undefined) {
        $scope.tracked_team = $cookies.get('tracked_team');
    }
    if ($cookies.get('tracked_event') != undefined) {
        $scope.event_name = $cookies.get('tracked_event');
    }
    $scope.nav = function (path) {
        $location.path(path);
        $cookies.put('tracked_team', $scope.tracked_team);
    }
});

app.controller('HomeController', function ($scope, $location, $cookies) {
    $scope.selected_event = "";
    $scope.events = [{'key': '2017onwa', 'name': 'Waterloo'}, {
        'key': '2017onham',
        'name': 'McMaster'
    }, {'key': '2017obar', 'name': 'Georgian'}];

    if ($cookies.get('tracked_event') != undefined) {
        $scope.selected_event = $cookies.get('tracked_event').name;
    }

    $scope.select_event = function () {
        if ($scope.selected_event == "") return;
        console.log($scope.selected_event);
        $scope.events.forEach(function (elem) {
            if (elem.name === $scope.selected_event) {
                $cookies.put('tracked_event', elem.key);
                $scope.tracked_event = elem.key;
                $location.path("/a");
            }
        });
    };
});

app.controller('EventHomeController', function ($scope) {

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
        {'name': 'a', 'key': 'a', 'formula': 'x*x', 'type': 'float'},
        {'name': 'b', 'key': 'b', 'formula': 'x+y', 'type': 'float'},
        {'name': 'c', 'key': 'c', 'formula': 'x+y*x-y/x/x', 'type': 'float'},
        {'name': 'd', 'key': 'd', 'formula': 'x+2', 'type': 'float'}
    ];
});

app.controller('EventSettingsController', function ($scope) {

});

app.controller('EventSetupController', function ($scope, $location) {
    $scope.setup_step = 0;
    $scope.events = ['2017onwa', '2017onham', '2017onbar', '2017 Waterloo District Event', '2017 McMaster District Event', '2017Georgian College District Event'];
    $scope.use_tba = false;
    $scope.default_data =
        [
            {
                "id": "key",
                "label" : "Event Key",
                "default_value": "",
                "type": "text"
            },
            {
                "id": "name",
                "label" : "Event Name",
                "default_value": "",
                "type": "text"
            },
            {
                "id": "short_name",
                "label" : "Short Name",
                "default_value": "",
                "type": "text"
            }
        ];

    //Step 0 - Ask if we should use TBA
    $scope.setup_with_tba_button = function () {
        $scope.setup_step = 1;
        $scope.use_tba = true;
    };

    $scope.setup_manually_button = function () {
        $scope.setup_step = 2;
    };

    //Step 1 - (TBA Only) Search for the event.
    $scope.event_search_input = "";
    $scope.setup_tba_event = function () {
        if ($scope.events.indexOf($scope.event_search_input) > -1) {
            console.log(Scope.event_search_input);
            //Do auto setup stuff.
        }
    };

    //Step 2 - Edit the event information (pre-filled inputs if using TBA)
    $scope.input_data = {};
    $scope.submit_manual_data = function(){
        console.log($scope.input_data);
        if(true){
            $location.path('/s/e');
        }
    };



});