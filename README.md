# Final Project: My Application
This writeup is for the UW HCDE 310 Final Project, describing primarily `main.py`. The program utilizes 2 APIS, DND 5e API and the Spotify API.

## API Info
### DND 5E
[Link](https://www.dnd5eapi.co/api/)

A simple REST API that has a lot of information related to Dungeons and Dragons, speficially 5th edition. There's information about spells, monsters, magical items, etc. Predominantly returns with JSON. No authorization is required to access this API.

### Spotify API
[Link](https://developer.spotify.com/documentation/web-api/quick-start/)

REST API allowing for direct interaction with a user’s Spotify account or browsing Spotify’s music libraries. The [search](https://developer.spotify.com/documentation/web-api/reference/search/search/) endpoint returns songs based on a search query, providing Spotify Catalog information on the song, artist, and album. Primarily JSON response. Each request needs to include an access token. This app only needs application authorization (Client Credentials) since this app does not access user information. [Authorization](https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow) requires creating a Spotify developer account and getting client credentials. This means providing the API `/api/token` endpoint with your applications Client ID and Secret Key to get an access token.
Line 120 of file `main.py` is the start of the function `spotifyAuth()` that gets authorization from the API.

## What this program does
Incorporating music into D&D enhances the overall experience of gameplay. Music can make any tense situation into a life-or-death decision, can offer insight into an NPCs motives, and set the mood alongside a DM’s (Dungeon Master) exposition. This project will take the form of an interactive webpage where users can pull up information on various D&D elements (in 5th Edition) and get song recommendations that line up with these elements. Users can request information about various spells and monsters found within 5th Edition and from that gathered information create a search query to find relevant music.
Users can then chose to save that element or song, and the informaion is stored in session storage to persist on next rendering of the page.

I made a video describing this website and the value it adds to give an overview of the program's motivation. It can be found on [YouTube](https://youtu.be/skHraFwad04).

## @app.route("/response", methods=['GET', 'POST'])
Adds user information and interaction. This one endpoint is called with both GET and POST methods but perfroms different tasks depending on which. On all occasions, it first searches for any past user information in session and updates the "saved" box.
### GET:
- Makes sure user passed in a param and sends that element name to the API to get info on that element. On success adds some details like element's name, damage type (if applicable), and level.
- Some example spell indexes are "bane", "alarm", and "acid-arrow" and example monsters are 'aboleth', 'bugbear', and 'dretch'.
- Gives user a button that will save that element (POST /response) or find a song based on the element (POST /response)
### POST:
- Performs one of two tasks based on a radio button selected by user: save the element or find a song
- Saving:
    - The name of the element and the type (spell/monster) is put in the "save" box and stored in session storage.
- Getting a Song:
    - Queries the Spotify search endpoint to get songs based on that element and presents top 5 songs returned to the user, where they can then chose to save a song.


## @app.route("/")
Primarily landing page for the website that returns a blank, standard page from the template. It looks into session storage for any past user saved data and updates the "save" box with that information.

## @app.route("/musicresp")
Post endpoint called when a user wants to save a song to the "saved" box. Updates session storage and sets the type of "SONG."

## static/dnd.css
All the styles are in this static stylesheet.

## templates/template.html
All template html files will be saved in this folder. As of now there is only one which serves as the base for this project.