var taplistApp = angular.module('taplist', []);
taplistApp.controller('TaplistController', ['$scope', '$log', '$http', function($scope, $log, $http) {
  function get_locations(){
    $http.get('https://taplists.beer/locations').
      success(function(data, status, headers, config) {
        $scope.locations = data['locations'];
      }).error(function(error){
        $log.log(error);
      });
  };
  function get_beers(){
    $http.get('https://taplists.beer' + $scope.loc + '/json').
      success(function(data, status, headers, config) {
        $scope.beers = data['beers'];
      }).error(function(error){
        $log.log(error);
      });
  };
  $scope.loc = $(location).attr('pathname');
  if ($scope.loc.indexOf('/scroll') > -1) {
      $scope.scroll = true;
      $scope.loc = $scope.loc.replace('/scroll', '');
  };

  if ($scope.loc.indexOf('/edit') > -1) {
      $scope.edit = true;
      $scope.loc = $scope.loc.replace('/edit', '');
  } else {
      $scope.edit = false;
  };

  if ($scope.loc.indexOf('/entry') > -1) {
      $scope.entry = true;
      $scope.loc = $scope.loc.replace('/entry', '');
  };

  if ($scope.loc !== '/') {
      get_beers();
  };
  get_locations();
}]);
