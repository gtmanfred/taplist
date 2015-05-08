var taplist = angular.module('taplist', [])
taplist.config(function($locationProvider) {
  $locationProvider.html5Mode({
    enabled: true,
    requireBase: false
  });
});
taplist.controller('TaplistController', ['$scope', '$log', '$http', '$location', function($scope, $log, $http, $location) {
  $log.log($location.search()['name']);
  $scope.beerdata = {};
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
  } else {
      $scope.scroll = false;
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
  } else {
      $scope.entry = false;
  };

  if ($scope.loc !== '/') {
      get_beers();
  };
  get_locations();
}]);
