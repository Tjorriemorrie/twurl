'use strict';

var React = require('react-native');
var {
	TouchableHighlight,
	View,
	Text,
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
		this.loadData();
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
				<View style={s.topicSection}>
					<Text></Text>
				</View>
			</View>
		);
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
				this.setState({
					data: data,
					message: 'Done and done',
				});
			}).catch((error) => {
				console.warn(error);
				this.setState({message: error});
			})
			.finally(() => {});
	},

});

module.exports = Main;
