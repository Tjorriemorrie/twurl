'use strict';

var React = require('react-native');
var {
	TouchableHighlight,
	View,
	Text,
	TextInput,
	} = React;


var s = require('./styles');
var c = require('./config');

var Auth = React.createClass({

	getInitialState: function () {
		var state = {
			email: 'jacoj82@gmail.com',
			password: 'wtf',
			editable: true,
			feedback: '',
		};
		console.info('[Auth] getInitialState:', state);
		return state;
	},

	componentWillUnmount: function () {
		console.info('[Auth] componentWillUnmount');
	},

	render: function () {
		console.info('[Auth] render');
		return (
			<View style={[s.container]}>
				<View>
					<Text>Please log in:</Text>
				</View>
				<View>
					<Text>Email:</Text>
				</View>
				<View>
					<TextInput
						style={[s.inputEmail]}
						autoCapitalize="none"
					    autoCorrect={false}
					    autoFocus={true}
					    editable={this.state.editable}
					    keyboardType="email-address"
					    secureTextEntry={false}
					    onChangeText={(val) => this.setState({'email': val})}
					    value={this.state.email}
						/>
				</View>
				<View>
					<Text>Password:</Text>
				</View>
				<View>
					<TextInput
						style={[s.inputPassword]}
						autoCapitalize="none"
					    autoCorrect={false}
					    autoFocus={false}
					    editable={this.state.editable}
					    keyboardType="default"
					    secureTextEntry={true}
					    onChangeText={(val) => this.setState({'password': val})}
					    value={this.state.password}
						/>
				</View>
				<View style={[s.paragraph]}>
					<Text>{this.state.feedback}</Text>
				</View>
				<TouchableHighlight
					style={[s.btn]}
				    onPress={this.authenticate}
					>
					<Text>Submit</Text>
				</TouchableHighlight>
			</View>
		);
	},

	authenticate: function () {
		console.info('[Auth] authenticate', this.state.email, this.state.password);
		this.setState({editable: false});
		var data = new FormData();
		data.append('email', this.state.email);
		data.append('password', this.state.password);
		fetch(c.host + '/user', {
				method: 'POST',
				body: data,
			})
			.then(c.checkStatus)
			.then(c.parseJSON)
			.then((data) => {
				console.log(data);
				this.props.setAuth(data);
			}).catch((error) => {
				console.warn(error.message);
				this.setState({
					feedback: error.message,
					editable: true,
				});
			})
			.finally(() => {});
	},

});


module.exports = Auth;
