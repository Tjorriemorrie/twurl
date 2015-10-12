'use strict';

var React = require('react-native');
var {
	TouchableHighlight,
	View,
	Text,
} = React;


var s = require('./styles');

var Article = React.createClass({

	render: function () {
		console.info('[Article] render');
		return (
			<View style={s.container}>
				<Text>wtf</Text>
			</View>
		);
	},

});

module.exports = Article;
