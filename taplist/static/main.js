var myApp = angular.module('TaplistApp', []);

myApp.controller('TaplistController', [$scope, $http, function($scope) {
    var loc = $(location).attr('pathname');
}]);
