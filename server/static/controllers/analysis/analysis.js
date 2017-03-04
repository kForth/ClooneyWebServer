var app = angular.module('app');

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


app.controller("SingleAnalysisController", function ($scope, $http, $cookies) {
    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };

    $scope.target_data = [];
    $scope.data_sources = ['avg_data', 'oprs'];
    $scope.keys = {};
    $scope.labels = [];
    $scope.type = "bar";
    $scope.series = ["Num Teams"];
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
        if ($scope.source === undefined || $scope.second === undefined || $scope.secondary_keys[$scope.primary] === undefined) {
            return;
        }
        $cookies.put('data-primary', $scope.primary);
        $cookies.put('data-second', $scope.second);

        var num_bins = 10;
        var key_set = $scope.primary + "," + $scope.second;
        var points = [];
        var teams = [];
        for (var i in $scope.target_data) {
            var entry = $scope.target_data[i];
            var value = getData(entry, key_set);
            points.push(value);
            if ($scope.source == "oprs") {
                teams.push($scope.target_data[i]["team_number"]);
            }
        }
        var min = Math.min.apply(null, points);
        var max = Math.max.apply(null, points);
        var delta = (max - min) / (num_bins);
        var bins = {};
        var team_groups = [];
        $scope.labels = [];
        for (var i = 0; i < num_bins; i++) {
            var min_val = (i * delta + min);
            var max_val = (min_val + delta);
            $scope.labels.push(Number(min_val.toPrecision(2)) + " - " + Number(max_val.toPrecision(2)));
            bins[i] = 0.0;
            team_groups.push([]);
        }
        for (var i in points) {
            var val = points[i] * 1.0;
            var bin_num = Math.floor((val - min) / delta);
            if (val >= max) bin_num = num_bins - 1;
            if (val <= min) bin_num = 0;
            bins[bin_num] += 1;
            team_groups[bin_num].push(teams[i]);

        }
        var team_strings = [];
        team_groups.forEach(function (elem) {
            team_strings.push(elem.join(", "));
        });
        // $scope.series = team_strings;
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
        .then(function (resp) {
            $scope.source = $cookies.get('data-source');
            if ($scope.source != undefined) {
                $scope.loadKeys();
                $scope.primary = $cookies.get('data-primary');
                $scope.second = $cookies.get('data-second');
                if ($scope.primary != undefined && $scope.second != undefined) $scope.updateData();
            }
        });


});
app.controller("DoubleAnalysisController", function ($scope, $http, $cookies) {
    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };

    $scope.x_target_data = [];
    $scope.y_target_data = [];
    $scope.data_sources = ['avg_data', 'oprs'];
    $scope.keys = {};
    $scope.labels = [];
    $scope.options = {
        scales: {
            xAxes: [
                {
                    type: 'linear',
                    display: true,
                    ticks: {
                        min: 0
                    }
                }
            ],
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
        if ($scope.x_source === undefined || $scope.x_second === undefined || $scope.x_secondary_keys[$scope.x_primary] === undefined ||
            $scope.y_source === undefined || $scope.y_second === undefined || $scope.y_secondary_keys[$scope.y_primary] === undefined) {
            return;
        }
        $cookies.put('data-x-primary', $scope.x_primary);
        $cookies.put('data-x-second', $scope.x_second);
        $cookies.put('data-y-primary', $scope.y_primary);
        $cookies.put('data-y-second', $scope.y_second);

        var x_key_set = $scope.x_primary + "," + $scope.x_second;
        var y_key_set = $scope.y_primary + "," + $scope.y_second;
        var points = [];
        var teams = [];
        for (var i = 0; i < $scope.x_target_data.length; i++) {
            var xEntry = $scope.x_target_data[i];
            var yEntry = $scope.y_target_data[i];

            var xValue = getData(xEntry, x_key_set);
            var yValue = getData(yEntry, y_key_set);
            points.push({
                x: xValue,
                y: yValue,
                r: 2
            });
            console.log(xValue - yValue);
            if ($scope.x_source == "oprs") {
                teams.push($scope.x_target_data[i]["team_number"]);
            }
        }
        $scope.data = points;
    };

    $scope.loadXKeys = function () {
        if ($scope.x_source === undefined) return;
        $cookies.put('data-x-source', $scope.x_source);
        $scope.x_primary_keys = [];
        $scope.x_secondary_keys = {};
        if ($scope.x_source === "avg_data")
            $scope.x_target_data = $scope.avg_data.sort(function (a, b) {
                var keyA = a["team_number"]["value"];
                var keyB = b["team_number"]["value"];
                if (keyA < keyB) return -1;
                if (keyA > keyB) return 1;
                return 0;
            });
        if ($scope.x_source === "oprs")
            $scope.x_target_data = $scope.opr_data.sort(function (a, b) {
                var keyA = a["team_number"];
                var keyB = b["team_number"];
                if (keyA < keyB) return -1;
                if (keyA > keyB) return 1;
                return 0;
            });
        for (var key in $scope.x_target_data[0]) {
            if ($scope.x_target_data[0][key] instanceof Object) {
                $scope.x_primary_keys.push(key);
                $scope.x_secondary_keys[key] = Object.keys($scope.x_target_data[0][key]);
            }
        }
    };

    $scope.loadYKeys = function () {
        if ($scope.y_source === undefined) return;
        $cookies.put('data-y-source', $scope.y_source);
        $scope.y_primary_keys = [];
        $scope.y_secondary_keys = {};
        if ($scope.y_source === "avg_data")
            $scope.y_target_data = $scope.avg_data.sort(function (a, b) {
                var keyA = a["team_number"]["value"];
                var keyB = b["team_number"]["value"];
                if (keyA < keyB) return -1;
                if (keyA > keyB) return 1;
                return 0;
            });
        if ($scope.y_source === "oprs")
            $scope.y_target_data = $scope.opr_data.sort(function (a, b) {
                var keyA = a["team_number"];
                var keyB = b["team_number"];
                if (keyA < keyB) return -1;
                if (keyA > keyB) return 1;
                return 0;
            });
        for (var key in $scope.y_target_data[0]) {
            if ($scope.y_target_data[0][key] instanceof Object) {
                $scope.y_primary_keys.push(key);
                $scope.y_secondary_keys[key] = Object.keys($scope.y_target_data[0][key]);
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
            $scope.avg_data = response.data;
        })
        .then($http.get('/api/event/' + $cookies.get('selected-event-id') + '/oprs')
            .then(function (response) {
                $scope.opr_data = angular.copy(response.data);
            })
            .then(function (resp) {
                $scope.x_source = $cookies.get('data-x-source');
                $scope.y_source = $cookies.get('data-y-source');
                if ($scope.x_source != undefined) {
                    $scope.loadXKeys();
                    $scope.x_primary = $cookies.get('data-x-primary');
                    $scope.x_second = $cookies.get('data-x-second');
                }
                if ($scope.y_source != undefined) {
                    $scope.loadYKeys();
                    $scope.y_primary = $cookies.get('data-y-primary');
                    $scope.y_second = $cookies.get('data-y-second');
                }
                $scope.updateData();
            }));


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