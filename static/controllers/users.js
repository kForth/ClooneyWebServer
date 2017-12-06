app.controller('UserLogoutController', function ($scope, $localStorage, $sessionStorage, $location, AuthenticationService, $http) {
    AuthenticationService.Logout(false);
    $location.path("/login");
});

app.controller('UserLoginController', function ($scope, $localStorage, $rootScope, $location, AuthenticationService) {
    if (AuthenticationService.isAuthorized(0)) $location.path("/");
    $scope.input = {
        'username': '',
        'password': ''
    };
    AuthenticationService.ClearCredentials();

    $scope.closeAlert = function () {
        $scope.alert = undefined;
    };

    $scope.login = function () {
        $rootScope.data_loading += 1;
        AuthenticationService.Login($scope.input.username, $scope.input.password,
            function (response) {
                $location.path('/');
            },
            function (ignored) {
                $scope.alert = 'Error. Try Again.';
                $rootScope.data_loading = 0;
            });
    }

});

app.controller('UserRegisterController', function ($scope, $rootScope, $location, $http) {
    $scope.input = {
        'first_name': '',
        'last_name': '',
        'username': '',
        'password': ''
    };

    $scope.closeAlert = function () {
        $scope.alert = undefined;
    };

    $scope.register = function () {
        $rootScope.data_loading += 1;
        $http.post('/users/create/', $scope.input)
            .then(function (ignored) {
                    $location.path('/login');
                },
                function (ignored) {
                    $scope.alert = 'Error. Try Again.';
                    $rootScope.data_loading = 0;
                });
    }
});