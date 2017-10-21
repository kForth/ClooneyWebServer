var app = angular.module('app', ['ngRoute', 'ui.bootstrap', 'ngCookies', 'angular-md5', 'chart.js'])
    .config(function ($routeProvider, $locationProvider) {
        $locationProvider.html5Mode(false).hashPrefix('');
        $routeProvider
            .when('/', {
                templateUrl: '../../../static/views/pages/home.html',
                controller: 'MainViewController'
            })
            .when('/sheets', {
                templateUrl: '../../../static/views/pages/create_sheets.html',
                controller: 'SheetCreatorController'
            })
            .otherwise({
                redirectTo: '/'
            });
    });

app.controller('ApplicationController', function () {

});

app.controller('MainViewController', function () {

});

app.directive('fieldSettingsDirective', function () {
    function link($scope) {
        $scope.show_contents = true;
        $scope.toggle_contents = function () {
            $scope.show_contents = !$scope.show_contents;
        };

    $scope.get_field_settings = function (field_type) {
        switch (field_type) {
            default:
                return {};
            case 'Numbers':
                return [
                    {
                        'name': 'Label',
                        'type': 'text',
                        'id': 'label',
                        'default': ''
                    },
                    {
                        'name': 'Max Value',
                        'type': 'number',
                        'id': 'ones',
                        'default': 9
                    },
                    {
                        'name': '\'+10\'s',
                        'type': 'number',
                        'id': 'tens',
                        'default': 1
                    },
                    {
                        'name': 'Show Zero',
                        'type': 'checkbox',
                        'id': 'show_zero',
                        'default': false
                    },
                    {
                        'name': 'Allow Prev Line',
                        'type': 'checkbox',
                        'id': 'prev_line',
                        'default': false
                    },
                    {
                        'name': 'Prev Line Offset',
                        'type': 'number',
                        'id': 'offset',
                        'default': 0
                    },
                    {
                        'name': 'Add Note Space',
                        'type': 'checkbox',
                        'id': 'note_space',
                        'default': false
                    },
                    {
                        'name': 'Note Space Width',
                        'type': 'number',
                        'id': 'note_width',
                        'default': 0
                    }
                ]
        }
    };
    }

    var directive = {
        restrict: 'C',
        scope: {
            field: '='
        },
        link: link,
        templateUrl: '../../static/views/templates/field_settings.html'
        // template: ''
    };

    return directive;

    // directive.compile = function (element, attributes) {
    //     // element.css("border", "1px solid #cccccc");
    //
    //     //linkFunction is linked with each element with scope to get the element specific data.
    //     var linkFunction = function ($scope, element, attributes) {
    //         // element.html("Student: <b>"+$scope.student.name +"</b> , Roll No: <b>"+$scope.student.rollno+"</b><br/>");
    //         // element.css("background-color", "#ff00ff");
    //     };
    //     return linkFunction;
    // };
});

