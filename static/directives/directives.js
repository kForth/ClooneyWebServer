app.directive('highlightTable', function ($location, $sessionStorage) {
    function link(scope) {
        if ($sessionStorage.colours == undefined) $sessionStorage.colours = {};
        scope.colours = $sessionStorage.colours[$location.path()] || {};

        scope.$watch('colours', function () {
            $sessionStorage.colours[$location.path()] = scope.colours;
        });

        scope.$watch(function () {
            return angular.toJson($sessionStorage);
        }, function () {
            scope.colours = $sessionStorage.colours[$location.path()];
        });

        scope.clearColours = function (event) {
            if (event.shiftKey || event.ctrlKey || event.metaKey) {
                scope.colours = {};
            }
        };

        scope.cycleColour = function (event, index) {
            if (scope.colours[index] === undefined)
                scope.colours[index] = 0;
            if (event.shiftKey) {
                scope.colours[index] = 0;
            }
            else if (event.ctrlKey || event.metaKey) {
                scope.colours[index] -= 1;
            }
            else {
                scope.colours[index] += 1;
            }
        };
    }

    return {
        link: link,
        restrict: 'A'
    };
});

app.directive('datacell', function () {
    function getData(obj, keys) {
        keys.split(".").forEach(function (key) {
            if (obj === undefined || keys === undefined) return obj;
            obj = obj[key];
        });
        return obj;
    }

    function link(scope) {
        scope.value = getData(scope.dcElement, scope.dcHeader.data_key);
        if (parseFloat(scope.value) == scope.value && parseInt(scope.value) != scope.value) {
            scope.value = scope.value.toFixed(2);
        }
    }

    return {
        link: link,
        restrict: 'E',
        template: "<span ng-show=\"dcHeader.title != 'Team'\" ng-class='dcHeader.data_class'>{{ value }}</span>" +
        "<a ng-click='dcTeamCallback(value)' ng-show=\"dcHeader.title == 'Team'\" ng-class='dcHeader.data_class'>{{ value }}</a>",
        scope: {
            'dcHeader': '=',
            'dcElement': '=',
            'dcTeamCallback': '='
        }
    }
});

app.directive('teamModal', function (EventDataService) {
    function link(scope) {
        scope.modalOpen = false;

        scope.closeModal = function () {
            scope.modalOpen = false;
        };
        scope.openModal = function (team) {
            scope.team_number = team;
            scope.team_data = EventDataService.getTeamAnalysis(team);

            scope.team_raw = EventDataService.getTeamEntries(team);

            scope.modalOpen = true;

            scope.team_data = EventDataService.get
        }
    }

    return {
        restrict: 'E',
        templateUrl: '../../static/views/templates/team_modal.html',
        replace: true,
        scope: false,
        link: link
    }
});

app.directive('multiSortTable', function ($location, $sessionStorage) {

    function link(scope) {
        if ($sessionStorage.sorts == undefined) $sessionStorage.sorts = {};
        scope.sorts = $sessionStorage.sorts[$location.path()];
        if (scope.sorts === undefined)
            scope.sorts = [];

        scope.$watch('sorts', function () {
            $sessionStorage.sorts[$location.path()] = scope.sorts;
        });

        scope.$watch(function () {
            return angular.toJson($sessionStorage);
        }, function () {
            scope.sorts = $sessionStorage.sorts[$location.path()];
        });


        scope.getData = function (obj, keys) {
            keys.split(".").forEach(function (e) {
                if (obj === undefined || keys === undefined) return obj;
                obj = obj[e];
            });
            return obj;
        };

        scope.sortData = function (event, key) {
            if (event.shiftKey) {
                scope.sorts = [];
            }
            if (scope.sorts.indexOf("-" + key) > -1) {
                if (event.ctrlKey || event.metaKey) {
                    scope.sorts.splice(scope.sorts.indexOf(key), 1);
                }
                else {
                    scope.sorts[scope.sorts.indexOf("-" + key)] = key;
                }
            }
            else if (scope.sorts.indexOf(key) > -1) {
                if (event.ctrlKey || event.metaKey) {
                    scope.sorts[scope.sorts.indexOf(key)] = "-" + key;
                }
                else {
                    scope.sorts.splice(scope.sorts.indexOf(key), 1);
                }
            }
            else {
                scope.sorts.push("-" + key);
            }
        };
    }

    return {
        link: link,
        restrict: 'A'
    };
});