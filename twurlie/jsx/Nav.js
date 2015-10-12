'use strict';

var React = require('react-native');
var {
	Text,
	View,
	Navigator,
	} = React;


var s = require('./styles');
var Auth = require('./Auth');
var MAin = require('./Main');
var Article = require('./Article');
var History = require('./History');

var Nav = React.createClass({

	getInitialState: function () {
		var state = {
			auth: null,
			user_key: null,
		};
		console.info('[Nav] getInitialState:', state);
		return state;
	},

	render: function () {
		console.info('[Nav] render');
		return (
			<View style={[s.container]}>
				<View style={[s.toolbar]}>
					<Text>twurlie</Text>
				</View>
				<Navigator
					initialRoute={{idx: 0, title: 'topics'}}
					renderScene={this.renderScene}
					/>
			</View>
		);
	},

	renderScene: function (route, nav) {
		console.info('[Nav] renderScene: route [', route.idx, '] ', route.title);

		if (!this.state.auth) {
			console.info('[Nav] renderScene: unauthorized');
			return <Auth nav={nav} setAuth={this.setAuth}/>;
		}
		else {

			if (route.idx == 0) {
				console.info('[Nav] renderScene: main');
				return <Main nav={nav} user_key={this.state.user_key}/>;
			}
			else {
				console.error('[Nav] renderScene: unknown route!', route);
			}
		}
	},

	setAuth: function (key) {
		console.info('[Nav] setAuth:', key);
		this.setState({
			auth: true,
			user_key: key,
		});
	},

});

module.exports = Nav;
