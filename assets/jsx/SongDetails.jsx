var React = require('react');


var SongDetails = React.createClass({
    render: function () {
        return (
            <span>
                <strong>
                    <small className="text-muted">{this.props.song.track_number} </small>
                    <span title={this.props.song.id}> {this.props.song.name}</span>
                </strong>
                <br/><small>
                    <span>{(this.props.song.artist) ? this.props.song.artist.name : 'no artist'}</span>
                    <br/><em><small className="text-muted">{(this.props.song.album) ? this.props.song.album.year : ''}</small> {(this.props.song.album) ? this.props.song.album.name : 'no album'}</em>
                </small>
            </span>
        );
    }
});


module.exports = SongDetails;