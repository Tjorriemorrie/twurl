var React = require('react');

var Factoid = React.createClass({

    getInitialState: function () {
        return {
            'ordering': [
                'is_parsed',
                'is_songs_named',
                'is_songs_tracked',
                'is_songs_artist',
                'is_songs_album',
                'is_albums_sized',
//                'is_albums_complete',
//                'is_logged_in',
            ],
            'is_parsed': false,
            'is_songs_named': false,
            'is_songs_tracked': false,
            'is_songs_artist': false,
            'is_songs_album': false,
            'is_albums_sized': false,
            'is_albums_complete': false,
            'is_logged_in': false,
        };
    },

    componentDidMount: function () {
        console.info('[Factoid] componentDidMount');
//        React.findDOMNode(this.refs.focusOnMe).focus();
        this.loadFactoid();
    },

//    componentDidUpdate: function (prevProps, prevState) {
//        console.info('[Factoid] componentDidUpdate');
//    },

    loadFactoid: function () {
        console.info('[Factoid] loadFactoid');

        if (this.state.ordering.length > 0) {
            $.getJSON('/factoid/' + this.state.ordering[0])
                .done(function (data) {
                    var new_state = {};
                    if (data === true) {
                        new_state[this.state.ordering[0]] = true;
                        new_state['ordering'] = this.state.ordering;
                        new_state['ordering'].shift();
                        setTimeout(function () {
                            this.loadFactoid();
                        }.bind(this), 1000);
                    } else {
                        new_state[this.state.ordering[0]] = data;
                    }
                    this.setState(new_state);
                }.bind(this))
                .fail(function (data, status, headers, config) {
                    alert('Error loading factoid');
                    console.error('[Factoid] loadFactoid: error', data);
                }.bind(this));
        }
    },

    submitSong: function (e) {
        console.info('[Factoid] submitSong');
        e.preventDefault();
        var form = React.findDOMNode(this.refs.formSong);
        console.info('[Factoid] submitSong form', form);
        this.sendFactoid(form, '/set/songs');
    },

    submitAlbum: function (e) {
        console.info('[Factoid] submitAlbum');
        e.preventDefault();
        var form = React.findDOMNode(this.refs.formAlbum);
        console.info('[Factoid] submitAlbum form', form);
        this.sendFactoid(form, '/set/albums');
    },

    sendFactoid: function (form, url) {
        console.info('[Factoid] sendFactoid');

        // remove factoid during submit
        var new_state = {};
        new_state[this.state.ordering[0]] = false;
        this.setState(new_state);

        // submit form
        $.post(url, $(form).serialize())
            .done(function (res) {
                console.info('[Factoid] sendFactoid res', res);
            }.bind(this))
            .fail(function (data, status, headers, config) {
                console.error('[Factoid] loadFactoid: error', data);
                alert('Error sendFactoid');
            }.bind(this))
            .always(function () {
                console.info('[Factoid] sendFactoid: always');
                this.loadFactoid();
            }.bind(this));
    },

    render: function () {
        console.info('[Factoid] render');
        var msg = null;

        if (typeof(this.state.is_parsed) != 'boolean') {
            msg = 'You have ' + this.state.is_parsed.count + ' unparsed songs';
        }

        else if (typeof(this.state.is_songs_named) != 'boolean') {
            msg = <form ref="formSong" className="form" onSubmit={this.submitSong}>
                <dl>
                    <dt>What is the name of this song?</dt>
                    <dd><span>{this.state.is_songs_named.path_name}</span></dd>
                    <dd><small classNames="text-muted">{this.state.is_songs_named.web_path}</small></dd>
                </dl>
                <input type="hidden" name="song" value={this.state.is_songs_named.id} />
                <input type="text" name="name" className="form-control input-sm" required autoFocus autoComplete="off" />
                <button type="submit" className="btn btn-default btn-sm">Submit</button>
            </form>
        }

        else if (typeof(this.state.is_songs_tracked) != 'boolean') {
            msg = <form ref="formSong" className="form" onSubmit={this.submitSong}>
                <dl>
                    <dt>What is the track of this song?</dt>
                    <dd><span>{this.state.is_songs_tracked.path_name}</span></dd>
                    <dd><small classNames="text-muted">{this.state.is_songs_tracked.web_path}</small></dd>
                </dl>
                <input type="hidden" name="id" value={this.state.is_songs_tracked.id} />
                <input type="number" name="song_track_number" className="form-control input-sm" required autoFocus autoComplete="off" />
                <button type="submit" className="btn btn-default btn-sm">Submit</button>
            </form>
        }

        else if (typeof(this.state.is_songs_artist) != 'boolean') {
            msg = <form ref="formSong" className="form" onSubmit={this.submitSong}>
                <dl>
                    <dt>Who is the artist of this song?</dt>
                    <dd>{this.state.is_songs_artist.name}</dd>
                    <dd><small className="text-muted">{this.state.is_songs_artist.web_path}</small></dd>
                </dl>
                <input type="hidden" name="id" value={this.state.is_songs_artist.id} />
                <input type="text" className="form-control input-sm" name="artist.name" required autoFocus autoComplete="off" />
                <button type="submit" className="btn btn-default btn-sm">Submit</button>
            </form>
        }

        else if (typeof(this.state.is_songs_album) != 'boolean') {
            msg = <form ref="formSong" className="form" onSubmit={this.submitSong}>
                <dl>
                    <dt>What is the album of this song?</dt>
                    <dd>{this.state.is_songs_album.name}</dd>
                    <dd><small className="text-muted">{this.state.is_songs_album.web_path}</small></dd>
                </dl>
                <input type="hidden" name="id" value={this.state.is_songs_album.id} />
                <input type="text" className="form-control input-sm" name="album.name" required autoFocus autoComplete="off" />
                <button type="submit" className="btn btn-default btn-sm">Submit</button>
            </form>
        }

        else if (typeof(this.state.is_albums_sized) != 'boolean') {
            msg = <form ref="formAlbum" className="form" onSubmit={this.submitAlbum}>
                <dl>
                    <dt>How many tracks does this album have?</dt>
                    <dd><span>{this.state.is_albums_sized.name}</span></dd>
                    <dd>~ {this.state.is_albums_sized.artist.name}</dd>
                </dl>
                <input type="hidden" name="id" value={this.state.is_albums_sized.id} />
                <input type="number" name="total_tracks" className="form-control input-sm" required autoFocus autoComplete="off" />
                <button type="submit" className="btn btn-default btn-sm">Submit</button>
            </form>
        }

        else if (typeof(this.state.is_albums_complete) != 'boolean') {
            msg = <form ref="formAlbumsSize" className="form" onSubmit={this.submitAlbumsSized}>
                <input type="hidden" name="album_id" value={this.state.is_albums_complete.album.id} />
                <h4>This album has missing tracks!</h4>
                <dl>
                    <dt>Tracks set on the album currently is <strong>{this.state.is_albums_complete.album.total_tracks}</strong></dt>
                    <dd><span>{this.state.is_albums_complete.album.name}</span></dd>
                    <dd>~ {this.state.is_albums_complete.album.artist.name}</dd>
                </dl>
                <input type="number" className="form-control input-sm" id="album_size" name="total_tracks" required autoFocus />
                <button type="submit" className="btn btn-default btn-sm">Submit</button>
                <hr/>
                <dl>
                    <dt>{this.state.is_albums_complete.songs.length} songs that belong to the album:</dt>
                    {this.state.is_albums_complete.songs.map(function (song) {
                        return <dd>{song.track_number} {song.name}</dd>;
                    })}
                </dl>
            </form>
        }

        else if (typeof(this.state.is_logged_in) != 'boolean') {
            msg = 'You are not logged into Last.fm';
        }

        if (msg) {
            return (
                <div className="alert alert-default">{msg}</div>
            );
        } else {
            return <span/>;
        }
    }
});

module.exports = Factoid;