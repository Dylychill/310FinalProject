# Dylan McKone
# HCDE 310 Final Project
# Date: 12/16/20
# Utilizing a base HTML template, this file sets the routes that allow users to input some form data
# that is used to make an API call to DnD5e API (Dungeons and Dragons 5th Edition) and get some information about various DND elements.
# Based on these elements, users can get song recommendations (Spotify API) and chose to save some of the queried data.


from flask import Flask, render_template, request, session
import urllib.parse, urllib.request, urllib.error, json
import os
import logging
import base64
import random
from secrets import CLIENT_ID, CLIENT_SECRET # authorization for Spotify API defined in another secret file
# the above secrets file will be ignored by git

app = Flask(__name__)
app.secret_key = os.urandom(24) # for session storage

# API URLS
basedndurl = "https://www.dnd5eapi.co/api/" # dnd api
base_spotsearch_url = "https://api.spotify.com/v1/search" # base url for the Spotify search endpoint

# Base webpage, checks for session data to fill in save. On load
@app.route("/")
def main_handler():
    spotifyAuth() # getting authorization for spotify api
    sessdata = getSessionSaveData()
    return render_template("template.html", saved=sessdata)

# user wants to get song reccomendations based on a dnd element
@app.route("/musicresp", methods=['POST'])
def getMusic():
    # getting music
    app.logger.info("In Music endpoint")
    all_saved = getSessionSaveData()
    sessdata = session.get("music")
    if sessdata is not None:
        music = json.loads(sessdata)
    else:
        music = []
    song = music[int(request.form.get("savesong"))] # the unique id of the song
    name = str(song["song-name"]) + " by "
    for artist in song["artist-names"]:
        name = name + artist
    link = song["link"]

    current = {"name":name, "type":"SONG", "link": link}
    all_saved.append(current)
    data = json.dumps(all_saved)
    session["save-data"] = data
    return render_template("template.html", saved=all_saved)

# Handles most of the DND search functionality - searching for a new query (GET) and saving dnd elements (POST)
@app.route("/response", methods=['GET', 'POST'])
def search_handler():
    # check if user already has save elements
    all_saved = getSessionSaveData()
    currentType = session.get("current-type") # whatever the element type is, save it here for later use
    # don't check for existence of above session type because you can't interact with that data unless the GET is made first, so it will exist
    if request.method == 'GET':
        searchEl = request.args.get("searchEl") # gets value of this textbox

        # remove trailing and leading spaces from index
        searchEl = searchEl.strip() # if the input is only spaces, wont request from API
        if searchEl: # form filled out with something
            # make a request for the element  with this variable, then fill in template with returned info
            typeEl = request.args.get("typeOf") # which radio button selected
            currentType = typeEl # to save this globally for use in the post request
            session["current-type"] = typeEl #save to session data for use in saving elements
            resp = getDNDInfo(typeEl, searchEl) # from API
            if resp:
                return render_template("template.html", searched_info=resp, saved=all_saved, typeEl=typeEl)
            else: # no info for that element returned by API
                return render_template("template.html", no_searched=True, saved=all_saved)
        else:
            return render_template("template.html", no_searched=True, saved=all_saved)
    elif request.method == "POST":
        el = request.form.get("save-or-song") # will be the name of the element
        typeEl = request.form.get("save-options")
        if el:
            if typeEl == "save":
                current = {"name":el, "type":currentType.upper()}
                all_saved.append(current)
                data = json.dumps(all_saved)
                session["save-data"] = data
                return render_template("template.html", saved=all_saved)
            elif typeEl == "song":
                # hit up Spotify for a song based on this element
                songs = getSongs(el)
                if songs:
                    return render_template("template.html", saved=all_saved, music=songs)
                else:
                    return render_template("template.html", saved=all_saved)


# --------Helper Functions below, not routes ----------------


# given the index (unique identifier) for some typeOf dnd element (spells, monsters, etc),
# will return information about that element by accessing the dnd API
# Example url: https://www.dnd5eapi.co/api/spells/acid-arrow/
def getDNDInfo(typeOf, index):
    # if the index is the word 'random' then get a random element of this type and get info on that
    if index == 'random':
        randInd = getRandomElement(typeOf)
        if randInd is not None:
            index = randInd
    fullurl = basedndurl + typeOf + "/" + index
    fetched = safeFetch(fullurl)
    if fetched is not None:
        return json.loads(fetched.read())
    else: # didn't exist in the API
        return None

