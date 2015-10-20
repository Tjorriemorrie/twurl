var React = require('react');


var Library = React.createClass({

    getInitialState: function () {
        console.info('[Library] getInitialState');
        return {
            'isScanning': false,
            'grouping': null,
            'rows': []
        };
    },

    componentDidMount: function () {
        console.info('[Library] componentDidMount');
    },

    onTabSelect: function (grouping) {
        console.info('[Library] onTabSelect: ', grouping);
        this.loadLibrarySongs(grouping);
    },

    scanDirectory: function () {
        console.info('[Library] scandir');
        if (this.state.isScanning) {
            alert('Scanning in progress');
        } else {
            this.setState({'isScanning': true});
            $.getJSON('/scan/dir')
                .done(function () {
                    console.info('[Library] scanDirectory: done');
                }.bind(this))
                .always(function (data) {
                    this.setState({'isScanning': false});
                    if (data['parsed'] >= 50) {
                        this.scanDirectory();
                    }
                }.bind(this));
        }
    },

    loadLibrarySongs: function (grouping) {
        console.info('[Library] loadLibrarySongs: grouping = ', grouping);
        $.getJSON('/find/' + grouping)
            .done(function (data) {
                console.info('[Library] loadLibrarySongs done');
                this.setState({
                    'grouping': grouping,
                    'rows': data
                });
            }.bind(this));
    },

    formatPercentage: function (v) {
        return Math.round(v * 100) + '%';
    },

    updateRow: function (row, key, val) {
        console.info('[Library] updateRow', row, key, val);

        var params = {'id': row.id};
        params[key] = val;

        // submit form
        $.post('/set/' + this.props.grouping, params)
            .done(function (res) {
                console.info('[Library] updateRow: done', res);
            }.bind(this))
            .fail(function (data, status, headers, config) {
                console.error('[Library] updateRow: error', data);
                alert('Error [Library] updateRow');
            }.bind(this))
            .always(function () {
                console.info('[Library] updateRow: always');
                this.loadLibrarySongs(this.props.grouping);
            }.bind(this));
    },

    getGrid: function () {
        console.info('[Library] getGrid');

        if (this.state.grouping == 'artists') {
            return <div>
                <h4>Artists</h4>
                <SmallGrid
                    rows={this.state.rows}
                    cols={[
                        {'key': 'rating', 'name': 'Rating', 'format': this.formatPercentage},
                        {'key': 'name', 'name': 'Title', 'edit': this.updateRow},
                        {'key': 'count_albums', 'name': 'Albums'},
                        {'key': 'count_songs', 'name': 'Songs'},
                    ]}
                />
            </div>;
        }

        else if (this.state.grouping == 'albums') {
            return <div>
                <h4>Albums</h4>
                <SmallGrid
                    rows={this.state.rows}
                    cols={[
                        {'key': 'rating', 'name': 'Rating', 'format': this.formatPercentage},
                        {'key': 'name', 'name': 'Title', 'edit': this.updateRow},
                        {'key': 'artist.name', 'name': 'Artist'},
                        {'key': 'count_songs', 'name': 'Songs'},
                    ]}
                />
            </div>;
        }

        else if (this.state.grouping == 'songs') {
            return <div>
                <h4>Songs</h4>
                <SmallGrid
                    rows={this.state.rows}
                    cols={[
                        {'key': 'rating', 'name': 'Rating', 'format': this.formatPercentage},
                        {'key': 'name', 'name': 'Title', 'edit': this.updateRow},
                        {'key': 'artist.name', 'name': 'Artist', 'edit': this.updateRow},
                        {'key': 'album.name', 'name': 'Album', 'edit': this.updateRow},
                        {'key': 'track_number', 'name': 'Track', 'edit': this.updateRow},
                    ]}
                />
            </div>;
        }
    },

    render: function () {
        console.info('[Library] render');

        var smallGrid = this.getGrid();

        return (
            <div className="row">
                <h3>
                    <button className="btn btn-default btn-sm pull-right" onClick={this.scanDirectory}>{this.state.isScanning ? 'Scanning...' : 'Refresh'}</button>
                    Library
                </h3>

                <div className="btn-group" data-toggle="buttons">
                    <label className="btn btn-default">
                        <input type="radio" autoComplete="off" onClick={this.onTabSelect.bind(this, 'artists')} /> Artists
                    </label>
                    <label className="btn btn-default">
                        <input type="radio" autoComplete="off" onClick={this.onTabSelect.bind(this, 'albums')} /> Albums
                    </label>
                    <label className="btn btn-default">
                        <input type="radio" autoComplete="off" onClick={this.onTabSelect.bind(this, 'songs')} /> Songs
                    </label>
                </div>

                {smallGrid}
            </div>
        );
    }
});

module.exports = Library;