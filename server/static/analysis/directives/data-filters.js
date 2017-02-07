var app = angular.module('app');

app.directive('filter-float', function(){
    function link(scope){
        console.log(scope.restrict);
    }

    function getTemplate(scope){
        return "";
    }

    return {
        link: link,
        restrict: 'C',
        transclude: true,
        template: "<b>Float</b>"
    };
});