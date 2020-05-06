# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import ArtistForm, VenueForm, ShowForm
from config import SQLALCHEMY_DATABASE_URI
from flask_migrate import Migrate
from datetime import datetime

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# connects to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

STATES = ['AL','AK','AZ','AR','CA','CO','CT','DE','DC','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','MD','MA','MI','MN','MS','MO','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(120), unique=True)
    image_link = db.Column(db.String(500))
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120), unique=True)
    shows = db.relationship('Show', backref='Venue', lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120), unique=True)
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), unique=True)
    shows = db.relationship('Show', backref='Artist', lazy=True)


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column('start_time', db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    for venue in Venue.query.with_entities(Venue.city, Venue.state).order_by(Venue.state).distinct():
        venueMetaData = {
            "city": venue[0],
            "state": venue[1],
        }
        tempVenues = []
        for fullVenue in Venue.query.filter_by(city=venue[0], state=venue[1]).all():
            tempVenue = {
                "id": fullVenue.id,
                "name": fullVenue.name,
            }
            for show in fullVenue.shows:
                counter = 0
                if(show.start_time > datetime.now()):
                    counter += 1
                tempVenue['num_upcoming_shows'] = counter
            tempVenues.append(tempVenue)
        venueMetaData['venues'] = tempVenues
        print(venueMetaData)
        data.append(venueMetaData)
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    searchTerm = request.form.get('search_term', '')
    search = "%{}%".format(searchTerm)
    venues = Venue.query.filter(Venue.name.ilike(search)).all()

    counter = 0
    data = {
        "count": len(venues),
        "data": []
    }
    for venue in venues:
        for show in venue.shows:
            counter = 0
            if(show.start_time > datetime.now()):
                counter += 1
        tempData = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": counter
        }
        data["data"].append(tempData)
    
    return render_template('pages/search_venues.html', results=data, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    specificVenue = Venue.query.get(venue_id)
    
    data = {
        "id": venue_id,
        "name": specificVenue.name,
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": specificVenue.address,
        "city": specificVenue.city,
        "state": specificVenue.state,
        "phone": specificVenue.phone,
        "website": "https://www.themusicalhop.com",
        "facebook_link": specificVenue.facebook_link,
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": specificVenue.image_link,
        "upcoming_shows_count": 0,
        "upcoming_shows": [],
        "past_shows": []
    }

    counter = 0
    for show in specificVenue.shows:
        artist = Artist.query.get(show.artist_id)
        if(show.start_time > datetime.now()):
            data["upcoming_shows"].append({
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time
            })
            counter += 1
        else:
            data["past_shows"].append({
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time
            })
        data['upcoming_shows_count'] = counter
    
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    req = request.form
    if req['state'] not in STATES:
        abort(422)
    try:
        venue = Venue(name=req['name'],
                    city=req['city'],
                    state=req['state'],
                    address=req['address'],
                    phone=req['phone'],
                    genres=req['genres'],
                    facebook_link=req['facebook_link'],
                    image_link='https://via.placeholder.com/335x500.png')
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + req['name'] + ' was successfully listed!')
    except Exception:
        flash('An error occurred. Venue ' + req['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except Exception:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify({'success': True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = []
    for artist in Artist.query.all():
        singleArtist = {
            "id": artist.id,
            "name": artist.name
        }
        data.append(singleArtist)

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    searchTerm = request.form.get('search_term', '')
    search = "%{}%".format(searchTerm)
    artists = Artist.query.filter(Artist.name.ilike(search)).all()

    counter = 0
    data = {
        "count": len(artists),
        "data": []
    }
    for artist in artists:
        for show in artist.shows:
            counter = 0
            if(show.start_time > datetime.now()):
                counter += 1
        tempData = {
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": counter
        }
        data["data"].append(tempData)
    return render_template('pages/search_artists.html', results=data, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    specificArtist = Artist.query.get(artist_id)
   
    data = {
        "id": artist_id,
        "name": specificArtist.name,
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "city": specificArtist.city,
        "state": specificArtist.state,
        "phone": specificArtist.phone,
        "website": "https://www.themusicalhop.com",
        "facebook_link": specificArtist.facebook_link,
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": specificArtist.image_link,
        "upcoming_shows_count": 0,
        "upcoming_shows": [],
        "past_shows": []
    }

    counter = 0
    for show in specificArtist.shows:
        venue = Venue.query.get(show.venue_id)
        if(show.start_time > datetime.now()):
            data["upcoming_shows"].append({
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": show.start_time
            })
            counter += 1
        else:
            data["past_shows"].append({
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": show.start_time
            })
        data['upcoming_shows_count'] = counter

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    specificArtist = Artist.query.get(artist_id)

    artist = {
      "id": artist_id,
      "name": specificArtist.name,
      "genres": specificArtist.genres,
      "city": specificArtist.city,
      "state": specificArtist.state,
      "phone": specificArtist.phone,
      "website": "https://www.themusicalhop.com",
      "facebook_link": specificArtist.facebook_link,
      "seeking_talent": True,
      "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
      "image_link": specificArtist.image_link
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    req = request.form
    if req['state'] not in STATES:
        abort(422)
    try:
        artist = Artist.query.get(artist_id)
        artist.name = req['name']
        artist.city = req['city']
        artist.state = req['state']
        artist.phone = req['phone']
        artist.genres = req['genres']
        artist.facebook_link = req['facebook_link']
        artist.image_link = 'https://via.placeholder.com/335x500.png'
        db.session.commit()
        flash('Artist ' + req['name'] + ' was successfully changed!')
    except Exception:
        flash('An error occurred. Artist ' + req['name'] + ' could not be changed.')
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    specificVenue = Venue.query.get(venue_id)

    venue = {
      "id": venue_id,
      "name": specificVenue.name,
      "genres": specificVenue.genres,
      "address": specificVenue.address,
      "city": specificVenue.city,
      "state": specificVenue.state,
      "phone": specificVenue.phone,
      "website": "https://www.themusicalhop.com",
      "facebook_link": specificVenue.facebook_link,
      "seeking_talent": True,
      "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
      "image_link": specificVenue.image_link
    }
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    req = request.form

    if req['state'] not in STATES:
        abort(422)
        
    try:
        venue = Venue.query.get(venue_id)
        venue.name = req['name']
        venue.city = req['city']
        venue.state = req['state']
        venue.address = req['address']
        venue.phone = req['phone']
        venue.genres = req['genres']
        venue.facebook_link = req['facebook_link']
        venue.image_link = 'https://via.placeholder.com/335x500.png'
        db.session.commit()
        flash('Venue ' + req['name'] + ' was successfully changed!')
    except Exception:
        flash('An error occurred. Venue ' + req['name'] + ' could not be changed.')
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    req = request.form
    if req['state'] not in STATES:
        abort(422)
    try:
        artist = Artist(name=req['name'],
                    city=req['city'],
                    state=req['state'],
                    phone=req['phone'],
                    genres=req['genres'],
                    facebook_link=req['facebook_link'],
                    image_link='https://via.placeholder.com/335x500.png')
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + req['name'] + ' was successfully listed!')
    except Exception:
        flash('An error occurred. Artist ' + req['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    data = []
    for show in Show.query.all():
        artist = Artist.query.get(show.artist_id)
        venue = Artist.query.get(show.venue_id)
        data.append({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    req = request.form
    try:
        show = Show(venue_id=req['venue_id'],
                    artist_id=req['artist_id'],
                    start_time=req['start_time']
                    )
        db.session.add(show)
        db.session.commit()
        flash('Show Successfully Added')
    except Exception:
        flash('An error occurred. Show could not be created')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
