var app = angular.module('app');

app.controller('HomeController', function ($scope, $cookies, $http, $sessionStorage, EventDataService) {
    $scope.event = EventDataService.getSelectedEvent();

    if ($scope.event !== undefined && $sessionStorage.avg_best_headers === undefined) {
        $http.get("/api/headers/" + $scope.event.id + "/avg_best", {cache: true})
            .then(function (response) {
                $scope.headers = response.data;
                $sessionStorage.avg_best_headers = response.data;
            });
    }
    else {
        $scope.headers = $sessionStorage.avg_best_headers;
    }

    EventDataService.getEventStats(
        function(data){
            $scope.data = data;
        })
        .then(function(data){
            $scope.data = data;
            $scope.data_loaded = true;
        });

});

app.controller('MatchesController', function ($scope, $cookies, $http, $sce, $location, $routeParams, $sessionStorage, EventDataService) {
    var httpSuffix = "";
    if ($routeParams.level != undefined) {
        if ($routeParams.level != undefined) {
            httpSuffix = "/" + $routeParams.level;
            if ($routeParams.team_number != undefined) {
                httpSuffix += "/" + $routeParams.team_number;
            }
        }
    }

    $scope.event = EventDataService.getSelectedEvent();

    if ($sessionStorage.match_headers == undefined && $scope.event !== undefined) {
        $http.get("/api/headers/" + $scope.event.id + "/matches", {cache: true})
            .then(function (response) {
                $scope.headers = response.data;
                $sessionStorage.match_headers = response.data;
            });
    }
    else {
        $scope.headers = $sessionStorage.match_headers;
    }

    if ($sessionStorage.matches == undefined && $scope.event !== undefined) {
        $http.get('/api/event/' + $scope.event.id + '/matches' + httpSuffix, {cache: true})
            .then(function (response) {
                if (response.data.length < 1) {
                    angular.element(document.querySelector("#table"))[0].innerHTML = "No matches found.";
                }
                else {
                    $scope.data = response.data;
                    $sessionStorage.matches = response.data;
                }
            });
    }
    else {
        $scope.data = $sessionStorage.matches;
    }
});

app.controller('OprsController', function ($scope, $cookies, $http, $sessionStorage, EventDataService) {
    $scope.event = EventDataService.getSelectedEvent();

    if ($sessionStorage.opr_headers == undefined && $scope.event !== undefined) {
        $http.get("/api/headers/" + $scope.event.id + "/oprs", {cache: true})
            .then(function (response) {
                $scope.headers = response.data;
                $sessionStorage.opr_headers = response.data;
            });
    }
    else {
        $scope.headers = $sessionStorage.opr_headers;
    }

    EventDataService.getBestOprs(
        function(data){
            $scope.data = data;
        })
        .then(function(data){
            $scope.data = data;
            $scope.data_loaded = true;
        });
});

app.controller('EventOprsController', function ($scope, $cookies, $http, $sessionStorage, EventDataService) {
    $scope.event = EventDataService.getSelectedEvent();

    if ($sessionStorage.opr_headers == undefined && $scope.event !== undefined) {
        $http.get("/api/headers/" + $scope.event.id + "/oprs", {cache: true})
            .then(function (response) {
                $scope.headers = response.data;
                $sessionStorage.opr_headers = response.data;
            });
    }
    else {
        $scope.headers = $sessionStorage.opr_headers;
    }

    EventDataService.getEventOprs(
        function(data){
            $scope.data = data;
        })
        .then(function(data){
            $scope.data = data;
            $scope.data_loaded = true;
        });
});

app.controller('RawController', function ($scope, $cookies, $http, $sessionStorage, EventDataService) {
    $scope.event = EventDataService.getSelectedEvent();

    if ($sessionStorage.raw_headers == undefined && $scope.event !== undefined) {
        $http.get("/api/headers/" + $scope.event.id + "/stats_raw", {cache: true})
            .then(function (response) {
                $scope.headers = response.data;
                $sessionStorage.raw_headers = response.data;
            });
    }
    else {
        $scope.headers = $sessionStorage.raw_headers;
    }

    EventDataService.getEventRaw(
        function(data){
            $scope.data = data;
        })
        .then(function(data){
            $scope.data = data;
            $scope.data_loaded = true;
        });

});

app.controller('TeamsController', function ($scope, $cookies, $http, $sessionStorage, EventDataService) {
    $scope.event = EventDataService.getSelectedEvent();

    if ($sessionStorage.teams_headers === undefined && $scope.event !== undefined) {
        $http.get("/api/headers/" + $scope.event.id + "/teams", {cache: true})
            .then(function (response) {
                $scope.headers = response.data;
                $sessionStorage.teams_headers = response.data;
            });
    }
    else {
        $scope.headers = $sessionStorage.teams_headers;
    }

    EventDataService.getEventTeams(
        function(data){
            $scope.data = data;
        })
        .then(function(data){
            $scope.data = data;
            $scope.data_loaded = true;
        });

});

app.controller('StatsController', function ($scope, $cookies, $http, $sessionStorage, EventDataService, $localStorage) {
    $scope.event = EventDataService.getSelectedEvent();

    if ($sessionStorage.avg_headers === undefined && $scope.event !== undefined) {
        $http.get("/api/headers/" + $scope.event.id + "/stats_avg", {cache: true})
            .then(function (response) {
                $scope.headers = response.data;
                $sessionStorage.avg_headers = response.data;
            });
    }
    else {
        $scope.headers = $sessionStorage.avg_headers;
    }

    EventDataService.getEventStats(
        function(data){
            $scope.data = data;
        })
        .then(function(data){
            $scope.data = data;
            $scope.data_loaded = true;
        });

});

