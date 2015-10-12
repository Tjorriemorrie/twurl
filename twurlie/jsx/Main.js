'use strict';

var React = require('react-native');
var {
	TouchableHighlight,
	View,
	Text,
} = React;


var s = require('./styles');

var Main = React.createClass({

	getInitialState: function () {
		var state = {
			data: {},
		};
		console.info('[Main] getInitialState:', state);
		return state;
	},

	componentDidMount: function () {
		console.info('[Main] componentDidMount');

	},

	render: function () {
		console.info('[Main] render');
		return (
			<View style={s.container}>
				<View style={s.topicSection}>
					<Text></Text>
				</View>
			</View>
		);
	},

});

module.exports = Main;
