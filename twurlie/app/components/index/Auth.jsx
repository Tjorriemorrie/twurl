import { Reapp, React, NestedViewList, View, Button } from 'reapp-kit';

export default class extends React.Component {
	render() {
		return (
			<View title="twurlie">
				<p>Authenticate</p>
				<Button onTap={() => this.router().transitionTo('index')}>
					Go to index view
				</Button>
			</View>
		);
	}
}
