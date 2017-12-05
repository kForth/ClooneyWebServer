app.controller('SheetsHomeController', function ($scope, $rootScope, $location, $http, AuthenticationService, FileSaver, Blob) {
    if (!AuthenticationService.isAuthorized(2)) $location.path("/");
    $scope.sheets = [];

    $scope.showDownloadDialog = function (sheet) {
        $scope.selected_sheet = sheet;
        $scope.start_match_number = 0;
        $scope.end_match_number = 100;

    };

    $scope.downloadSheet = function () {
        $rootScope.data_loading += 1;
        $http.get('/download_sheet/' + $scope.selected_sheet.id + "/" + $scope.start_match_number + "/" + $scope.end_match_number)
            .then(function (resp) {
                    var data = new Blob([resp.data], {type: 'text/plain;charset=utf-8'});
                    FileSaver.saveAs(data, $scope.selected_sheet.name + '.pdf');
                    $rootScope.data_loading = 0;
                    $scope.cancelDownload();
                },
                function (ignored) {
                    $rootScope.data_loading = 0;
                });
    };

    $scope.cancelDownload = function () {
        $scope.selected_sheet = undefined;
    };

    $http.get('/get/sheets')
        .then(function (resp) {
            $scope.sheets = resp.data;
        });
});

app.controller('SheetsEditController', function ($scope, $rootScope, $location, $http, AuthenticationService, appPath) {
    if (!AuthenticationService.isAuthorized(2)) $location.path("/");
    $scope.sheet_mode = appPath.mode;
    $scope.expanded = {};

    if (appPath.id != undefined) {
        $rootScope.data_loading += 1;
        $http.get('/get/sheet/' + appPath.id)
            .then(function (resp) {
                    $scope.sheet = resp.data;
                    $scope.backup_sheet = angular.copy($scope.sheet);
                },
                function (ignored) {
                    $location.path('/sheets');
                });
    }
    else {
        $scope.sheet = {
            'name': '',
            'id': undefined,
            'data': []
        };
    }

    $scope.saveSheet = function () {
        if ($scope.sheet.name.length < 5) {
            return;
        }
        $rootScope.data_loading += 1;
        $http.post('/save/sheet', $scope.sheet)
            .then(function (ignored) {
                    $rootScope.data_loading = 0;
                },
                function (ignored) {
                    $rootScope.data_loading = 0;
                    console.error('Failed to save sheet.');
                });
    };

    $scope.cancelSheet = function () {
        $location.path('/sheets');
    };

    $scope.revertSheet = function () {
        // $scope.sheet = angular.copy($scope.backup_sheet);
    };

    $scope.saveEditField = function () {
        $scope.sheet.data[$scope.selected_field_index] = $scope.selected_field;
        $scope.cancelEditField();
    };

    $scope.cancelEditField = function () {
        $scope.selected_field = undefined;
    };

    $scope.editField = function (field) {
        $scope.selected_field_index = $scope.sheet.data.indexOf(field);
        $scope.selected_field = angular.copy(field);
    };

    $scope.addField = function (type, field) {
        var new_field = {
            'type': type
        };
        for (var i in field) {
            var option = field[i];
            switch (option.type) {
                default:
                case 'text':
                    new_field[option.id] = option.value || "";
                    break;
                case 'number':
                    new_field[option.id] = option.value || 0;
                    break;
                case 'checkbox':
                    new_field[option.id] = option.value || false;
                    break;
            }
        }

        var existing_keys = [];
        $scope.sheet.data.forEach(function (e) {
            existing_keys.push(e.key || []);
        });
        var suffix_num = 0;
        if (existing_keys.indexOf(new_field.key) !== -1) new_field.key = new_field.key + "_" + (++suffix_num);
        while (existing_keys.indexOf(new_field.key) !== -1) {
            new_field.key = new_field.key.substring(0, new_field.key.length - 1 - (++suffix_num).toString().length) + "_" + suffix_num.toString();
        }
        new_field.name = new_field.key.replace(/_/g, " ").toProperCase(); //Replace all '_' with ' '

        $scope.sheet.data.push(new_field);
    };

    $rootScope.data_loading += 1;
    $http.get("/get/default_fields")
        .then(function (resp) {
            $scope.default_fields = resp.data;
            $rootScope.data_loading = 0;
        });
});