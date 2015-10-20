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
var Moment = require('moment');

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
							{this.renderLink(key, val)}
						</View>
					);
				}.bind(this))}
			</View>;
		}
	},

	renderLink: function (topic, link) {
		console.info('[Main] renderLink', topic, link);
		if (link) {
			return <View style={s.linkBox}>
				<View style={s.linkUrlView}>
					<Text style={s.linkUrlText}>URL: {link.link_id}</Text>
				</View>
				<TouchableHighlight style={s.linkUrlView} onPress={this.read.bind(this, topic, link)}>
					<Text style={s.linkUrlText}>Read now!</Text>
				</TouchableHighlight>
				<View style={s.linkPriorityView}>
					<Text style={s.linkPriorityText}>Priority: {link.priority}</Text>
				</View>
				<View style={s.linkReadAtView}>
					<Text style={s.linkReadAtText}>Read at: {link.read_at}</Text>
				</View>
				<View style={s.linkTweetedCountView}>
					<Text style={s.linkTweetedCountText}>Tweeted: {link.tweeted_count}</Text>
				</View>
			</View>;
		}
		else {
			return <View style={s.linkBox}>
				<Text>No link; please wait a day</Text>
			</View>;
		}
	},

	read: function (topic, link) {
		console.info('[Main] read topic', topic);
		console.info('[Main] read link_id', link.link_id);
		this.props.nav.push({scene: 'read', topic: topic, link_id: link.link_id});

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
				var data = JSON.parse(user_data);
				this.setState({
					data: data,
					message: 'You have ' + Object.keys(data).length + ' topics',
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