app.directive('highlightTable', function ($location, $cookies) {
    function link(scope) {
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


app.directive('multiSortTable', function ($location, $cookies, $sce, $sessionStorage, EventDataService) {

    function link(scope) {
        var cookie_prefix = $location.$$path.replace("/", "");
        try {
            scope.sorts = JSON.parse($cookies.get(cookie_prefix + '-table-sort'));
        }
        catch (ex) {
        }

        if (scope.sorts === undefined)
            scope.sorts = [];

        scope.getData = function (elem, key) {
            if (elem === undefined || key === undefined){
                return "";
            }
            if (key.includes(",") || key.includes(".")) {
                key.replaceAll(".", ",");
                var keys = key.split(",");
                var val = elem;
                keys.forEach(function (k) {
                    if (val === undefined) {
                        val = "";
                    }
                    else {
                        val = val[k.trim()];
                    }
                });
                return val;
            }
            else {
                return elem[key];
            }
        };

        scope.sortData = function (event, key) {
            if (event.shiftKey) {
                scope.sorts = [];
            }
            var index;
            if (scope.sorts.indexOf("-" + key) > -1) {
                index = scope.sorts.indexOf("-" + key);
                scope.sorts[index] = key;
            }
            else if (scope.sorts.indexOf(key) > -1) {
                index = scope.sorts.indexOf(key);
                scope.sorts.splice(index, 1);
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

app.controller('SingleTeamController', function ($scope, $http, $location, $cookies, $sessionStorage, EventDataService) {
    $scope.team_number = parseInt($location.url().split("/")[2]);
    $scope.event = EventDataService.getSelectedEvent();

    $scope.team_info = {};
    $scope.avg_data = {};
    $scope.raw_data = [];
    $scope.images = [];

    $scope.interval = 5000;
    $scope.noWrapSlides = false;
    $scope.active = 0;

    $http.get("/api/event/" + $scope.event.id + "/team/" + $scope.team_number + "/images")
        .then(function (response) {
            var i = 0;
            response.data.forEach(function (elem) {
                $scope.images.push({
                    image: "../../../static/robot_pics/" + $scope.team_number + "/" + elem,
                    id: i++
                });
            });
        });

    EventDataService.getTeamInfo($scope.team_number,
        function(data){
            $scope.team_info = data;
        })
        .then(function(data){
            $scope.team_info = data;
        });

    EventDataService.getTeamStats($scope.team_number,
        function(data){
            $scope.avg_data = data;
        })
        .then(function(data){
            $scope.avg_data = data;
        });

    EventDataService.getTeamRaw($scope.team_number,
        function(data){
            $scope.raw_data = data;
        })
        .then(function(data){
            $scope.raw_data = data;
        });

    if ($sessionStorage.single_team_info_headers == undefined && $scope.event !== undefined) {
        $http.get("/api/headers/" + $scope.event.id + "/single_team_info", {cache: true})
            .then(function (response) {
                $scope.team_info_headers = response.data;
                $sessionStorage.single_team_info_headers = response.data;
            });
    }
    else {
        $scope.team_info_headers = $sessionStorage.single_team_info_headers;
    }

    if ($sessionStorage.single_team_data_info_headers == undefined && $scope.event !== undefined) {
        $http.get("/api/headers/" + $scope.event.id + "/single_team_data_info", {cache: true})
            .then(function (response) {
                $scope.data_info_headers = response.data;
                $sessionStorage.single_team_data_info_headers = response.data;
            });
    }
    else {
        $scope.data_info_headers = $sessionStorage.single_team_data_info_headers;
    }

    if ($sessionStorage.single_team_data_headers == undefined && $scope.event !== undefined) {
        $http.get("/api/headers/" + $scope.event.id + "/single_team_data", {cache: true})
            .then(function (response) {
                $scope.data_headers = response.data;
                $sessionStorage.single_team_data_headers = response.data;
            });
    }
    else {
        $scope.data_headers = $sessionStorage.single_team_data_headers;
    }

    $scope.getData = function (elem, key) {
        if (elem === undefined || key === undefined) {
            return "";
        }
        if (key.includes(",") || key.includes(".")) {
            key = key.replaceAll(".", ",");
            var keys = key.split(",");
            var val = elem;
            keys.forEach(function (k) {
                if (val === undefined) {
                    val = "";
                }
                else {
                    val = val[k.trim()];
                }
            });
            return val;
        }
        else {
            return elem[key];
        }
    };

});

app.controller('MatchPreviewController', function ($scope, $http, $sessionStorage, $location, $cookies, EventDataService) {
    $scope.match_key = $location.url().split("/")[2];
    $scope.event = EventDataService.getSelectedEvent();

    $http.get('/api/event/' + $scope.event.id + '/match/' + $scope.match_key)
        .then(function (response) {
            $scope.match_info = response.data;
            $scope.alliance_data = {
                'red': [],
                'blue': []
            };
            ['red', 'blue'].forEach(function (alliance) {
                $scope.match_info['alliances'][alliance]['team_keys'].forEach(function (team) {
                    var team_number = ('' + team).substr(3);
                    $http.get("/api/event/" + $scope.event.id + "/stats/avg/" + team_number)
                        .then(function (response) {
                            $scope.alliance_data[alliance].push(response.data);
                        });
                });
            });
        });

    if ($sessionStorage.match_single_team_data_headers == undefined && $scope.event !== undefined) {
        $http.get("/api/headers/" + $scope.event.id + "/match_single_team_data", {cache: true})
            .then(function (response) {
                $scope.data_headers = response.data;
                $sessionStorage.match_single_team_data_headers = $scope.data_headers;
            });
    }
    else {
        $scope.data_headers = $sessionStorage.match_single_team_data_headers;
    }

});