app.controller('SheetCreatorController', function ($scope, $cookies) {
    // if($cookies.get('fields_data') != undefined){
    //     $scope.data = $cookies.get('fields_data');
    // }
    // else{
        $scope.data = [];
    // }

    $scope.add_field_status = {
        isopen: false
      };

    $scope.add_field = function(){
        var settings = $scope.get_field_settings('Numbers');
        var obj = {
            'id': '',
            'type': 'Numbers',
            'options': {}
        };
        for(var e in settings){
            e = settings[e];
            obj['options'][e.id] = e.default;
        }
        $scope.data.push(obj);
        $cookies.put('fields_data', $scope.data);
        console.log($scope.data);
    };

    $scope.get_field_settings = function (field_type) {
        switch (field_type) {
            default:
                return {};
            case 'Numbers':
                return [
                    {
                        'name': 'Label',
                        'type': 'text',
                        'id': 'label',
                        'default': ''
                    },
                    {
                        'name': 'Max Value',
                        'type': 'number',
                        'id': 'ones',
                        'default': 9
                    },
                    {
                        'name': '\'+10\'s',
                        'type': 'number',
                        'id': 'tens',
                        'default': 1
                    },
                    {
                        'name': 'Show Zero',
                        'type': 'checkbox',
                        'id': 'show_zero',
                        'default': false
                    },
                    {
                        'name': 'Allow Prev Line',
                        'type': 'checkbox',
                        'id': 'prev_line',
                        'default': false
                    },
                    {
                        'name': 'Prev Line Offset',
                        'type': 'number',
                        'id': 'offset',
                        'default': 0
                    },
                    {
                        'name': 'Add Note Space',
                        'type': 'checkbox',
                        'id': 'note_space',
                        'default': false
                    },
                    {
                        'name': 'Note Space Width',
                        'type': 'number',
                        'id': 'note_width',
                        'default': 0
                    }
                ]
        }
    };

    // $scope.data = [
    //     {
    //         "name": "Draw the Robot",
    //         "type": "Image",
    //         "options": {
    //             "label": "Draw the Robot",
    //             "width": 2,
    //             "height": 1.5,
    //             "image_path": null,
    //             "prev_line": true,
    //             "offset": 3.75,
    //             "y_offset": 1.25
    //         },
    //         "id": "robot_drawing"
    //     },
    //     {
    //         "name": "Auto Divider",
    //         "type": "Divider",
    //         "options": {
    //             "label": "Autonomous"
    //         }
    //     },
    //     {
    //         "name": "Auto Didn't Move",
    //         "type": "Boolean",
    //         "options": {
    //             "label": "Didn't Move"
    //         },
    //         "id": "auto_no_move"
    //     },
    //     {
    //         "name": "Auto Scored Low Boiler",
    //         "type": "Boolean",
    //         "options": {
    //             "label": "Scored Low Boiler",
    //             "prev_line": true
    //         },
    //         "id": "auto_scored_low"
    //     },
    //     {
    //         "name": "Auto Triggered Hopper",
    //         "type": "Boolean",
    //         "options": {
    //             "label": "Triggered Hopper",
    //             "prev_line": true
    //         },
    //         "id": "auto_triggered_hopper"
    //     },
    //     {
    //         "name": "Auto Scored High",
    //         "type": "Numbers",
    //         "options": {
    //             "label": "Scored High",
    //             "tens": 5
    //         },
    //         "id": "auto_scored_high"
    //     },
    //     {
    //         "name": "Auto Gear Location",
    //         "type": "MultipleChoice",
    //         "options": {
    //             "label": "Gear Location",
    //             "options": [
    //                 "NA",
    //                 "Blr",
    //                 "Mid",
    //                 "RZ"
    //             ]
    //         },
    //         "default": "NA",
    //         "id": "auto_gear_location"
    //     },
    //     {
    //         "name": "Auto Gears Scored",
    //         "type": "Numbers",
    //         "options": {
    //             "label": "Gears Scored",
    //             "ones": 3,
    //             "prev_line": true
    //         },
    //         "id": "auto_gears_scored",
    //         "prev_line": true
    //     },
    //     {
    //         "name": "Tele-Op Divider",
    //         "type": "Divider",
    //         "options": {
    //             "label": "Tele-Op"
    //         }
    //     },
    //     {
    //         "name": "Gears Placed",
    //         "type": "Numbers",
    //         "options": {
    //             "label": "Placed Gears",
    //             "tens": 1,
    //             "note_space": true
    //         },
    //         "id": "tele_gears_scored"
    //     },
    //     {
    //         "name": "Gears From Near",
    //         "type": "Numbers",
    //         "options": {
    //             "label": "Gears from Near",
    //             "tens": 1,
    //             "note_space": true
    //         },
    //         "id": "tele_gears_from_near"
    //     },
    //     {
    //         "name": "Gears From Far",
    //         "type": "Numbers",
    //         "options": {
    //             "label": "Gears from Far",
    //             "tens": 1,
    //             "note_space": true
    //         },
    //         "id": "tele_gears_from_far"
    //     },
    //     {
    //         "name": "Scored High",
    //         "type": "MultipleChoice",
    //         "options": {
    //             "label": "Scored High",
    //             "options": [
    //                 ["💩", 0],
    //                 ["👎", 1],
    //                 ["👍", 2],
    //                 ["🔥", 3]
    //             ]
    //         },
    //         "id": "tele_scored_high",
    //         "default": "NA"
    //     },
    //     {
    //         "name": "Performace Divider",
    //         "type": "Divider",
    //         "options": {
    //             "label": "Overall Performance"
    //         }
    //     },
    //     {
    //         "name": "Sopped Moving",
    //         "type": "Boolean",
    //         "options": {
    //             "label": "Stopped Moving"
    //         },
    //         "id": "disabled"
    //     },
    //     {
    //         "name": "Never Moved",
    //         "type": "Boolean",
    //         "options": {
    //             "label": "Never Moved",
    //             "prev_line": true
    //         },
    //         "id": "no_move"
    //     },
    //     {
    //         "name": "No Show",
    //         "type": "Boolean",
    //         "options": {
    //             "label": "No Show",
    //             "prev_line": true
    //         },
    //         "id": "no_show"
    //     },
    //     {
    //         "name": "Climbed",
    //         "type": "MultipleChoice",
    //         "options": {
    //             "label": "Climbed",
    //             "options": [
    //                 ["S", 1],
    //                 ["F", 0]
    //             ]
    //         },
    //         "id": "tele_climbed",
    //         "default": "NA"
    //     },
    //     {
    //         "name": "Defense",
    //         "type": "MultipleChoice",
    //         "options": {
    //             "label": "Defense",
    //             "options": [
    //                 ["💩", 0],
    //                 ["👎", 1],
    //                 ["👍", 2],
    //                 ["🔥", 3]
    //             ],
    //             "prev_line": true
    //         },
    //         "id": "tele_defense",
    //         "default": ""
    //     },
    //     {
    //         "name": "Notes",
    //         "type": "Image",
    //         "options": {
    //             "label": "Notes",
    //             "width": 5.625,
    //             "height": 2.5,
    //             "image_path": null
    //         },
    //         "id": "notes"
    //     }
    // ];
});