'use strict';

var config = {

	host: 'http://10.0.2.2:9999',
	//'host': 'https://twurlie-1091.appspot.com',
	storage_user_email: 'twurlie_user_email',
	storage_user_key: 'twurlie_user_key',
	storage_user_data: 'twurlie_user_data',

	checkStatus: function (response) {
		//console.debug(response.headers);
		console.debug(response.status);
		if (response.status >= 200 && response.status < 300) {
			return response;
		}
		else if (response.status >= 403) {
			throw new Error('You are not authorised');
		}
		else if (response.status >= 500) {
			throw new Error('Internal error occurred, please try again later');
		}
		else if (response.status == 404) {
			throw new Error(response.status + ': not found');
		}
		else {
			throw new Error(response.status + ': an error occurred');
		}
	},

	parseJSON: function (response) {
		return response.json();
	},

	mapObject: function (obj, callback) {
		return Object.keys(obj).map(function (key) {
			return callback(key, obj[key]);
		});
	},

};

module.exports = config;
