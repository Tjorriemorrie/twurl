'use strict';

var React = require('react-native');
var {
	TouchableHighlight,
	View,
	Text,
	AsyncStorage,
} = React;


var s = require('./styles');
var c = require('./config');

var Main = React.createClass({

	getInitialState: function () {
		var state = {
			message: 'Loading...',
			data: {},
		};
		console.info('[Main] getInitialState:', state);
		return state;
	},

	componentDidMount: function () {
		console.info('[Main] componentDidMount');
		this._loadData().done();
	},

	componentWillUnmount: function () {
		console.info('[Main] componentWillUnmount');
	},

	render: function () {
		console.info('[Main] render');
		return (
			<View style={s.container}>
				<View>
					<Text>{this.state.message}</Text>
				</View>
				{this.renderTopics()}
			</View>
		);
	},

	renderTopics: function () {
		console.info('[Main] renderTopics');
		if (this.state.data) {
			return <View>
				{c.mapObject(this.state.data, function(key, val) {
					return (
						<View style={s.topicView} key={key}>
							<Text style={s.topicText}>{key}</Text>
							{this.renderLink(val)}
						</View>
					);
				}.bind(this))}
			</View>;
		}
	},

	renderLink: function (link) {
		console.info('[Main] renderLink');
		if (link) {
			return <View style={s.linkBox}>
				<View style={s.linkUrlView}>
					<Text style={s.linkUrlText}>{link.link_id}</Text>
				</View>
				<View style={s.linkPriorityView}>
					<Text style={s.linkPriorityText}>{link.priority}</Text>
				</View>
				<View style={s.linkReadAtView}>
					<Text style={s.linkReadAtText}>{link.read_at}</Text>
				</View>
				<View style={s.linkTweetedCountView}>
					<Text style={s.linkTweetedCountText}>{link.tweeted_count}</Text>
				</View>
			</View>;
		}
	},

	loadData: function () {
		console.info('[Main] loadData for ', this.props.user_key);
		var data = new FormData();
		data.append('user_key', this.props.user_key);
		fetch(c.host + '/user/main', {
				method: 'POST',
				body: data,
			})
			.then(c.checkStatus)
			.then(c.parseJSON)
			.then((data) => {
				console.log(data);
				this._saveData(data);
				this.setState({
					data: data,
					message: 'You have ' + Object.keys(data).length + ' topics',
				});
			}).catch((error) => {
				console.warn(error);
				this.setState({message: error});
			})
			.finally(() => {});
	},

	// Async Storage

	async _loadData() {
		console.info('[Main] _loadData');
		try {
			var user_data = await AsyncStorage.getItem(c.storage_user_data);
			if (user_data !== null) {
				console.info('[Main] _loadData: data found!');
				this.setState({
					data: JSON.parse(user_data),
				});
			}
			else {
				console.info('[Main] _loadData: no data found, loading...');
				this.loadData();
			}
		}
		catch (error) {
			console.error('AsyncStorage error: ' + error.message);
		}
	},

	async _saveData(user_data) {
		console.info('[Main] _saveData', user_data);
		try {
			await AsyncStorage.setItem(c.storage_user_data, JSON.stringify(user_data));
		}
		catch (error) {
			console.error('AsyncStorage error: ' + error.message);
		}
	},

});

module.exports = Main;
