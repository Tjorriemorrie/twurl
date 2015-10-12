/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 */
'use strict';

var React = require('react-native');
var {
	AppRegistry,
	StyleSheet,
	Text,
	View,
	} = React;


var Nav = require('./jsx/Nav');

var twurlie = React.createClass({
	render: function () {
		return (
			<Nav/>
		);
	}
});

AppRegistry.registerComponent('twurlie', () => twurlie);
