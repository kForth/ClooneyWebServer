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
        function (data) {
            $scope.data = data;
        })
        .then(function (data) {
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
        function (data) {
            $scope.data = data;
        })
        .then(function (data) {
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
        function (data) {
            $scope.data = data;
        })
        .then(function (data) {
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
        function (data) {
            $scope.data = data;
        })
        .then(function (data) {
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
        function (data) {
            $scope.data = data;
        })
        .then(function (data) {
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
        function (data) {
            $scope.data = data;
        })
        .then(function (data) {
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
            if (elem === undefined || key === undefined) {
                return "";
            }
            if (key.indexOf(",") > -1 || key.indexOf(".") > -1) {
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
            scope.updateSort();
        };

        if ($sessionStorage.use_fuzzy_sort === undefined) {
            $sessionStorage.use_fuzzy_sort = false;
        }
        if ($sessionStorage.fuzzy_sort_tolerance === undefined) {
            $sessionStorage.fuzzy_sort_tolerance = 0.2;
        }
        scope.fuzzy_sort_tolerance = 0.2;
        scope.updateSort = function () {
            if (scope.data === undefined) {
                return;
            }
            scope.data = scope.data.sort(function (a, b) {
                for (var i in scope.sorts) {
                    var key = scope.sorts[i];
                    var val = 1;
                    if (key.charAt(0) === '-') {
                        key = key.slice(1);
                        val = -1;
                    }
                    var a_val = scope.getData(a, key);
                    var b_val = scope.getData(b, key);
                    if (typeof a_val == 'number' &&
                        $sessionStorage.use_fuzzy_sort === true &&
                        i < scope.sorts.length - 1) {
                        if (Math.abs(a_val - b_val) <= $sessionStorage.fuzzy_sort_tolerance) {
                            continue
                        }
                    }
                    if (a_val !== b_val) {
                        return a_val > b_val ? val : -val;
                    }
                }
                return 0;
            });
        };
        scope.updateSort();
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
        function (data) {
            $scope.team_info = data;
        })
        .then(function (data) {
            $scope.team_info = data;
        });

    EventDataService.getTeamStats($scope.team_number,
        function (data) {
            $scope.avg_data = data;
        })
        .then(function (data) {
            $scope.avg_data = data;
        });

    EventDataService.getTeamRaw($scope.team_number,
        function (data) {
            $scope.raw_data = data;
        })
        .then(function (data) {
            $scope.raw_data = data;
            updateCubeChart();
            updateAutoCubeChart();
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
        if (key.indexOf(",") > -1 || key.indexOf(".") > -1) {
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
    function genColors(n) {
        var h, s, l;
        var colors = [];
        for (var i = 0; i < 360; i += 360 / n) {
            h = i / 360;
            s = 0.40;
            l = 0.50;

            var r, g, b;
            if (s == 0) {
                r = g = b = l; // achromatic
            }
            else {
                var hue2rgb = function hue2rgb(p, q, t) {
                    if (t < 0) t += 1;
                    if (t > 1) t -= 1;
                    if (t < 1 / 6) return p + (q - p) * 6 * t;
                    if (t < 1 / 2) return q;
                    if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
                    return p;
                };

                var q = l < 0.5 ? l * (1 + s) : l + s - l * s;
                var p = 2 * l - q;
                r = hue2rgb(p, q, h + 1 / 3);
                g = hue2rgb(p, q, h);
                b = hue2rgb(p, q, h - 1 / 3);
            }
            var red = ("0" + Math.round(r * 255).toString(16)).slice(-2).toUpperCase();
            var green = ("0" + Math.round(g * 255).toString(16)).slice(-2).toUpperCase();
            var blue = ("0" + Math.round(b * 255).toString(16)).slice(-2).toUpperCase();
            colors.push("#" + red + green + blue);
        }
        return colors;
    }

    function updateCubeChart() {
        $scope.cube_chart_data = [];
        $scope.cube_chart_labels = [];
        cube_chart_keys.forEach(function (e) {
            $scope.cube_chart_data.push([]);
        });
        $scope.raw_data.forEach(function (row) {
            $scope.cube_chart_labels.push(row['match']);
            for (var i in cube_chart_keys) {
                $scope.cube_chart_data[i].push(row[cube_chart_keys[i]]);
            }
        });
    }

    var cube_chart_keys = ['tele_scored_exchange', 'tele_scored_scale', 'tele_scored_own_switch', 'tele_scored_opp_switch'];
    $scope.cube_chart_series = ['Exchange Cubes', 'Scale Cubes', 'Home Switch Cubes', 'Away Switch Cubes'];
    $scope.cube_chart_colors = genColors(4);//['#4CAF50', '#69F0AE', '#76FF03', '#B2FF59'];
    $scope.cube_chart_options = {
        scales: {
            yAxes: [{
                stacked: true,
                display: true,
                position: 'left'
            }],
            xAxes: [{
                stacked: true
            }]
        }
    };
    updateCubeChart();

    function updateAutoCubeChart() {
        $scope.auto_cube_chart_data = [];
        $scope.auto_cube_chart_labels = [];
        auto_cube_chart_keys.forEach(function (e) {
            $scope.auto_cube_chart_data.push([]);
        });
        $scope.raw_data.forEach(function (row) {
            $scope.auto_cube_chart_labels.push(row['match']);
            for (var i in auto_cube_chart_keys) {
                $scope.auto_cube_chart_data[i].push(row[auto_cube_chart_keys[i]]);
            }
        });
    }

    var auto_cube_chart_keys = ['auto_scored_exchange', 'auto_scored_scale', 'auto_scored_switch'];
    $scope.auto_cube_chart_colors = genColors(4);//['#4CAF50', '#69F0AE', '#B2FF59'];
    $scope.auto_cube_chart_series = ['Exchange', 'Scale', 'Switch'];
    $scope.auto_cube_chart_options = {
        scales: {
            yAxes: [{
                stacked: true,
                display: true,
                position: 'left',
                ticks: {
                    max: 4,
                    interval: 1
                }
            }],
            xAxes: [{
                stacked: true
            }]
        }
    };
    updateAutoCubeChart();


});

app.controller('MatchPreviewController', function ($scope, $http, $sessionStorage, $location, $cookies, EventDataService) {
    $scope.match_key = $location.url().split("/")[2];
    $scope.event = EventDataService.getSelectedEvent();

    if ($scope.event !== undefined) {
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
    }

    if ($sessionStorage.stats_avg_headers == undefined && $scope.event !== undefined) {
        $http.get("/api/headers/" + $scope.event.id + "/stats_avg", {cache: true})
            .then(function (response) {
                $scope.data_headers = response.data;
                $sessionStorage.stats_avg_headers = $scope.data_headers;
            });
    }
    else {
        $scope.data_headers = $sessionStorage.stats_avg_headers;
    }

    EventDataService.getEventStats(
        function (data) {
            if (data != undefined) {
                $scope.avg_data = {};
                data.forEach(function (elem) {
                    $scope.avg_data[elem.team_number.value] = elem;
                })
            }
        })
        .then(function (data) {
            if (data != undefined) {
                $scope.avg_data = {};
                data.forEach(function (elem) {
                    $scope.avg_data[elem.team_number.value] = elem;
                })
            }
        });

    $scope.getData = function (elem, key) {
        if (elem === undefined || key === undefined) {
            return "";
        }
        if (key.indexOf(",") > -1 || key.indexOf(".") > -1) {
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