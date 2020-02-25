# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 15:48:58 2019

@author: Xiang Guo
"""

import pylast
import time
import datetime

import os
import pandas as pd
from tqdm import tqdm
import spotipy
import spotipy.util as util

from PyLyrics import *
import lyricsgenius
import re

import urllib
from bs4 import BeautifulSoup
import requests


os.chdir('C:/Users/Xiang Guo/Desktop/lastfm_data')

#df = pd.read_csv('aria464/2019-08-11 00-00-00 - 2019-08-12 00-00-00.csv')

genius = lyricsgenius.Genius("2R3_Bm2Lom75aMNCGSeizVrqUJHC4C7ySMb0suSvQLKJxFCVv-EBbfyNoL_p3LWg")

# You have to have your own unique two values for API_KEY and API_SECRET
# Obtain yours from https://www.last.fm/api/account/create for Last.fm
API_KEY = "cfdf2a95ec6a1ef4a882edeb7babc7c0"  # this is a sample key
API_SECRET = "9e7893b6b3eec44557f36e5fd3e8e830"

# In order to perform a write operation you need to authenticate yourself
username = "Gusiev"
password_hash = pylast.md5("iWSJ:.v8YmJBcyM")

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                               username=username, password_hash=password_hash)



username2 = 'y0ffmc3dhkom7n4117ctzqf1m'
scope = 'user-top-read user-read-recently-played user-library-read \
user-read-birthdate user-read-private user-read-playback-state user-read-currently-playing'


token2 = util.prompt_for_user_token(username2,scope,client_id='4d997c7f0b714987b8a9b674e512aa49',\
   client_secret='85bf3491c2a14266b8c37d4f826fbadc',redirect_uri='http://www.google.com/')
sp = spotipy.Spotify(auth = token2)



search_url = 'https://mojim.com/song_name.html?t3'
lrc_url = 'https://mojim.com/twthxsong_idx1.htm'


    
def get_song_id(song_name, artist):
    artist = str(artist)
    song_name = str(song_name)
    req = requests.get(search_url.replace('song_name', song_name))
    data = req.text

    soup = BeautifulSoup(data, 'lxml')
    spans = soup.findAll('span', {
        'class': 'mxsh_ss4'
    })
    patt = re.compile(r"(.*?) " + artist)
    for sp in spans:
        a = sp.find('a', {
            'title': patt
        })
        if a != None:
            return a.attrs['href'].replace('/twy', '').replace('.htm', '')
    return None

def get_song_lrc(song_id):
    req = requests.get(lrc_url.replace('song_id', song_id))
    data = req.text
    soup = BeautifulSoup(data, "html.parser")
    patt = re.compile(r"var swfmm = \"(.*?)\";")
    scrp = soup.find("script", text=patt)
    lrc = patt.search(scrp.text).group(1).replace("_", "%")
    dec = urllib.parse.unquote(lrc)
    return dec



def search_lyrics(artist,song_name):
    artist = str(artist)
    song_name = str(song_name)
    if re.search(r'[\u4e00-\u9fff]+', song_name) and re.search(r'[\u4e00-\u9fff]+', artist):
        song_name = song_name.replace('-', ' ')
        song_id = get_song_id(song_name,str(artist))            
        if song_id != None:
            lrc = get_song_lrc(song_id)
            return re.sub("\n", " ", lrc)
        else:
            return None
    else:
        try:
            pylyrics = PyLyrics.getLyrics(artist,song_name)
            return re.sub("\n", " ", pylyrics)
        except:
            try:
                song = genius.search_song(song_name, artist = artist)
                if song != None:
                    genius_lyrics = re.sub("\n", " ", song.lyrics)
                    genius_lyrics = re.sub("[\[].*?[\]]", "", genius_lyrics)
                    return genius_lyrics
                else:
                    return None
            except:
                return None
            
'''
            else:
                ###for Chinese lyrics#####
                ################# https://github.com/YumeMichi/Mojim-LRC
                song_name = song_name.replace('-', ' ')
                song_id = get_song_id(song_name,artist)            
                if song_id != None:
                    lrc = get_song_lrc(song_id)
                    return re.sub("\n", " ", lrc)
'''




def revised_name(song):
    song_name = re.sub("[\(].*?[\)]", "", song)
    song_name = song_name.split('-')[0]
    return song_name


def song_id_return(artist,song_name,sp = sp):
    artist = str(artist)
    song_name = str(song_name)    
    #q='artist:{} track:{}'.format(artist,song_name)
    q='track:{}'.format(song_name)
    try:
        search_id = sp.search(q=q)
    except:
        token2 = util.prompt_for_user_token(username2,scope,client_id='4d997c7f0b714987b8a9b674e512aa49',\
                                             client_secret='85bf3491c2a14266b8c37d4f826fbadc',redirect_uri='http://www.google.com/')
        sp = spotipy.Spotify(auth = token2)
        search_id = sp.search(q=q)
    try:    
        song_id = search_id['tracks']['items'][0]['id']
        song_duration = search_id['tracks']['items'][0]['duration_ms']
        return song_id, song_duration
    except:
        return None, None


##https://developer.spotify.com/documentation/web-api/reference/object-model/#audio-features-object
## get the features
def audio_features(song_id,sp=sp):
    if song_id == None:
        return  None, None, None, None, None, None, None, None, None, None, None, None
    else:
        try:
            features = sp.audio_features(song_id)[0]
        except:
            token2 = util.prompt_for_user_token(username2,scope,client_id='4d997c7f0b714987b8a9b674e512aa49',\
                                                 client_secret='85bf3491c2a14266b8c37d4f826fbadc',redirect_uri='http://www.google.com/')
            sp = spotipy.Spotify(auth = token2)
            features = sp.audio_features(song_id)[0]
        if features == None:
            return  None, None, None, None, None, None, None, None, None, None, None, None
        else:
            danceability = features['danceability']
            energy = features['energy']
            key = features['key']
            loudness = features['loudness']
            mode = features['mode']
            speechiness = features['speechiness']
            acousticness = features['acousticness']
            instrumentalness = features['instrumentalness']
            liveness = features['liveness']
            valence = features['valence']
            tempo = features['tempo']
            time_signature = features['time_signature']
            
            return danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, time_signature


# time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1556073032.967827))
# set the time
x = datetime.datetime.now()
year = x.year
month = x.month
day = x.day

end_time = time.mktime(time.strptime('{}/{}/{}'.format(day,month,year),  "%d/%m/%Y")) 
start_time = end_time - 3600*24*5


# for different users
usernames = ['Gx_shawn','Gusiev', 'aria464', 'arashtavakoli','luisjlr','paulbonczek',
             'sanjanamendu','etiffanies','emrobartes']


for username in usernames:
    user = network.get_user(username)
    try:
        os.mkdir(username)
    except:
        pass
    user_path = os.path.join(username)
    #recent_tracks = user.get_recent_tracks(time_from = '1564433351',time_to = '1564434568')
    recent_tracks = user.get_recent_tracks(limit = None, time_from = int(start_time),time_to = int(end_time))
    
    df = pd.DataFrame(columns = ['Album', 'Playback_date','Local_date','Timestamp', 'Track','Artist','Song','Corrected_song','Duration',\
                                 'Duration_spotify', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',\
                                 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature', 'lyrics'])
    if recent_tracks == None:
        pass
    else:
        Album = []
        Playback_date = []
        Playback_timestamp = []
        TTrack = []
        Artist = []
        Song_name = []
        Corrected_song_name = []
        Duration = []
        
        Duration_spotify = []
        
        danceability_list = []
        energy_list = []
        key_list = []
        loudness_list = []
        mode_list = []
        speechiness_list = []
        acousticness_list = []
        instrumentalness_list = []
        liveness_list = []
        valence_list = []
        tempo_list = []
        time_signature_list = []
        
        lyrics_list = []
        
        
        for track in tqdm(recent_tracks):
            album = track.album
            playback_date = track.playback_date
            playback_timestamp = track.timestamp
            Track = track.track
            artist = Track.artist
            song_name = Track.get_name()
            corrected_song_name = Track.get_correction()
            try:
                duration = Track.get_duration()
            except:
                duration = None
            
            
            Album.append(album)
            Playback_date.append(playback_date)
            Playback_timestamp.append(playback_timestamp)
            TTrack.append(Track)
            Artist.append(artist)
            Song_name.append(song_name)
            Corrected_song_name.append(corrected_song_name)
            Duration.append(duration)
            
            
            revised_song_name = revised_name(song_name)
            
            current_song_id, song_duration =  song_id_return(artist,revised_song_name)
            
            current_features = audio_features(current_song_id)
            
            Duration_spotify.append(song_duration)
            
            danceability_list.append(current_features[0])
            energy_list.append(current_features[1])
            key_list.append(current_features[2])
            loudness_list.append(current_features[3])
            mode_list.append(current_features[4])
            speechiness_list.append(current_features[5])
            acousticness_list.append(current_features[6])
            instrumentalness_list.append(current_features[7])
            liveness_list.append(current_features[8])
            valence_list.append(current_features[9])
            tempo_list.append(current_features[10])
            time_signature_list.append(current_features[11])
            
            
            lyrics_list.append(search_lyrics(artist,revised_song_name))
            
            
        df['Album'] = Album 
        df['Playback_date'] = Playback_date
        df['Local_date'] = [datetime.datetime.fromtimestamp(int(i)) for i in Playback_timestamp]
        df['Timestamp'] = Playback_timestamp
        df['Track'] = TTrack
        df['Artist'] = Artist 
        df['Song'] = Song_name 
        df['Corrected_song'] = Corrected_song_name 
        df['Duration'] = Duration
        
        df['Duration_spotify'] = Duration_spotify
        
        
        df['danceability'] = danceability_list
        df['energy'] = energy_list
        df['key'] = key_list
        df['loudness'] = loudness_list
        df['mode'] = mode_list
        df['speechiness'] = speechiness_list
        df['acousticness'] = acousticness_list
        df['instrumentalness'] = instrumentalness_list
        df['liveness'] = liveness_list
        df['valence'] = valence_list
        df['tempo'] = tempo_list
        df['time_signature'] = time_signature_list
        
        df['lyrics'] = lyrics_list

    
    df2 = df.iloc[::-1]   
    
    filename = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(start_time)) + ' - ' + time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(end_time)) + '.csv'

    df2.to_csv(user_path + '/' + filename, index = False, encoding='utf_8_sig')




