import { Reapp, React, NestedViewList, View, Button } from 'reapp-kit';

class Index extends React.Component {
	render() {
		return (
			<NestedViewList {...this.props.viewListProps}>
				<View title="twurlie">
					<p>Index</p>
					<Button onTap={() => this.router().transitionTo('auth')}>
						Go to auth view
					</Button>
				</View>
			</NestedViewList>
		);
	}
}

export default Reapp(Index);

/*
 This is your root route. When you wrap it with Reapp()
 it passes your class two properties:

 - viewListProps: Passes the scrollToStep to your ViewList so it animates
 - child: The child route
 */