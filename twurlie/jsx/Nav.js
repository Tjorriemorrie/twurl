'use strict';

var React = require('react-native');
var {
	Text,
	View,
	Navigator,
	AsyncStorage,
	} = React;


var s = require('./styles');
var c = require('./config');
var Auth = require('./Auth');
var Main = require('./Main');
var Article = require('./Article');
var History = require('./History');

var Nav = React.createClass({

	getInitialState: function () {
		var state = {
			auth: false,
			user_key: null,
		};
		console.info('[Nav] getInitialState:', state);
		return state;
	},

	componentDidMount: function () {
		console.info('[Nav] componentDidMount');
		this._loadInitialState().done();
	},

	componentWillUnmount: function () {
		console.info('[Nav] componentWillUnmount');
	},

	render: function () {
		console.info('[Nav] render');
		return (
			<View style={[s.container]}>
				<View style={[s.toolbar]}>
					<Text>twurlie</Text>
				</View>
				<Navigator
					initialRoute={{scene: 'main'}}
					renderScene={this.renderScene}
					/>
			</View>
		);
	},

	renderScene: function (route, nav) {
		console.info('[Nav] renderScene: route');

		if (!this.state.auth) {
			console.info('[Nav] renderScene: unauthorized');
			return <Auth nav={nav} setAuth={this.setAuth}/>;
		}
		else {

			if (route.scene == 'main') {
				console.info('[Nav] renderScene: main');
				return <Main nav={nav} user_key={this.state.user_key}/>;
			}
			else if (route.scene == 'read') {
				console.info('[Nav] renderScene: read', route.link_id);

			}
			else {
				console.error('[Nav] renderScene: unknown route!', route);
			}
		}
	},

	setAuth: function (key) {
		console.info('[Nav] setAuth:', key);
		this._onAuth(key);
		this.setState({
			auth: true,
			user_key: key,
		});
	},

	// Async Storage

	async _loadInitialState() {
		console.info('[Nav] _loadInitialState');
		try {
			var user_key = await AsyncStorage.getItem(c.storage_user_key);
			if (user_key !== null) {
				this.setState({
					auth: true,
					user_key: user_key,
				});
			}
		}
		catch (error) {
			console.error('AsyncStorage error: ' + error.message);
		}
	},

	async _onAuth(user_key) {
		console.info('[Nav] _onAuth', user_key);
		try {
			await AsyncStorage.setItem(c.storage_user_key, user_key);
		}
		catch (error) {
			console.error('AsyncStorage error: ' + error.message);
		}
	},

});

module.exports = Nav;
