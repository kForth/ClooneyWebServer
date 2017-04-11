var app = angular.module('app');

app.controller('HomeController', function ($scope, $cookies, $http) {
    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };

    $http.get('/api/event/' + $scope.event.key + '/stats/avg/best')
        .then(function (resp) {
            $scope.data = resp.data;
        })

});


app.controller("SingleAnalysisController", function ($scope, $http, $cookies) {
    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };

    $scope.target_data = [];
    $scope.data_sources = ['avg_data'];
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
                    stacked: true,
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
        var vals = [];
        var teams = [];
        for(var i in $scope.target_data) {
            var entry = $scope.target_data[i];
            var value = getData(entry, key_set);
            points.push({ val: value, team: $scope.target_data[i]["team_number"]["value"]});
            vals.push(value);
            if ($scope.source == "oprs") {
                teams.push($scope.target_data[i]["team_number"]);
            }
        }
        $scope.labels = [];
        $scope.data = [];
        $scope.series = [];
        var min = Math.min.apply(null, vals);
        var max = Math.max.apply(null, vals);
        var delta = (max - min) / (num_bins);
        var bins = {};
        for (var i = 0; i < num_bins; i++) {
            var min_val = (i * delta + min);
            var max_val = (min_val + delta);
            $scope.labels.push(Number(min_val.toPrecision(2)) + " - " + Number(max_val.toPrecision(2)));
            bins[i] = 0;
        }
        for (var i in points) {
            // var bin_clone = angular.copy(bins);
            var val = points[i].val * 1.0;
            var bin_num = Math.floor((val - min) / delta);
            if (val >= max) bin_num = num_bins - 1;
            if (val <= min) bin_num = 0;
            bins[bin_num] += 1;
            // bin_clone[bin_num] = 1;
            // $scope.series.push(points[i].team);
            // $scope.data.push(Object.values(bin_clone));
            $scope.data.push(Object.values(bins));
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

    $http.get('/api/event/' + $cookies.get('selected-event-id') + '/avg', {cache: true})
        .then(function (response) {
            $scope.avg_data = response.data;
        });


});
app.controller("DoubleAnalysisController", function ($scope, $http, $cookies) {
    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };

    $scope.x_target_data = [];
    $scope.y_target_data = [];
    $scope.data_sources = ['avg_data'];
    $scope.keys = {};
    $scope.labels = [];
    $scope.series = [];
    $scope.options = {
        scales: {
            xAxes: [
                {
                    type: 'linear',
                    display: true,
                    position: 'bottom'
                }
            ],
            yAxes: [
                {
                    type: 'linear',
                    display: true,
                    position: 'left'
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
        }
        $scope.data = points;
    };

    $scope.loadXKeys = function () {
        if ($scope.x_source === undefined) return;
        $cookies.put('data-x-source', $scope.x_source);
        $scope.x_primary_keys = [];
        $scope.x_secondary_keys = {};
        if ($scope.x_source === "avg_data")
            console.log($scope.avg_data);
            $scope.x_target_data = $scope.avg_data.sort(function (a, b) {
                var keyA = a["team_number"]["value"];
                var keyB = b["team_number"]["value"];
                if (keyA < keyB) return -1;
                if (keyA > keyB) return 1;
                return 0;
            });
        // if ($scope.x_source === "oprs")
        //     $scope.x_target_data = $scope.opr_data.sort(function (a, b) {
        //         var keyA = a["team_number"];
        //         var keyB = b["team_number"];
        //         if (keyA < keyB) return -1;
        //         if (keyA > keyB) return 1;
        //         return 0;
        //     });
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
            $scope.y_target_data = $scope.avg_data;
        // if ($scope.y_source === "oprs")
        //     $scope.y_target_data = $scope.opr_data.sort(function (a, b) {
        //         var keyA = a["team_number"];
        //         var keyB = b["team_number"];
        //         if (keyA < keyB) return -1;
        //         if (keyA > keyB) return 1;
        //         return 0;
        //     });
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

    var data_read = 0;

    function updateKeys() {
        if (++data_read >= 2) {
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
        }
    }

    $http.get('/api/event/' + $cookies.get('selected-event-id') + '/avg', {cache: true})
        .then(function (response) {
            $scope.avg_data = response.data;
            // console.log(response.data);
            updateKeys();
        });
    // $http.get('/api/event/' + $cookies.get('selected-event-id') + '/oprs', {cache: true})
    //     .then(function (response) {
    //         $scope.opr_data = angular.copy(response.data);
    //         console.log(response.data);
    //         updateKeys();
    //     })


});

app.controller('MatchesController', function ($scope, $cookies, $http, $sce, $location, $routeParams) {
    var httpSuffix = "";
    if ($routeParams.level != undefined) {
        if ($routeParams.level != undefined) {
            httpSuffix = "/" + $routeParams.level;
            if ($routeParams.team_number != undefined) {
                httpSuffix += "/" + $routeParams.team_number;
            }
        }
    }

    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };

    $http.get("/api/headers/" + $scope.event.key + "/matches", {cache: true})
        .then(function (response) {
            $scope.headers = angular.copy(response.data);
        });

    $http.get('/api/event/' + $scope.event.key + '/matches' + httpSuffix, {cache: true})
        .then(function (response) {
            if (response.data.length < 1) {
                angular.element(document.querySelector("#table"))[0].innerHTML = "No matches found.";
            }
            $scope.data = angular.copy(response.data);
        });

});

app.controller('OprsController', function ($scope, $cookies, $http) {
    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };

    $http.get("/api/headers/" + $scope.event.key + "/oprs", {cache: true})
        .then(function (response) {
            $scope.headers = response.data;
        });

    $http.get('/api/event/' + $cookies.get('selected-event-id') + '/oprs', {cache: true})
        .then(function (response) {
            $scope.data = response.data;
            if (response.data.length < 1) {
                angular.element(document.querySelector("#table"))[0].innerHTML = "No OPRs found."
            }
        });
});

