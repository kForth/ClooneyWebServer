app = angular.module('app');app.factory('AuthService', function ($http, Session, md5, $sessionStorage) {
        var authService = {};
        authService.guest_user = {
            'name': 'Guest',
            'username': 'guest',
            'role': 0,
            'api_key': 'guest'
        }

        authService.testCachedUser = function(){
            if($sessionStorage.user !== undefined){
                return true;
            }
            else{
                $sessionStorage.user = angular.copy(authService.guest_user)
                return false
            }
        };

        authService.login = function (credentials) {
            var user_pass = {
                username: credentials.username,
                password: md5.createHash(credentials.password)
            };
            return $http
                .post('/user/login', user_pass)
                .then(
                    function (resp) {
                        $sessionStorage.user = resp.data
                        return true;
                    },
                    function (resp) {
                        $sessionStorage.user = angular.copy(authService.guest_user)
                        return false;
                    }
                );
        };

        authService.logout = function(){
            $sessionStorage.user = {
                'name': 'Guest',
                'username': 'guest',
                'role': 0,
                'api_key': 'guest'
            }
        };

        authService.isLoggedIn = function(){
            return $sessionStorage.user && $sessionStorage.user.role > 0
        };

        authService.isAuthorized = function(min_level) {
            return $sessionStorage.user['role'] >= min_level;
        };

        authService.updateName = function(new_name, password, user_to_update){
            if(user_to_update === undefined){
                user_to_update = $sessionStorage.user.username
            }
            return $http.post('/user/update/name', {
                'username': $sessionStorage.user.username,
                'password': password || '',
                'user_to_update': user_to_update,
                'new_name': new_name
            })
            .then(
                function(resp){
                    $sessionStorage.user.name = new_name
                    return true;
                },
                function(resp){
                    return false;
                }
            )
        }

        authService.updateUsername = function(old_pass, new_username, user_to_update){
            if(user_to_update === undefined){
                user_to_update = $sessionStorage.user.username
            }
            return $http.post('/user/update/username', {
                'username': $sessionStorage.user.username,
                'password': old_pass,
                'user_to_update': user_to_update,
                'new_username': new_username
            })
            .then(
                function(resp){
                    $sessionStorage.user.username = new_username
                    return {success: true};
                },
                function(resp){
                    return {
                        success: false,
                        bad_password: resp.status == 401,
                        bad_username: resp.status == 409
                    };
                }
            )
        }

        authService.updatePassword = function(old_pass, new_pass, user_to_update){
            if(user_to_update === undefined){
                user_to_update = $sessionStorage.user.username
            }
            return $http.post('/user/update/password', {
                'username': $sessionStorage.user.username,
                'old_pass': old_pass,
                'user_to_update': user_to_update,
                'new_pass': new_pass
            })
            .then(
                function(resp){
                    return true;
                },
                function(resp){
                    return false
                }
            )
        }

        authService.getUser = function(){
            return $sessionStorage.user;
        }

        return authService;
    })
    .service('Session', function () {
        this.create = function (sessionId, userId, userRole) {
            this.id = sessionId;
            this.userId = userId;
            this.userRole = userRole;
        };
        this.destroy = function () {
            this.id = null;
            this.userId = null;
            this.userRole = null;
        };
    })
    .controller("LoginController", function ($rootScope, $scope, $cookies, $location, $localStorage, AuthService) {
        if(AuthService.isLoggedIn()){
            $location.path('/logout');
        }

        $scope.credentials = {
            username: $localStorage.username || '',
            password: ''
        };
        $scope.errors = false;
        $scope.login = function (credentials) {
            AuthService.login(credentials).then(function(success){
                if(success){
                    $scope.errors = false;
                    $location.path('/');
                }
                else{
                    $scope.errors = true;
                }
            });
        };
    })
    .controller("LogoutController", function ($rootScope, $scope, $cookies, $location, $localStorage, AuthService) {
        if(!AuthService.isLoggedIn()){
            $location.path('/login');
        }

        $scope.logout = function() {
            AuthService.logout();
            $location.path('/');
        };
    })
    .controller("EditAccountController", function ($rootScope, $scope, $cookies, $location, $localStorage, AuthService) {
        if(!AuthService.isLoggedIn() || !AuthService.isAuthorized(5)){
            $location.path('/');
        }

        $scope.name_new = AuthService.getUser().name;
        $scope.username_new = AuthService.getUser().username;


        $scope.name_errors = [];
        $scope.username_errors = [];
        $scope.password_errors = [];

        $scope.changeName = function(new_name){
            AuthService.updateName(new_name)
            .then(function(success){
                $scope.username_errors = !success;
            })
        }

        $scope.changeUsername = function(new_username, old_pass){
            $scope.username_errors = []
            AuthService.updateUsername(old_pass, new_username)
            .then(function(resp){
                if(resp.success){
                    $scope.username_pwd = ""
                }
                else{
                    if(resp.bad_password){
                        $scope.username_errors.push("bad_password")   
                    }
                    if(resp.bad_username){
                        $scope.username_errors.push("bad_username")   
                    }
                }
            })
        }

        $scope.changePassword = function(old_pass, new_pass, new_pass2){
            $scope.password_errors = []
            if(new_pass === new_pass2){
                AuthService.updatePassword(old_pass, new_pass)
                .then(function(success){
                    if(success){
                        $scope.password_new = "";
                        $scope.password_new2 = "";
                        $scope.password_old = ""
                    }
                    else{
                        $scope.password_errors.push("old_password_wrong")
                    }
                })
            }
            else{
                $scope.password_errors.push("new_not_matching")
            }
        }

    });