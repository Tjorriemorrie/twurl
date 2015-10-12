'use strict';

var React = require('react-native');
var {
	TouchableHighlight,
	View,
	Text,
} = React;


var s = require('./styles');

var History = React.createClass({

	render: function () {
		console.info('[History] render');
		return (
			<View style={s.container}>
				<Text>history</Text>
				<Text>history</Text>
				<Text>history</Text>
			</View>
		);
	},

});


module.exports = History;