app.controller('RawController', function ($scope, $cookies, $http, $sce) {
    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };

    $http.get("/api/headers/" + $scope.event.key + "/stats_raw", {cache: true})
        .then(function (response) {
            $scope.headers = response.data;
        });

    $http.get('/api/event/' + $cookies.get('selected-event-id') + '/stats/raw', {cache: true})
        .then(function (response) {
            $scope.data = response.data;
            if (response.data.length < 1) {
                angular.element(document.querySelector("#table"))[0].innerHTML = "No data available."
            }
        });

});

app.controller('TeamsController', function ($scope, $cookies, $http) {
    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };

    $http.get("/api/headers/" + $scope.event.key + "/teams", {cache: true})
        .then(function (response) {
            $scope.headers = response.data;
        });

    $http.get('/api/event/' + $cookies.get('selected-event-id') + '/teams', {cache: true})
        .then(function (response) {
            $scope.data = response.data;
            if (response.data.length < 1) {
                angular.element(document.querySelector("#table"))[0].innerHTML = "No teams registered.";
            }
        });

});

app.controller('StatsController', function ($scope, $cookies, $http) {
    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };

    $http.get("/api/headers/" + $scope.event.key + "/stats_avg", {cache: true})
        .then(function (response) {
            $scope.headers = response.data;
        });

    $http.get('/api/event/' + $cookies.get('selected-event-id') + '/stats/avg', {cache: true})
        .then(function (response) {
            $scope.data = response.data;
            if (response.data.length < 1) {
                angular.element(document.querySelector("#table"))[0].innerHTML = "No stats available."
            }
        });

});

app.directive('highlightTable', function ($location, $cookies) {
    function link(scope) {
        // var cookie_prefix = $location.$$path.replace("/", "");
        try{
            scope.colours = JSON.parse($cookies.get("highlighted-rows"));
        }
        catch(ex){}
        if(scope.colours === undefined)
            scope.colours = {};

        scope.cycleColour = function(index){
            if(scope.colours[index] === undefined)
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
        try{
            scope.sorts = JSON.parse($cookies.get(cookie_prefix + '-table-sort'));
        }
        catch(ex){}

        if(scope.sorts === undefined)
            scope.sorts = [];

        scope.sortData = function (event, key) {
            if(event.shiftKey){
                scope.sorts = [];
                // if(scope.sorts.indexOf("-" + key) > -1)
                //     scope.sorts.splice(scope.sorts.indexOf("-" + key), 1);
                // if(scope.sorts.indexOf(key) > -1)
                //     scope.sorts.splice(scope.sorts.indexOf(key), 1);
            }
            if(scope.sorts.indexOf("-" + key) > -1){
                var index = scope.sorts.indexOf("-" + key);
                // scope.sorts.splice(index, 1);
                scope.sorts[index] = key;
            }
            else if(scope.sorts.indexOf(key) > -1){
                var index = scope.sorts.indexOf(key);
                scope.sorts.splice(index, 1);
                // scope.sorts[index] = "-" + key;
            }
            else{
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