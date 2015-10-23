// Ionic Starter App

var SERVER = 'localhost:9999';

// angular.module is a global place for creating, registering and retrieving Angular modules
// 'starter' is the name of this angular module example (also set in a <body> attribute in index.html)
// the 2nd parameter is an array of 'requires'
var app = angular.module('starter', ['ionic'], function ($httpProvider) {

	// Use x-www-form-urlencoded Content-Type
	$httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8';

	/**
	 * The workhorse; converts an object to x-www-form-urlencoded serialization.
	 * @param {Object} obj
	 * @return {String}
	 */
	var param = function (obj) {
		var query = '', name, value, fullSubName, subName, subValue, innerObj, i;

		for (name in obj) {
			value = obj[name];

			if (value instanceof Array) {
				for (i = 0; i < value.length; ++i) {
					subValue = value[i];
					fullSubName = name + '[' + i + ']';
					innerObj = {};
					innerObj[fullSubName] = subValue;
					query += param(innerObj) + '&';
				}
			}
			else if (value instanceof Object) {
				for (subName in value) {
					subValue = value[subName];
					fullSubName = name + '[' + subName + ']';
					innerObj = {};
					innerObj[fullSubName] = subValue;
					query += param(innerObj) + '&';
				}
			}
			else if (value !== undefined && value !== null) {
				query += encodeURIComponent(name) + '=' + encodeURIComponent(value) + '&';
			}
		}

		return query.length ? query.substr(0, query.length - 1) : query;
	};

	// Override $http service's default transformRequest
	$httpProvider.defaults.transformRequest = [
		function (data) {
			return angular.isObject(data) && String(data) !== '[object File]' ? param(data) : data;
		}
	];
})

	.run(function ($ionicPlatform) {
		$ionicPlatform.ready(function () {
			// Hide the accessory bar by default (remove this to show the accessory bar above the keyboard
			// for form inputs)
			if (window.cordova && window.cordova.plugins.Keyboard) {
				cordova.plugins.Keyboard.hideKeyboardAccessoryBar(true);
			}
			if (window.StatusBar) {
				StatusBar.styleDefault();
			}
		});
	})


app.controller('MainCtrl', function ($scope, Users, Topics) {

	$scope.header = 'twurlie';
	$scope.topics = Topics.all();

	Users.auth().then(function (user_key) {
		$scope.user_key = user_key;
		Topics.all(user_key).then(function (topics) {
			$scope.topics = topics;
		});
	});

	$scope.openLink = function (link_id) {
		console.info('opening link', link_id);
		navigator.InAppBrowser.open(link_id, '_system', 'location=yes');
	}

})


app.factory('Topics', function ($http) {
	var topics = {};

	return {
		all: function (user_key) {
			console.info('[Topics] all', SERVER);
			return $http.post('http://' + SERVER + '/user/main', {user_key: user_key})
				.then(function (res) {
					console.log('[Topics] all:', res.data);
					topics = res.data;
					return topics;
				}, function (error) {
					console.error('[Topics] all:', error.status);
				})
		},
	};
});


app.factory('Users', function ($http) {
	var authenticated = false;
	var user_key = {};
	var email = 'jacoj82@gmail.com';
	var password = 'foo';

	return {
		auth: function () {
			console.info('[Users] auth', SERVER);
			return $http.post('http://' + SERVER + '/user', {email: email, password: password})
				.then(function (res) {
					// For JSON responses, resp.data contains the result
					console.log('Success', res.data);
					user_key = res.data;
					authenticated = true;
					return user_key;
				}, function (error) {
					console.error('[Users] auth:', error.status);
				})
		},
		key: function () {
			return user_key;
		}
	};
});
