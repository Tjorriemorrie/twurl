'use strict';

var React = require('react-native');
var {
	StyleSheet,
	PixelRatio,
	} = React;


var styles = StyleSheet.create({

	container: {
		flex: 1,
	},

	center: {
		flex: 1,
		justifyContent: 'center',
		alignItems: 'center',
	},

	paragraph: {
		height: 40,
	},


	topicView: {
		backgroundColor: '#eeeeee',
	},
	topicText: {
		fontWeight: 'bold',
	},
	linkBox: {

	},
	linkUrlView: {},
	linkUrlText: {},
	linkPriorityView: {},
	linkPriorityText: {},
	linkReadAtView: {},
	linkRatedAtText: {},
	linkTweetedCountView: {},
	linkTweetedCountText: {},


	load: {
		color: 'white',
		fontWeight: 'bold',
		backgroundColor: 'rgba(0, 0, 0, 0.67)',
	},

	toolbar: {
		backgroundColor: 'blue',
		height: 60,
		borderWidth: 10,
		borderColor: 'purple',
	},


	inputEmail: {
		borderWidth: 1,
		borderColor: 'black',
	},
	inputPassword: {
		borderWidth: 1,
		borderColor: 'black',
	},


	btn: {
		backgroundColor: 'rgba(0, 0, 0, 0.1)',
		height: 50,
		width: 200,
		borderWidth: 1,
		borderColor: 'black',
	}

});

module.exports = styles;
