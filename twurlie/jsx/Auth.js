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
		fetch(
			c.host + '/user',
			{
				method: 'POST',
				headers: {
					'Accept': 'application/json',
					'Content-Type': 'application/json',
					'Origin': '',
					//'Host': 'api.producthunt.com'
				},
				body: JSON.stringify({
					email: this.state.email,
					password: this.state.password,
				})
			})
			.then((response) => response.text())
			.then((responseText) => {
				console.log(responseText);
				this.props.setAuth(responseText);
			}).catch((error) => {
				console.warn(error);
				this.setState({'feedback': error});
			})
			.finally(() => {
				this.setState({editable: true});
			});
	},

});


module.exports = Auth;
