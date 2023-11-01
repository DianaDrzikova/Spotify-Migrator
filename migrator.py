"""Get tracks from Spotify playlist and import them to another playlist"""

import csv
import os
import re
import spotipy.util as util
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
import time
from tqdm import tqdm
import torch

# insert from spotify for developers
CLIENT_ID = "" 

# insert from spotify for developers
CLIENT_SECRET = ""

# change to your username
USERNAME = ""

# change destination link of a playlist (public)
PLAYLISTTOINSERT = "" 

# change source link of a playlist (public)
PLAYLIST_LINK = ""

def GetSession():
    """ authentize for spotify

    Raises:
        ValueError: error if url for playlist is in wrong format

    Returns:
        session: authentized session for spotify
        playlisturi: url of playlist which tracks will be downloaded
    """
    scope = 'playlist-modify-public'
    username = USERNAME
    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET
    token = util.prompt_for_user_token(username,scope,client_id=client_id,client_secret=client_secret,redirect_uri='http://localhost/') #Follow Directions in Console
    session = spotipy.Spotify(auth=token)

    # get uri from https link
    if match := re.match(r"https://open.spotify.com/playlist/\S+.*", PLAYLIST_LINK):
        print(match.group())
        playlist_uri = match.group()
    else:
        raise ValueError("Expected format: https://open.spotify.com/playlist/...")

    return session, playlist_uri

def GetPlaylistTracks(playlist_id):
    """ get all tracks from playlist

    Args:
        playlist_id (str): id of playlist which tracks are exctracted from

    Returns:
        tracks (list): metadata of tracks
    """
    results = session.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = session.next(results)
        tracks.extend(results['items'])
    return tracks

def GetTracksID(tracks):
    """ parsing id from tracks metadata

    Args:
        tracks (list): array of tracks metadata

    Returns:
        id (array): ids of tracks
    """
    id = []
    for track in tracks:
        idSong = track["track"]["id"]
        id.append(idSong)
    return id

def GetPlaylistID(username, playlist_name):
    """ get playlist for insertion id

    Args:
        username (str): username of spotify user
        playlist_name (str): name of playlist

    Returns:
        playlist_id (str): id of playlist
    """
    playlist_id = ''
    playlists = session.user_playlists(username)
    for playlist in playlists['items']:  
        if playlist['name'] == playlist_name:  
            playlist_id = playlist['id']
    return playlist_id

def InsertToPlaylist(id, playlist_id):
    """ inserting to playlist

    Args:
        id (list): ids of tracks
        playlist_id (str): _description_
    """

    with torch.no_grad(), tqdm(total=len(id), leave=False, unit='clip') as pbar:
        for track in id:
            session.user_playlist_add_tracks(USERNAME, playlist_id, [track])
            time.sleep(0.5)
            pbar.set_postfix(track=[track])
            pbar.update()

session, playlist_uri = GetSession()
tracks = GetPlaylistTracks(playlist_uri)
playlist_id = GetPlaylistID(USERNAME, PLAYLISTTOINSERT)
id = GetTracksID(tracks)

InsertToPlaylist(id, playlist_id)



