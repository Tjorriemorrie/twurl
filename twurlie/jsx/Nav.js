'use strict';

var React = require('react-native');
var {
	Text,
	View,
	Navigator,
	AsyncStorage,
	TouchableHighlight,
	} = React;


var s = require('./styles');
var c = require('./config');
var Auth = require('./Auth');
var Main = require('./Main');
var Read = require('./Read');
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
					<TouchableHighlight style={s.btn} onPress={this.setAuth.bind(this, null)}>
						<Text>log out</Text>
					</TouchableHighlight>
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
				return <Read nav={nav} user_key={this.state.user_key} topic={route.topic} link_id={route.link_id}/>;
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
			auth: !!key,
			user_key: key,
		});
		if (!key) {
			console.warn('No key provided, clearing storage!');
			AsyncStorage.clear();
		}
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
