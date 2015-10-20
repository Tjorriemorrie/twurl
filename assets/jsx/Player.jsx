var React = require('react');
var SongDetails = require('./SongDetails.jsx');


var Player = React.createClass({
    audio_tag: null,
    getInitialState: function () {
        console.info('[Player] getInitialState...');
        return {
            'queue': [],
            'histories': [],
            'selections': [],
            'current': ""
        };
    },
    componentDidMount: function () {
        console.info('[Player] componentDidMount...');
        this.audio_tag = React.findDOMNode(this.refs.audio_tag);
        this.audio_tag.addEventListener('ended', this.onEnded);
        console.info('[Player] audio_tag event listener added for ended');
        this.audio_tag.volume = 0.75;
        console.info('[Player] audio_tag volume set to 75%');
        this.loadQueue();
    },
    notifyPing: function () {
        console.info('Notifying ping...');
        if (this.state.selections.length < 1) {
            return false;
        }
        if (this.state.queue.length >= 4) {
            return false;
        }
        var audio_ping = new Audio('/static/sounds/ping.mp3');
        audio_ping.play();
    },
    loadQueue: function () {
        console.info('[Player] loadQueue...');
        return $.get('/load/queue')
            .success(function (data, status, headers, config) {
                console.info('[Player] loadQueue: ', data.length, data[0]);
                this.setState({'queue': data});
                this.playNext();
                this.getSelections();
                this.loadHistories();
            }.bind(this))
            .error(function (data, status, headers, config) {
                alert('Error retrieving files');
                console.error('[Player] loadQueue: error', data);
            }.bind(this));
    },
    loadHistories: function () {
        console.info('[Player] loadHistories...');
        return $.get('/load/histories')
            .success(function (data, status, headers, config) {
                console.info('[Player] loadHistories: ', data.length, data[0]);
                this.setState({'histories': data});
            }.bind(this))
            .error(function (data, status, headers, config) {
                alert('Error retrieving files');
                console.error('[Player] loadHistories: error', data);
            }.bind(this));
    },
    getSelections: function () {
        console.info('[Player] getSelection...');
        if (this.state.selections.length > 0) {
            console.info('[Player] getSelection: Already have selections');
            return;
        }
        if (this.state.queue.length > 4) {
            console.info('[Player] getSelection: Already have enough songs in queue');
            return;
        }
        $.get('/selection')
            .success(function (data, status, headers, config) {
                console.info('[Player] getSelection: success', data.length, data[0]);
                this.setState({"selections": data});
            }.bind(this))
            .error(function (data, status, headers, config) {
                alert('Error retrieving selection files');
                console.error('[Player] getSelection: error', data);
            }.bind(this));
    },
    setSelection: function (song) {
        console.info('[Player] setSelection...');

        // remove from selection
        var selections = this.state.selections;
        var selection = selections.shift();
        this.setState({"selections": selections});
        console.info('[Player] setSelection: removed from selections', this.state.selections.length);

        // update backend
        var losers = [];
        selection.forEach(function (loser) {
            losers.push(loser.id);
        });
        $.post('/add/queue', {'winner': song.id, 'losers': losers})
            .success(function (data, status, headers, config) {
                this.loadQueue();
            }.bind(this))
            .error(function (data, status, headers, config) {
                alert('Error updating selection');
                console.error('[Player] setSelection: error', data);
            }.bind(this));
    },
    playNext: function () {
        console.info('[Player] playNext...');

        // empty queue?
        if (this.state.queue.length < 1) {
            console.warn('[Player] playNext: queue empty');
            return;
        }

        // already playing?
        if (this.state.current != "") {
            console.warn('[Player] playNext: already playing');
            return;
        }

        var queue_first = this.state.queue[0];
        console.info('[Player] playNext:', queue_first);
        this.setState({"current": queue_first.src});
        this.audio_tag.play();
        document.title = queue_first.song.name + ' ~' + queue_first.song.artist.name;
        this.notifyPing();
    },
    onEnded: function () {
        console.info('[Player] onEnded...');
        this.setState({"current": ""});
        document.title = "speler";

        // update backend
        $.post('/ended', {'id': this.state.queue[0].id})
            .success(function (data, status, headers, config) {
                this.loadQueue();
            }.bind(this))
            .error(function (data, status, headers, config) {
                alert('Error updating selection');
                console.error('[Player] setSelection: error', data);
            }.bind(this));
    },
    render: function () {
        console.info('[Player] render...');
        return (
            <div className="row">
                <div className="col-sm-11">
                    <div>
                        <audio ref="audio_tag" src={this.state.current} controls/>
                        {(this.state.queue.length)
                            ? <a onClick={this.onEnded} href="#" className="audio_next">&#10940;</a>
                            : ''
                        }
                    </div>

                    {(!this.state.selections.length)
                        ? ''
                        : (
                            <div>
                                <h5>Choose next song to add to playlist:</h5>
                                <div className="btn-group btn-group-vertical">
                                    {this.state.selections[0].map(function (selection) {
                                        return (
                                            <a key={selection.id} onClick={this.setSelection.bind(this, selection)} className="btn btn-default" type="button">
                                                <small><SongDetails song={selection}/></small>
                                            </a>
                                        );
                                    }.bind(this))}
                                </div>
                            </div>
                        )
                    }

                    <div>
                        <h5>Playlist:</h5>
                        <ol>
                            {this.state.queue.map(function (queue, index) {
                                return (
                                    <li key={queue.id} className={(index < 1) ? 'current_song' : ''}><SongDetails song={queue.song}/></li>
                                );
                            })}
                        </ol>
                    </div>

                    <div>
                        <h5>Recently Played:</h5>
                        {(!this.state.histories.length)
                            ? <p>no songs played recently</p>
                            : (
                                <ol>
                                    {this.state.histories.map(function (history) {
                                        return (
                                            <li key={history.id}>
                                                <SongDetails song={history.song}/>
                                            </li>
                                        );
                                    })}
                                </ol>
                            )
                        }
                    </div>
                </div>
            </div>
        );
    }
});

module.exports = Player;
