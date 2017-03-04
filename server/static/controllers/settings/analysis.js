var app = angular.module('settingsApp', ['ngRoute', 'ui.bootstrap', 'ngCookies']);

app.controller('HeaderEditController', function ($http, $scope, $location, $cookies) {

    $scope.add_message = "Add Header";
    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };

    $scope.reset = function () {
        var headerTarget = "/api/headers/" + $scope.event.key + "/" + $cookies.get('selected-header-group');
        $http.get('/api/headers/' + $scope.event.key + '/meta').then(function (response) {
            $scope.headers = angular.copy(response.data);
        });
        $http.get(headerTarget).then(function (response) {
            $scope.edit_headers = angular.copy(response.data);
        });
    };

    $scope.save = function () {
        var headerTarget = "/api/headers/" + $scope.event.key + "/" + $cookies.get('selected-header-group');
        $http.post(headerTarget, $scope.edit_headers).then(function (response) {
            if (response.status != 200) {
                console.log("Couldn't Save");
            }
        });
        $scope.reset();
    };

    $scope.addRow = function () {
        $scope.edit_headers.push({});
    };

    $scope.duplicateRow = function (row) {
        $scope.edit_headers.splice($scope.edit_headers.indexOf(row) + 1, 0, angular.copy(row));
    };

    $scope.deleteRow = function (row) {
        $scope.edit_headers.splice($scope.edit_headers.indexOf(row), 1)
    };

    $scope.descendRow = function (row) {
        var index = $scope.edit_headers.indexOf(row);
        if (index >= $scope.edit_headers.length) return;
        $scope.deleteRow(row);
        $scope.edit_headers.splice(index + 1, 0, angular.copy(row));
    };

    $scope.ascendRow = function (row) {
        var index = $scope.edit_headers.indexOf(row);
        if (index <= 0) return;
        $scope.deleteRow(row);
        $scope.edit_headers.splice(index - 1, 0, angular.copy(row));
    };

    if($scope.event.key != undefined){
        $scope.reset();
    }

});

app.controller('ExpressionEditController', function ($http, $scope, $location, $cookies) {

    $scope.add_message = "Add Expression";
    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };

    var headerTarget = "/api/event/" + $scope.event.key + "/expressions";
    $scope.reset = function () {
        $http.get('/api/headers/' + $scope.event.key + '/expressions').then(function (response) {
            $scope.headers = angular.copy(response.data);
        });
        $http.get(headerTarget).then(function (response) {
            $scope.edit_headers = angular.copy(response.data);
        });
    };

    $scope.save = function () {
        $http.post(headerTarget, $scope.edit_headers).then(function (response) {
            if (response.status != 200) {
                console.log("Couldn't Save");
            }
        });
        $scope.reset();
    };

    $scope.addRow = function () {
        $scope.edit_headers.push({});
    };

    $scope.duplicateRow = function (row) {
        $scope.edit_headers.splice($scope.edit_headers.indexOf(row) + 1, 0, angular.copy(row));
    };

    $scope.deleteRow = function (row) {
        $scope.edit_headers.splice($scope.edit_headers.indexOf(row), 1)
    };

    $scope.descendRow = function (row) {
        var index = $scope.edit_headers.indexOf(row);
        if (index >= $scope.edit_headers.length) return;
        $scope.deleteRow(row);
        $scope.edit_headers.splice(index + 1, 0, angular.copy(row));
    };

    $scope.ascendRow = function (row) {
        var index = $scope.edit_headers.indexOf(row);
        if (index <= 0) return;
        $scope.deleteRow(row);
        $scope.edit_headers.splice(index - 1, 0, angular.copy(row));
    };

    if($scope.event.key != undefined){
        $scope.reset();
    }

});

app.controller('SidebarController', function ($scope, $location, $cookies, $http, $route) {

    $scope.isActive = function (viewLocation) {
        return viewLocation === $location.path();
    };

    $scope.getSelectedEvent = function () {
        var event = $cookies.get('selected-event-name');
        if (event === undefined) {
            return 'Select'
        }
        return event;
    };
    $scope.isSelectedEvent = function (event) {
        return event === $cookies.get('selected-event-id');
    };
    $scope.selectEvent = function (event) {
        $cookies.put('selected-event-id', event.id);
        $cookies.put('selected-event-name', event.name);
        loadGroups();
        $route.reload()
    };

    $http.get("/api/events")
        .then(function (response) {
            $scope.events = response.data;
        });

    $scope.getSelectedHeaders = function () {
        var group = $cookies.get('selected-header-group');
        if (group === undefined) {
            return 'Select'
        }
        return group;
    };
    $scope.isSelectedHeaders = function (group) {
        return group === $cookies.get('selected-header-group');
    };
    $scope.selectHeaders = function (group) {
        $scope.headerGroup = group;
        $cookies.put('selected-header-group', group);
        $route.reload()
    };

    function loadGroups(){
        $http.get('/api/headers/' + $scope.event.key).then(function (response) {
            $scope.headerGroups = angular.copy(response.data);
            $route.reload()
        });
    }

    $scope.event = {
        name: $cookies.get('selected-event-name'),
        key: $cookies.get('selected-event-id')
    };
    $scope.headerGroup = "";
    if($scope.event.key != undefined){
        loadGroups();
    }

});

app.config(function ($routeProvider) {
    $routeProvider
        .when('/h', {
            templateUrl: '../../../../static/views/settings/edit_table.html',
            controller: 'HeaderEditController'
        })
        .when('/e', {
            templateUrl: '../../../../static/views/settings/edit_table.html',
            controller: 'ExpressionEditController'
        })
        .otherwise({redirectTo: '/h'});
});