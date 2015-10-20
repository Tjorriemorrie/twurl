var React = require('react');

//Custom Formatter component
var PercentageFormatter = React.createClass({
    render: function () {
        return (
            <span>{Math.round(this.props.value * 100) + '%'}</span>
        );
    }
});

module.exports = PercentageFormatter;
