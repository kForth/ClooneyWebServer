var app = angular.module('app', ['ngRoute', 'ui.bootstrap', 'ngCookies', 'anguFixedHeaderTable', 'chart.js']);

app.controller('AppController', function ($scope) {

});

app.controller('HomeController', function ($scope, $cookies) {
    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };
});

app.controller('StatsController', function ($scope, $cookies) {
    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };

});

app.controller('PredictionController', function ($scope, $cookies) {
    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };
});


app.controller("AnalysisController", function ($scope, $http, $cookies) {
    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };

    $scope.target_data = [];
    $scope.data_sources = ['avg_data', 'oprs'];
    $scope.keys = {};
    $scope.labels = [];
    $scope.type = "bar";
    $scope.options = {
        scales: {
            yAxes: [
                {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    ticks: {
                        min: 0
                    }
                }
            ]
        }
    };
    $scope.updateData = function () {
        if ($scope.target_data === undefined || $scope.second === undefined || $scope.secondary_keys[$scope.primary] === undefined) {
            return;
        }
        $cookies.put('data-primary', $scope.primary);
        $cookies.put('data-second', $scope.second);
        var num_bins = 10;
        var key_set = $scope.primary + "," + $scope.second;
        var points = [];
        for (var i in $scope.target_data) {
            var entry = $scope.target_data[i];
            var value = getData(entry, key_set);
            points.push(value);
        }
        var min = Math.min.apply(null, points);
        var max = Math.max.apply(null, points);
        var delta = (max - min) / (num_bins);
        var bins = {};
        $scope.labels = [];
        for (var i = 0; i < num_bins; i++) {
            var min_time = (i * delta + min);
            var max_time = (min_time + delta);
            $scope.labels.push(Number(min_time.toPrecision(2)) + " - " + Number(max_time.toPrecision(2)));
            bins[i] = 0.0;
        }
        for (var i in points) {
            var val = points[i] * 1.0;
            var bin_num = Math.floor((val - min) / delta);
            if (val >= max) bin_num = num_bins - 1;
            if (val <= min) bin_num = 0;
            bins[bin_num] += 1;
        }
        $scope.data = [Object.values(bins)];
    };

    $scope.loadKeys = function () {
        if ($scope.source === undefined) return;
        $cookies.put('data-source', $scope.source);
        $scope.primary_keys = [];
        $scope.secondary_keys = {};
        if ($scope.source === "avg_data")
            $scope.target_data = $scope.avg_data;
        if ($scope.source === "oprs")
            $scope.target_data = $scope.opr_data;
        for (var key in $scope.target_data[0]) {
            if ($scope.target_data[0][key] instanceof Object) {
                $scope.primary_keys.push(key);
                $scope.secondary_keys[key] = Object.keys($scope.target_data[0][key]);
            }
        }
    };

    function getData(elem, key) {
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
    }

    $http.get('/api/event/' + $cookies.get('selected-event-id') + '/stats/avg')
        .then(function (response) {
            $scope.avg_data = angular.copy(response.data);
        });
    $http.get('/api/event/' + $cookies.get('selected-event-id') + '/oprs')
        .then(function (response) {
            $scope.opr_data = angular.copy(response.data);
        })
        .then(function (resp){
            $scope.source = $cookies.get('data-source');
            console.log($scope.source);
            if($scope.source != undefined){
                $scope.loadKeys();
                $scope.primary = $cookies.get('data-primary');
                $scope.second = $cookies.get('data-second');
                if($scope.primary != undefined && $scope.second != undefined) $scope.updateData();
            }
        });


});

app.config(function ($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: '../../../../static/views/analysis/home.html',
            controller: 'HomeController'
        })
        .when('/m', {
            templateUrl: '../../../../static/views/analysis/table.html',
            controller: 'MatchesController'
        })
        .when('/m/:level', {
            templateUrl: '../../../../static/views/analysis/table.html',
            controller: 'MatchesController'
        })
        .when('/t', {
            templateUrl: '../../../../static/views/analysis/table.html',
            controller: 'TeamsController'
        })
        .when('/s', {
            templateUrl: '../../../../static/views/analysis/table.html',
            controller: 'StatsController'
        })
        .when('/r', {
            templateUrl: '../../../../static/views/analysis/table.html',
            controller: 'RawController'
        })
        .when('/p', {
            templateUrl: '../../../../static/views/analysis/table.html',
            controller: 'PredictionController'
        })
        .when('/o', {
            templateUrl: '../../../../static/views/analysis/table.html',
            controller: 'OprsController'
        })
        .when('/a', {
            templateUrl: '../../../../static/views/analysis/graphs.html',
            controller: 'HomeController'
        })
        .otherwise({redirectTo: '/'});
});