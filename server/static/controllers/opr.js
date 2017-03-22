var app = angular.module('app')
    .controller("OprController", function($scope, $cookies, $http){
        $scope.event = {
            name: $cookies.get('selected-event-name'),
            key: $cookies.get('selected-event-id')
        };

        $scope.selectedEvent = undefined;


        $http.get("/api/sql/opr/events")
            .then(function(response){
                console.log(response.data);
                $scope.events = response.data;
            });


        function updateHeaders(){
            $http.get("/api/headers/" + $scope.event.key + "/oprs")
                .then(function (response) {
                    $scope.headers = response.data;
                });
        }


        $scope.updateEvent = function(){
            $scope.event.key = $scope.selectedEvent;
            $cookies.put('selected-event-id', $scope.event.key);
            updateHeaders();

            var data = {
                q: JSON.stringify({
                    filters: [{
                        name: 'event',
                        op: '==',
                        val: $scope.event
                    }]
                })
            };
            $http.get('/api/sql/oprs', data)
                .then(function(response){
                    console.log(response.data.objects);
                    // $scope.data = response.data;
                    if (response.data.objects.length < 1) {
                        angular.element(document.querySelector("#table"))[0].innerHTML = "No OPRs found."
                    }
                });
        };
    });