# Gets the resource list of a given type from D&D API and returns the index (id/name) of a random element available in the API
def getRandomElement(typeOf):
    resourcesURL = basedndurl + typeOf + "/" # returns JSON of all available elements
    fetched = safeFetch(resourcesURL)
    if fetched is not None:
        allEl = json.loads(fetched.read())
        randIndex = random.randint(0, allEl["count"])
        return allEl["results"][randIndex]["index"]
    else: # didn't exist in the API
        return None

# Spotify Details - only accessing public content, Client Credentials
# Get client credentials access token from Spotify API
# This access can be used for the search endpoint
# Following method taken from UW HCDE 310 and edited
# return None on error
def spotifyAuth():
    """Get authorization to Spotify API"""
    # Documentation: https://developer.spotify.com/web-api/authorization-guide/#client_credentials_flow
    # the Authorization in the *header*, as a Base 64-encoded
    # string that contains the client ID and client secret key.
    # The field must have the format:
    # Authorization: Basic <base64 encoded client_id:client_secret>
    # To get a bearer token to work as a "client," it also needs:
    # grant_type = "client_credentials" as a parameter
    try:
        # build the header
        authorization =  base64.standard_b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode())
        headers = {"Authorization":"Basic " + authorization.decode()}
        # encode the params dictionary, note it needs to be byte encoded
        params = {"grant_type" : "client_credentials"}
        encodedparams = urllib.parse.urlencode(params).encode()
        # request goes to POST https://accounts.spotify.com/api/token
        request = urllib.request.Request(
            'https://accounts.spotify.com/api/token',
                data=encodedparams, headers=headers)
        resp = safeFetch(request)
        respdata = json.load(resp)
        accessToken = respdata['access_token'] # expires after ~60 minutes
        session["spotify-access"] = accessToken
        return accessToken
    except urllib.error.URLError as e:
        print('Error trying to retrieve data: ', e)
        if hasattr(e, "code"):
            print("Error Code: ", e.code)
        elif hasattr(e, "reason"):
            print("Failed to reach the server, Reason: ", e.reason)
        return None

# Defining a query - the name of the element input by the user will be the query used for spotify
# Get Spotify Catalog information that match a keyword string - condenses content in a simplified version
def getSongs(query):
    # Search endpoint documentation - https://developer.spotify.com/documentation/web-api/reference/search/search/
    try:
        cleaned_query = cleanQuery(query)
        urlwithparams = base_spotsearch_url + "?q=" + cleaned_query + "&limit=5&type=track"
        headers = {'Authorization': 'Bearer ' + session["spotify-access"]}
        fullurl = urllib.request.Request(url = urlwithparams, headers = headers)
        fetched = safeFetch(fullurl)
        if fetched is not None:
            resp = json.loads(fetched.read())
            music = []
            songInfo = {}
            uniqueID = 0
            for song in resp["tracks"]["items"]:
                songInfo["song-name"] = song["name"]
                songInfo["link"] = song["external_urls"]["spotify"]
                songInfo["album-name"] = song["album"]["name"]
                artists = []
                for artist in song["album"]["artists"]:
                    artists.append(artist["name"])
                songInfo["artist-names"] = artists
                songInfo["unique-id"] = uniqueID
                uniqueID = uniqueID + 1
                music.append(songInfo)
                songInfo = {}
            session['music'] = json.dumps(music)
            return music
        else:
            return None
    except:
        return None

# Looks in the user's session data to get any elements that have been saved previously, and returns that as an array
def getSessionSaveData():
    sessdata = session.get("save-data")
    if sessdata is not None:
        all_saved = json.loads(sessdata)
    else:
        all_saved = [] # each element in this list will be JSON object per element (spell/monster/etc)
    return all_saved

# cleans up search terms in form that Spotify Search API will accept, changing space values
def cleanQuery(raw):
    # Encode spaces with the hex code %20
    return raw.replace(" ", "%20")


# make json a bit more readable, does not alter content
def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

# Helper method to safely make requests from nonlocal servers.
# Prints errors when they occur, returns the open url when safe
# when calling this, check for returning none to note errors
def safeFetch(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.URLError as e:
        print('Error trying to retrieve data: ', e)
        if hasattr(e, "code"):
            print("Error Code: ", e.code)
        elif hasattr(e, "reason"):
            print("Failed to reach the server, Reason: ", e.reason)
        return None

# run it on localhost
if __name__ == "__main__": # if running this file directly
    app.run(host="localhost", port=8080, debug=True) # debug just makes the error messages verbose
