var app = angular.module('app');

app.controller('SidebarController', function ($scope, $location, $cookies, $http, $route) {
    $scope.isActive = function (viewLocation) {
        return viewLocation.replace("/", "") === $location.path().split('/')[1];
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
        $route.reload()
    };

    $scope.match_levels = [
          {
              link: "",
              name: "All Matches"
          },
          {
              link: "qm",
              name: "Qualification"
          },
          {
              link: "qf",
              name: "Quarter-Finals"
          },
          {
              link: "sf",
              name: "Semi-Finals"
          },
          {
              link: "f",
              name: "Finals"
          }
      ];

    $scope.getSelectedLevel = function() {
        if($location.path().split('/')[1] == "m" && $location.path().split('/').length > 2){
            return $location.path().split('/')[2].toUpperCase();
        }
        else{
            return "Select";
        }
    };

    $http.get("/api/events/2016")
        .then(function (response) {
            $scope.events = response.data;
        });

    var cachedList = $cookies.get('picklist');

    if (cachedList != undefined) {
        var picklistArea = angular.element(document.querySelector('#picklist'))[0];
        picklistArea.value = cachedList;
    }

    $scope.updateList = function () {
        var picklistArea = angular.element(document.querySelector('#picklist'))[0];
        $cookies.put('picklist', picklistArea.value);
    };

    $scope.increaseFont = function () {
        updateFont(2)
    };
    $scope.decreaseFont = function () {
        updateFont(-2)
    };
    function updateFont(delta) {
        var picklistArea = angular.element(document.querySelector('#picklist'))[0];
        if (picklistArea.style.fontSize == '') {
            picklistArea.style.fontSize = 15 + Math.sign(delta);
        }
        picklistArea.style.fontSize = parseInt(picklistArea.style.fontSize) + delta;
    }

    $scope.saveList = function () {
        var filename = 'picklist.txt';
        var data = angular.element(document.querySelector('#picklist'))[0].value;
        var success = false;
        var contentType = 'text/plain;charset=utf-8';

        try {
            // Try using msSaveBlob if supported
            var blob = new Blob([data], {type: contentType});
            if (navigator.msSaveBlob) {
                navigator.msSaveBlob(blob, filename);
            }
            else {
                // Try using other saveBlob implementations, if available
                var saveBlob = navigator.webkitSaveBlob || navigator.mozSaveBlob || navigator.saveBlob;
                if (saveBlob === undefined) throw "Not supported";
                saveBlob(blob, filename);
            }
            success = true;
        } catch (ex) {
            console.log("saveBlob method failed with the following exception:");
            console.log(ex);
        }

        if (!success) {
            // Get the blob url creator
            var urlCreator = window.URL || window.webkitURL || window.mozURL || window.msURL;
            if (urlCreator) {
                // Try to use a download link
                var link = document.createElement('a');
                if ('download' in link) {
                    // Try to simulate a click
                    try {
                        // Prepare a blob URL
                        var blob = new Blob([data], {type: contentType});
                        var url = urlCreator.createObjectURL(blob);
                        link.setAttribute('href', url);

                        // Set the download attribute (Supported in Chrome 14+ / Firefox 20+)
                        link.setAttribute("download", filename);

                        // Simulate clicking the download link
                        var event = document.createEvent('MouseEvents');
                        event.initMouseEvent('click', true, true, window, 1, 0, 0, 0, 0, false, false, false, false, 0, null);
                        link.dispatchEvent(event);
                        console.log("Download link method with simulated click succeeded");
                        success = true;

                    } catch (ex) {
                        console.log("Download link method with simulated click failed with the following exception:");
                        console.log(ex);
                    }
                }

                if (!success) {
                    alert("Download Failed. Try again.")
                }

            }
        }

        if (!success) {
            // Fallback to window.open method
            console.log("No methods worked for saving the array buffer, using last resort window.open.  Not Implemented");
            //window.open(httpPath, '_blank', '');
        }
    };

    $scope.copyList = function () {
        var textArea = angular.element(document.querySelector('#picklist'))[0];
        textArea.select();
        document.execCommand('copy');
    };

    $scope.toggleSidebar = function () {
        $scope.sidebarShown = !$scope.sidebarShown;
        if ($scope.sidebarShown) {
            $scope.toggleVerb = "Hide";
        }
        else {
            $scope.toggleVerb = "Show";
        }
        $route.reload();
    };
    $scope.sidebarShown = false;
    $scope.toggleVerb = "Show";

});