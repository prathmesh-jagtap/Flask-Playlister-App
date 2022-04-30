# main file : Which is the controller  of our model

from flask import Flask, render_template, redirect, request, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["TESTING"] = True
app.config["SECRET_KEY"] = 'ed93a0fd1f3fca263d3c915fa9bc4ccc28c4c30b0e814a3e01972fcad1f09a51'

URI = "mongodb+srv://M001DB:M001DB@sandbox.uwba1.mongodb.net/Playlister?retryWrites=False"
# host = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/Playlister")
# Creating object for mongodb connection
client = MongoClient(URI)
# this will create database in mongodb
db = client.Playlister
# This creates playlists collection in our database
playlists = db.playlists
# comments collection
comments = db.comments


# this is our Root Route - '/'
@app.route('/')
def playlists_index():
    """Shoe all playlists."""
    return render_template('playlists_index.html', playlists=playlists.find())


@app.route('/playlists/new')
def playlists_new():
    """Creates a new playlists"""
    return render_template('playlists_new.html', title="New Playlist")


def video_url_creator(id_lst):
    videos = ['https://youtube.com/embed/' + vid_id for vid_id in id_lst]
    return videos


@app.route('/playlists', methods=['POST'])
def playlists_submit():
    """Submit a new playlist/"""
    # taking the video IDs and make a list out of them
    video_ids = request.form.get('video_ids').split()
    # Now calling the function to create the list of Urls
    videos = video_url_creator(video_ids)
    playlist = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'videos': videos,
        'video_ids': video_ids
    }
    playlists.insert_one(playlist)
    return redirect(url_for('playlists_index'))


@app.route('/playlists/<playlist_id>')
def playlists_show(playlist_id):
    """Returning the playlist."""
    playlist = playlists.find_one({"_id": ObjectId(playlist_id)})
    # for comments
    playlist_comments = comments.find({"playlist_id": ObjectId(playlist_id)})
    return render_template('playlists_show.html', playlist=playlist, comments=playlist_comments)


@app.route('/playlists/<playlist_id>', methods=['POST'])
def playlists_update(playlist_id):
    """editing the playlist"""
    video_ids = request.form.get('video_ids').split()
    videos = video_url_creator(video_ids)
    # Create our updated playlist
    updated_playlist = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'videos': videos,
        'video_ids': video_ids
    }
    playlists.update_one(
        {'_id': ObjectId(playlist_id)},
        {'$set': updated_playlist})
    return redirect(url_for('playlists_show', playlist_id=playlist_id))


@app.route('/playlists/<playlist_id>/edit')
def playlist_edit(playlist_id):
    """Showing the edit for a playlist"""
    playlist = playlists.find_one({'_id': ObjectId(playlist_id)})
    return render_template('playlists_edit.html', playlist=playlist, title="Edit Playlist")


@app.route('/playlists/<playlist_id>/delete', methods=['POST'])
def playlists_delete(playlist_id):
    """Delete one playlist."""
    playlists.delete_one({'_id': ObjectId(playlist_id)})
    return redirect(url_for('playlists_index'))


@app.route('/playlists/comments', methods=['POST'])
def comments_new():
    """Submit a new comment"""
    comment = {
        'title': request.form.get('title'),
        'content': request.form.get('content'),
        'playlist_id': ObjectId(request.form.get("playlist_id"))
    }
    comments.insert_one(comment)
    return redirect(url_for('playlists_show', playlist_id=request.form.get('playlist_id')))


if __name__ == '__main__':
    app.run(debug=True)
