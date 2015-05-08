var taplist = angular.module('taplist', [])
taplist.config(function($locationProvider) {
  $locationProvider.html5Mode({
    enabled: true,
    requireBase: false
  });
});
taplist.controller('TaplistController', ['$scope', '$log', '$http', '$location', function($scope, $log, $http, $location) {
  $scope.beerdata = {
    beerid: "",
    beername: "",
    brewery: "",
    beertype: "",
    alcohols: "",
    pricepint: "",
    pricehalf: "",
    pricegrowler: "",
    notes: "",
    active: ""
  };
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
      var beerid = $location.search()['name'];
      if (beerid) {
        var url = 'https://taplists.beer' + $scope.loc + '/' + beerid;
        $http.get(url).
          success(function(data, status, headers, config) {
            $scope.beerdata.beerid = beerid;
            $scope.beerdata.beername = data['beer']['name'];
            $scope.beerdata.brewery = data['beer']['brewery'];
            $scope.beerdata.beertype = data['beer']['type'];
            $scope.beerdata.alcohols = data['beer']['content'];
            $scope.beerdata.pricepint = data['beer']['pint'];
            $scope.beerdata.pricehalf = data['beer']['half'];
            $scope.beerdata.pricegrowler = data['beer']['growler'];
            $scope.beerdata.notes = data['beer']['notes'];
            $scope.beerdata.active = data['beer']['active'];
          }).error(function(error){
            $log.log(error);
          });
      };
  } else {
      $scope.entry = false;
  };

  if ($scope.loc !== '/') {
      get_beers();
  };
  get_locations();
  $scope.entry = function(){
    var payload = {
        "brewery": $scope.beerdata.brewery,
        "beername": $scope.beerdata.beername,
        "beertype": $scope.beerdata.beertype,
        "alcohols": $scope.beerdata.alcohols,
        "active": $scope.beerdata.active,
        "pricepint": $scope.beerdata.pricepint,
        "pricehalf": $scope.beerdata.pricehalf,
        "pricegrowler": $scope.beerdata.pricegrowler,
        "notes": $scope.beerdata.notes
    };
    if ($scope.beerid) {
      payload.name = $scope.beerdata.beerid;
      $http.put("https://taplists.beer/entry", payload).
        success(function(data, status, headers, config) {
          $log.log(status);
        }).error(function(error){
          $log.log(error);
        });
    } else {
      $http.post("https://taplists.beer/entry", payload).
        success(function(data, status, headers, config) {
          $log.log(status);
        }).error(function(error){
          $log.log(error);
        });
    };
  };
}]);
