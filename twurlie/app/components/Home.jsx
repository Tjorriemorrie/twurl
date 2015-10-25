import { Reapp, React, NestedViewList, View, Button } from 'reapp-kit';

export default class extends React.Component {
	render() {
		return (
			<View {...this.props} title="Sub Route" titleLeft={backButton}>
				<p>Hello, Woo!</p>

				<Button onTap={() => this.router().transitionTo('sub')}>
					Go to sub view
				</Button>
			</View>
		);
	}
}
