app.controller('SetupEventController', function ($scope, $sessionStorage, $location, $http, AuthenticationService) {
    if (!AuthenticationService.isAuthorized(2)) $location.path("/");
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
    $scope.closeAlert = function () {
        $scope.alert = false
    };

    //Step 0 - Ask if we should use TBA
    $scope.setup_with_tba_button = function () {
        $scope.setup_step = 1;
        $scope.searchable_events = [];
        $http.get('/get/search_events').then(function (resp) {
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
            .then(function (resp) {
                    if (resp.status === 200) {
                        $scope.update_available_events();
                        $sessionStorage.tracked_event = resp.data;
                        $sessionStorage.tracked_event_okay = true;
                        $location.path('/s');
                    }
                },
                function (resp) {
                    if (resp.status === 409) {
                        $scope.alert = {type: 'danger', msg: event.key + ' has already been setup.'};
                    }
                    else {
                        $scope.alert = {
                            type: 'danger',
                            msg: 'Some kind of error occurred with ' + event.key + '. Try again?'
                        };
                    }
                });
    };

    //Step 2 - Edit the event information
    $scope.input_data = {};
    $scope.submit_manual_data = function () {
        // $location.path('/s/e');
    };


});